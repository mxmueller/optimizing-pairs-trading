import yaml
import requests
import logging
import time
from datetime import datetime, UTC
from typing import Dict, Any
from enum import Enum
import sys
from pathlib import Path
from multiprocessing import Queue
from sqlalchemy import text

sys.path.append(str(Path(__file__).parent.parent.parent))
from database.database import DatabaseConnection
from layer.normalized.normalizers import MarketDataNormalizer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class LogSource(str, Enum):
    SYSTEM = "system"


class NormalizedDataProcessor:
    def __init__(self, input_queue: Queue, output_queue: Queue, symbol: str) -> None:
        """
        Initialisiert den Processor für ein spezifisches Symbol
        """
        self.symbol = symbol
        self.db = DatabaseConnection()
        self.config = self._load_config()
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.normalizer = MarketDataNormalizer()

    def _load_config(self) -> Dict[str, Any]:
        try:
            with open('/app/config/symbols.yaml', 'r') as file:
                config = yaml.safe_load(file)

            # Validiere Symbol in Konfiguration
            if not any(s['pair'] == self.symbol for s in config['symbols']):
                raise ValueError(f"Symbol {self.symbol} not found in configuration")

            return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise

    def send_log(self, message: str, level: LogLevel = LogLevel.INFO) -> None:
        log_data = {
            "source": LogSource.SYSTEM,
            "level": level,
            "message": message,
            "component": f"normalized-processor-{self.symbol}",
            "action": "normalized_layer",
            "status": "active",
            "timestamp": datetime.now(UTC).isoformat()
        }

        try:
            requests.post("http://logging:8000/log", json=log_data, timeout=5)
        except Exception as e:
            logger.error(f"Failed to send log: {e}")

    def publish_feature_event(self, start_date: str, end_date: str, record_count: int) -> None:
        """Publiziert Update-Events an die Feature Layer Queue"""
        try:
            feature_event = {
                "event_type": "normalized_update",
                "symbol": self.symbol,
                "start_date": start_date,
                "end_date": end_date,
                "record_count": record_count,
                "timestamp": datetime.now(UTC).isoformat()
            }
            self.output_queue.put(feature_event)
            self.send_log(
                f"Published feature event: {record_count} records",
                LogLevel.INFO
            )
        except Exception as e:
            self.send_log(
                f"Failed to publish feature event: {e}",
                LogLevel.ERROR
            )
            logger.error(f"Failed to publish feature event: {e}")

    def normalize_data(self, start_date: str, end_date: str) -> None:
        try:
            # Kleine Verzögerung um Race Conditions zu vermeiden
            time.sleep(1)

            with self.db.get_session() as session:
                # Prüfe zuerst ob Daten da sind
                check_query = text("""
                    SELECT COUNT(*) 
                    FROM raw_market_data 
                    WHERE symbol = :symbol
                    AND date BETWEEN :start_date AND :end_date
                """)

                count = session.execute(
                    check_query,
                    {"symbol": self.symbol, "start_date": start_date, "end_date": end_date}
                ).scalar()

                if count == 0:
                    self.send_log(
                        f"No raw data found. Retrying in 2 seconds...",
                        LogLevel.WARNING
                    )
                    time.sleep(2)
                    count = session.execute(
                        check_query,
                        {"symbol": self.symbol, "start_date": start_date, "end_date": end_date}
                    ).scalar()
                    if count == 0:
                        raise ValueError(f"No data found after retry")

                # Hole die Rohdaten
                query = text("""
                    SELECT 
                        date,
                        symbol,
                        open as raw_open,
                        high as raw_high,
                        low as raw_low,
                        close as raw_close,
                        volume as raw_volume
                    FROM raw_market_data
                    WHERE symbol = :symbol
                    AND date BETWEEN :start_date AND :end_date
                    ORDER BY date
                """)

                result = session.execute(
                    query,
                    {"symbol": self.symbol, "start_date": start_date, "end_date": end_date}
                )

                raw_data = []
                for row in result:
                    raw_data.append({
                        'date': row.date,
                        'symbol': row.symbol,
                        'raw_open': float(row.raw_open),
                        'raw_high': float(row.raw_high),
                        'raw_low': float(row.raw_low),
                        'raw_close': float(row.raw_close),
                        'raw_volume': float(row.raw_volume)
                    })

                if not raw_data:
                    self.send_log(
                        "No raw data found",
                        LogLevel.WARNING
                    )
                    return

                normalized_data = self.normalizer.normalize_batch(
                    raw_data,
                    calculate_returns=True,
                    calculate_volume=True,
                    calculate_price=True,
                    calculate_turbulence=True,
                    volume_window=20,
                    price_window=20,
                    turbulence_window=60
                )

                # Insert normalisierte Daten
                insert_stmt = text("""
                    INSERT INTO normalized_market_data (
                        date, symbol, raw_open, raw_high, raw_low, raw_close, raw_volume,
                        returns, log_returns, volume_minmax, log_volume, zscore_volume,
                        zscore_price, rolling_mean_return, rolling_std_return, 
                        turbulence_index, rel_turbulence
                    ) VALUES (
                        :date, :symbol, :raw_open, :raw_high, :raw_low, :raw_close, :raw_volume,
                        :returns, :log_returns, :volume_minmax, :log_volume, :zscore_volume,
                        :zscore_price, :rolling_mean_return, :rolling_std_return,
                        :turbulence_index, :rel_turbulence
                    )
                    ON CONFLICT (date, symbol) DO UPDATE SET
                        raw_open = EXCLUDED.raw_open,
                        raw_high = EXCLUDED.raw_high,
                        raw_low = EXCLUDED.raw_low,
                        raw_close = EXCLUDED.raw_close,
                        raw_volume = EXCLUDED.raw_volume,
                        returns = EXCLUDED.returns,
                        log_returns = EXCLUDED.log_returns,
                        volume_minmax = EXCLUDED.volume_minmax,
                        log_volume = EXCLUDED.log_volume,
                        zscore_volume = EXCLUDED.zscore_volume,
                        zscore_price = EXCLUDED.zscore_price,
                        rolling_mean_return = EXCLUDED.rolling_mean_return,
                        rolling_std_return = EXCLUDED.rolling_std_return,
                        turbulence_index = EXCLUDED.turbulence_index,
                        rel_turbulence = EXCLUDED.rel_turbulence,
                        last_updated = CURRENT_TIMESTAMP
                """)

                for record in normalized_data:
                    session.execute(insert_stmt, record)

                session.commit()

                # Nach erfolgreicher Normalisierung, Feature Event publizieren
                self.publish_feature_event(
                    start_date=start_date,
                    end_date=end_date,
                    record_count=len(normalized_data)
                )

                log_message = "Successfully normalized data"
                logger.info(log_message)
                self.send_log(log_message, LogLevel.INFO)

        except Exception as e:
            error_msg = f"Error normalizing data: {str(e)}"
            logger.error(error_msg)
            self.send_log(error_msg, LogLevel.ERROR)
            raise

    def process_raw_event(self, event: Dict[str, Any]) -> None:
        try:
            # Validiere Event Symbol
            if event['symbol'] != self.symbol:
                self.send_log(
                    f"Received event for wrong symbol: {event['symbol']}",
                    LogLevel.WARNING
                )
                return

            logger.info("Processing event")
            self.send_log(
                f"Received raw event from {event['start_date']} to {event['end_date']} with {event['record_count']} records"
            )

            if event['record_count'] > 0:
                self.normalize_data(
                    event['start_date'],
                    event['end_date']
                )
                self.send_log(
                    f"Completed normalization from {event['start_date']} to {event['end_date']}"
                )

        except Exception as e:
            error_msg = f"Error processing raw event: {str(e)}"
            logger.error(error_msg)
            self.send_log(error_msg, LogLevel.ERROR)


