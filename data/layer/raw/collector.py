import yaml
import requests
import logging
import time
from datetime import datetime, UTC, timedelta, date
from typing import Dict, Any, List, Tuple, Optional
from enum import Enum
import sys
from pathlib import Path
from sqlalchemy import text
import pandas_market_calendars as mcal
from functools import wraps, lru_cache
from multiprocessing import Queue
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.append(str(Path(__file__).parent.parent.parent))
from database.database import DatabaseConnection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class LogSource(str, Enum):
    SYSTEM = "system"


def retry_on_exception(retries=3, delay=5):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < retries - 1:
                        logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay} seconds...")
                        time.sleep(delay)
            raise last_exception

        return wrapper

    return decorator


class MarketCalendar:
    def __init__(self):
        self.calendar = mcal.get_calendar('NYSE')

    @lru_cache(maxsize=1000)
    def is_trading_day(self, check_date: date) -> bool:
        schedule = self.calendar.schedule(start_date=check_date, end_date=check_date)
        return len(schedule) > 0

    def get_trading_days(self, start_date: date, end_date: date) -> List[date]:
        schedule = self.calendar.schedule(start_date=start_date, end_date=end_date)
        return [d.date() for d in schedule.index]

    @lru_cache(maxsize=1)
    def get_last_trading_day(self) -> date:
        today = datetime.now(UTC).date()
        schedule = self.calendar.schedule(
            start_date=today - timedelta(days=10),
            end_date=today
        )
        return schedule.index[-1].date() if len(schedule) > 0 else None


