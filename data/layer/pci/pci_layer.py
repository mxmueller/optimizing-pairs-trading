import yaml
import requests
import logging
from datetime import datetime, UTC
from typing import Dict, Any
from enum import Enum
from multiprocessing import Queue
from sqlalchemy import text
from database.database import DatabaseConnection
from layer.pci.pci_processor import PCIProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LogLevel(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

class PCILayerProcessor:
    def __init__(self, input_queue: Queue, output_queue: Queue, symbol_pair: str):
        self.symbol_pair = symbol_pair
        self.symbol1, self.symbol2 = symbol_pair.split('_')
        self.db = DatabaseConnection()
        self.config = self._load_config()
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.pci_processor = PCIProcessor()
        self.event_buffer = {self.symbol1: None, self.symbol2: None}
        self.processed_ranges = set()

    def _load_config(self) -> Dict[str, Any]:
        with open('/app/config/settings.yaml', 'r') as file:
            config = yaml.safe_load(file)
            pair_config = next((pair for pair in config['pci_pairs']
                             if f"{pair['primary']}_{pair['secondary']}" == self.symbol_pair), None)
            if not pair_config or not pair_config.get('active', False):
                raise ValueError(f"Pair {self.symbol_pair} not found or not active")
            self.pci_settings = config['settings']['pci']
            return config

    def send_log(self, message: str, level: LogLevel = LogLevel.INFO):
        try:
            log_data = {
                "source": "system",
                "level": level,
                "message": message,
                "component": f"pci-processor-{self.symbol_pair}",
                "timestamp": datetime.now(UTC).isoformat()
            }
            requests.post("http://logging:8000/log", json=log_data, timeout=5)
        except Exception as e:
            logger.error(f"Failed to send log: {e}")

    def get_all_pairs(self):
        try:
            with self.db.get_session() as session:
                # Get all active pairs from config
                active_pairs = []
                for pair in self.config['pci_pairs']:
                    if pair.get('active', False):
                        primary = pair['primary']
                        secondary = pair['secondary']
                        data1 = self._get_symbol_data(session, primary)
                        data2 = self._get_symbol_data(session, secondary)
                        if data1 and data2 and len(data1) == len(data2):
                            active_pairs.append({
                                'data1': data1,
                                'data2': data2,
                                'primary': primary,
                                'secondary': secondary
                            })
                return active_pairs
        except Exception as e:
            self.send_log(f"Failed to get pairs: {e}", LogLevel.ERROR)
            return []

    def _get_symbol_data(self, session, symbol):
        try:
            query = text("""
                SELECT date, close 
                FROM raw_market_data 
                WHERE symbol = :symbol 
                ORDER BY date
            """)
            result = session.execute(query, {"symbol": symbol}).fetchall()
            return [{'date': row[0], 'close': float(row[1])} for row in result]
        except Exception as e:
            self.send_log(f"Failed to get data for {symbol}: {e}", LogLevel.ERROR)
            return None

    def validate_data_availability(self, start_date: str, end_date: str) -> bool:
        try:
            with self.db.get_session() as session:
                for symbol in [self.symbol1, self.symbol2]:
                    count = session.execute(text("""
                        SELECT COUNT(*) 
                        FROM raw_market_data 
                        WHERE symbol = :symbol 
                        AND date BETWEEN :start_date AND :end_date
                    """), {
                        "symbol": symbol,
                        "start_date": start_date,
                        "end_date": end_date
                    }).scalar()

                    if count == 0:
                        self.send_log(
                            f"No data for {symbol} between {start_date} and {end_date}",
                            LogLevel.WARNING
                        )
                        return False
                return True
        except Exception as e:
            self.send_log(f"Data validation failed: {e}", LogLevel.ERROR)
            return False

    def get_date_range(self, event1: Dict, event2: Dict) -> tuple[str, str]:
        dates = [event1['start_date'], event1['end_date'],
                event2['start_date'], event2['end_date']]
        return min(dates), max(dates)

    def process_raw_event(self, event: Dict[str, Any]) -> None:
        try:
            symbol = event.get('symbol')
            if symbol not in [self.symbol1, self.symbol2]:
                return

            logger.info(f"Received event for {symbol}: {event['start_date']} to {event['end_date']}")
            self.event_buffer[symbol] = event

            if all(self.event_buffer.values()):
                start_date, end_date = self.get_date_range(
                    self.event_buffer[self.symbol1],
                    self.event_buffer[self.symbol2]
                )

                range_key = f"{start_date}_{end_date}"
                if range_key in self.processed_ranges:
                    logger.info(f"Range {range_key} already processed")
                    return

                if not self.validate_data_availability(start_date, end_date):
                    return

                # Get all potential pairs and run selection
                all_pairs = self.get_all_pairs()
                selected_pairs = self.pci_processor.select_pairs(all_pairs)

                if not selected_pairs:
                    self.send_log("No pairs selected after filtering")
                    return

                # Process only selected pairs
                try:
                    for pair in selected_pairs:
                        if (pair['primary'] == self.symbol1 and
                            pair['secondary'] == self.symbol2):
                            self.process_pci(
                                start_date, end_date,
                                pair['data1'], pair['data2']
                            )
                    self.processed_ranges.add(range_key)
                except Exception as e:
                    self.send_log(f"PCI processing failed: {e}", LogLevel.ERROR)
                finally:
                    self.event_buffer = {self.symbol1: None, self.symbol2: None}

        except Exception as e:
            self.send_log(f"Event processing failed: {e}", LogLevel.ERROR)

    def process_pci(self, start_date: str, end_date: str, data1, data2) -> None:
        try:
            self.pci_processor.pci_settings = self.pci_settings
            pci_results = self.pci_processor.process_pair(data1, data2)

            if not pci_results:
                logger.warning("No PCI results generated")
                return

            with self.db.get_session() as session:
                session.execute(text("""
                    INSERT INTO pci_market_data (
                        date, symbol_pair, symbol1, symbol2,
                        beta, rho, sigma_m, sigma_r,
                        mt, rt, zscore, r2_mr, lr_score
                    ) VALUES (
                        :date, :symbol_pair, :symbol1, :symbol2,
                        :beta, :rho, :sigma_m, :sigma_r,
                        :mt, :rt, :zscore, :r2_mr, :lr_score
                    ) ON CONFLICT (date, symbol_pair) DO UPDATE SET
                        beta = EXCLUDED.beta,
                        rho = EXCLUDED.rho,
                        sigma_m = EXCLUDED.sigma_m,
                        sigma_r = EXCLUDED.sigma_r,
                        mt = EXCLUDED.mt,
                        rt = EXCLUDED.rt,
                        zscore = EXCLUDED.zscore,
                        r2_mr = EXCLUDED.r2_mr,
                        lr_score = EXCLUDED.lr_score
                """), pci_results)

                session.commit()
                self.send_log(
                    f"Processed {len(pci_results)} records for {self.symbol_pair}",
                    LogLevel.INFO
                )

        except Exception as e:
            self.send_log(f"PCI processing failed: {str(e)}", LogLevel.ERROR)
            raise

def main(input_queue: Queue, output_queue: Queue, symbol_pair: str):
    try:
        processor = PCILayerProcessor(input_queue, output_queue, symbol_pair)
        logger.info(f"Started PCI processor for {symbol_pair}")

        while True:
            try:
                event = input_queue.get()
                processor.process_raw_event(event)
            except Exception as e:
                logger.error(f"Main loop error: {str(e)}")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise

if __name__ == "__main__":
    pass