def wait_for_database(max_attempts: int = 30, delay: int = 10) -> None:
    """Wartet auf verfügbare Datenbankverbindung"""
    attempt = 0
    while attempt < max_attempts:
        try:
            with DatabaseConnection().get_session() as session:
                session.execute(text('SELECT 1'))
                logger.info("Successfully connected to database")
                return
        except Exception as e:
            attempt += 1
            if attempt < max_attempts:
                logger.warning(f"Database connection attempt {attempt}/{max_attempts} failed: {e}")
                logger.info(f"Waiting {delay} seconds before next attempt...")
                time.sleep(delay)
            else:
                logger.error(f"Failed to connect to database after {max_attempts} attempts")
                raise


def main(input_queue: Queue, output_queue: Queue, symbol: str) -> None:
    """
    Hauptfunktion für die Symbol-spezifische Normalisierung
    """
    wait_for_database()
    processor = NormalizedDataProcessor(input_queue, output_queue, symbol)
    processor.send_log("Starting normalized layer processor")
    logger.info(f"Normalized layer processor started for {symbol}")

    while True:
        try:
            event = input_queue.get()
            processor.process_raw_event(event)
        except Exception as e:
            error_msg = f"Main loop error: {str(e)}"
            logger.error(error_msg)
            processor.send_log(error_msg, LogLevel.ERROR)
            time.sleep(5)


if __name__ == "__main__":
    # Dieser Block wird normalerweise nicht direkt ausgeführt
    pass