class RawDataCollector:
    BATCH_SIZE = 1000
    CHUNK_DAYS = 90
    MAX_WORKERS = 3

    def __init__(self, update_queue: Queue, symbol: str):
        self.symbol = symbol
        self.config = self._load_config()
        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}
        self.db = DatabaseConnection()
        self.start_date = datetime.strptime(
            self.config['settings']['historical_start_date'],
            "%Y-%m-%d"
        ).replace(tzinfo=UTC)
        self.market_calendar = MarketCalendar()
        self.update_queue = update_queue

    def _load_config(self) -> Dict[str, Any]:
        try:
            with open('/app/config/settings.yaml', 'r') as file:
                config = yaml.safe_load(file)
            self._validate_config(config)
            return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise

    def _validate_config(self, config: Dict[str, Any]) -> None:
        required_keys = ['settings', 'symbols']
        required_settings = ['historical_start_date', 'api']

        if not all(key in config for key in required_keys):
            raise ValueError(f"Missing required config keys. Required: {required_keys}")
        if not all(key in config['settings'] for key in required_settings):
            raise ValueError(f"Missing required settings. Required: {required_settings}")
        if not any(s['pair'] == self.symbol for s in config['symbols']):
            raise ValueError(f"Symbol {self.symbol} not found in configuration")

    def send_log(self, message: str, level: LogLevel = LogLevel.INFO) -> None:
        log_data = {
            "source": LogSource.SYSTEM,
            "level": level,
            "message": message,
            "component": f"raw-collector-{self.symbol}",
            "status": "active",
            "timestamp": datetime.now(UTC).isoformat()
        }
        try:
            requests.post("http://logging:8000/log", json=log_data, timeout=5)
        except Exception as e:
            logger.error(f"Failed to send log: {e}")

    def publish_update_event(self, start_date: datetime, end_date: datetime, record_count: int):
        try:
            update_event = {
                "event_type": "data_update",
                "symbol": self.symbol,
                "start_date": start_date.date().isoformat(),
                "end_date": end_date.date().isoformat(),
                "record_count": record_count,
                "timestamp": datetime.now(UTC).isoformat()
            }
            self.update_queue.put(update_event)
            self.send_log(f"Published update event: {record_count} records")
        except Exception as e:
            self.send_log(f"Failed to publish update event: {e}", LogLevel.ERROR)

    def get_missing_dates(self) -> List[date]:
        with self.db.get_session() as session:
            query = text("""
                SELECT DISTINCT date
                FROM raw_market_data
                WHERE symbol = :symbol
                ORDER BY date
            """)
            existing_dates = set(row[0] for row in session.execute(query, {"symbol": self.symbol}))
            trading_days = self.market_calendar.get_trading_days(
                start_date=self.start_date.date(),
                end_date=self.market_calendar.get_last_trading_day()
            )
            return [day for day in trading_days if day not in existing_dates]

    def create_optimal_date_ranges(self, dates: List[date]) -> List[Tuple[datetime, datetime]]:
        if not dates:
            return []

        dates = sorted(dates)
        ranges = []
        current_start = dates[0]
        prev_date = dates[0]

        for current_date in dates[1:]:
            if len(self.market_calendar.get_trading_days(current_start, current_date)) >= self.BATCH_SIZE:
                ranges.append((
                    datetime.combine(current_start, datetime.min.time(), UTC),
                    datetime.combine(prev_date, datetime.min.time(), UTC)
                ))
                current_start = current_date
            prev_date = current_date

        ranges.append((
            datetime.combine(current_start, datetime.min.time(), UTC),
            datetime.combine(prev_date, datetime.min.time(), UTC)
        ))
        return ranges

    def fetch_data_chunk(self, start_date: datetime, end_date: datetime) -> Dict:
        url = f"{self.config['settings']['api']['base_url']}/{self.symbol}"
        params = {
            **self.config['settings']['api']['params'],
            'period1': int(start_date.timestamp()),
            'period2': int((end_date + timedelta(days=1)).timestamp()),
            'interval': '1d'
        }
        response = requests.get(url, params=params, headers=self.headers, timeout=10)
        response.raise_for_status()
        return response.json()

    @retry_on_exception(retries=3, delay=5)
    def collect_and_store_data(self, start_date: datetime, end_date: datetime) -> int:
        logger.info(f"Collecting data from {start_date.date()} to {end_date.date()}")

        date_chunks = []
        current = start_date
        while current < end_date:
            chunk_end = min(current + timedelta(days=self.CHUNK_DAYS), end_date)
            date_chunks.append((current, chunk_end))
            current = chunk_end + timedelta(days=1)

        records = []
        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            future_to_chunk = {
                executor.submit(self.fetch_data_chunk, chunk_start, chunk_end): (chunk_start, chunk_end)
                for chunk_start, chunk_end in date_chunks
            }

            for future in as_completed(future_to_chunk):
                try:
                    data = future.result()
                    if not data.get('chart', {}).get('result'):
                        continue

                    result = data['chart']['result'][0]
                    timestamps = result.get('timestamp', [])
                    quotes = result.get('indicators', {}).get('quote', [{}])[0]

                    for i, ts in enumerate(timestamps):
                        dt = datetime.fromtimestamp(ts, UTC).date()
                        if not self.market_calendar.is_trading_day(dt):
                            continue

                        if all(quotes.get(field) and i < len(quotes[field]) for field in
                               ['open', 'high', 'low', 'close', 'volume']):
                            records.append({
                                "date": dt,
                                "symbol": self.symbol,
                                "open": quotes['open'][i],
                                "high": quotes['high'][i],
                                "low": quotes['low'][i],
                                "close": quotes['close'][i],
                                "volume": quotes['volume'][i]
                            })

                except Exception as e:
                    chunk_start, chunk_end = future_to_chunk[future]
                    logger.error(f"Error fetching chunk {chunk_start} to {chunk_end}: {e}")

        if records:
            with self.db.get_session() as session:
                for i in range(0, len(records), self.BATCH_SIZE):
                    batch = records[i:i + self.BATCH_SIZE]
                    session.execute(
                        text("""
                        INSERT INTO raw_market_data 
                        (date, symbol, open, high, low, close, volume)
                        VALUES (:date, :symbol, :open, :high, :low, :close, :volume)
                        ON CONFLICT (date, symbol) DO UPDATE 
                        SET open = EXCLUDED.open,
                            high = EXCLUDED.high,
                            low = EXCLUDED.low,
                            close = EXCLUDED.close,
                            volume = EXCLUDED.volume
                        """),
                        batch
                    )
                session.commit()

        total_records = len(records)
        self.publish_update_event(start_date, end_date, total_records)
        logger.info(f"Successfully stored {total_records} records")
        return total_records

    def update_symbol_data(self) -> Dict[str, Any]:
        last_trading_day = self.market_calendar.get_last_trading_day()

        with self.db.get_session() as session:
            query = text("SELECT MAX(date) FROM raw_market_data WHERE symbol = :symbol")
            last_update = session.execute(query, {"symbol": self.symbol}).scalar()

            if last_update and self.market_calendar.is_trading_day(last_update):
                if last_update >= last_trading_day:
                    status_msg = f"Data is up to date (last update: {last_update})"
                    logger.info(status_msg)
                    self.send_log(status_msg)
                    return {"symbol": self.symbol, "status": "up_to_date", "updates": 0}

        missing_dates = self.get_missing_dates()
        if missing_dates and last_update:
            today = datetime.now(UTC).date()
            missing_dates = [d for d in missing_dates if d < today or d not in [last_update]]

        if not missing_dates:
            status_msg = "No missing dates"
            logger.info(status_msg)
            self.send_log(status_msg)
            return {"symbol": self.symbol, "status": "up_to_date", "updates": 0}

        self.send_log(f"Starting update with {len(missing_dates)} missing dates")
        date_ranges = self.create_optimal_date_ranges(missing_dates)

        total_updates = 0
        for start, end in date_ranges:
            records_added = self.collect_and_store_data(start, end)
            total_updates += records_added
            time.sleep(2)

        final_status = f"Completed update: {total_updates} records in {len(date_ranges)} batches"
        logger.info(final_status)
        self.send_log(final_status)

        return {
            "symbol": self.symbol,
            "status": "updated",
            "updates": total_updates,
            "batches_processed": len(date_ranges)
        }


def wait_for_database(max_attempts=30, delay=10):
    attempt = 0
    while attempt < max_attempts:
        try:
            with DatabaseConnection().get_session() as session:
                session.execute(text('SELECT 1'))
                logger.info("Successfully connected to database")
                return True
        except Exception as e:
            attempt += 1
            if attempt < max_attempts:
                logger.warning(f"Database connection attempt {attempt}/{max_attempts} failed: {e}")
                logger.info(f"Waiting {delay} seconds before next attempt...")
                time.sleep(delay)
            else:
                logger.error(f"Failed to connect to database after {max_attempts} attempts")
                raise


def main(update_queue: Queue, symbol: str) -> None:
    wait_for_database()
    collector = RawDataCollector(update_queue, symbol)

    while True:
        try:
            collector.send_log("Starting data collection cycle")
            stats = collector.update_symbol_data()

            if stats["updates"] > 0:
                msg = f"Updated: {stats['updates']} new records in {stats['batches_processed']} batches"
                logger.info(msg)
                collector.send_log(msg)

            collector.send_log("Data collection cycle completed")
            logger.info("Waiting for next check...")
            time.sleep(3600)

        except Exception as e:
            error_msg = f"Main loop error: {str(e)}"
            logger.error(error_msg)
            collector.send_log(error_msg, LogLevel.ERROR)
            time.sleep(60)


if __name__ == "__main__":
    pass