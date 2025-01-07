import logging
from datetime import datetime, UTC
import time
from typing import Dict, Any
import requests
from enum import Enum
from multiprocessing import Queue
from sqlalchemy import text
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from database.database import DatabaseConnection

# Logging Setup
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


class SymbolWorker:
    def __init__(self, symbol: str, raw_to_normalized_queue: Queue, normalized_to_feature_queue: Queue):
        """
        Initialisiert einen Worker für ein spezifisches Symbol
        """
        self.symbol = symbol
        self.raw_to_normalized_queue = raw_to_normalized_queue
        self.normalized_to_feature_queue = normalized_to_feature_queue
        self.db = DatabaseConnection()

    def send_log(self, message: str, level: LogLevel = LogLevel.INFO) -> None:
        """Sendet Logs an den Logging Service"""
        log_data = {
            "source": LogSource.SYSTEM,
            "level": level,
            "message": message,
            "component": f"worker-{self.symbol}",
            "status": "active",
            "timestamp": datetime.now(UTC).isoformat()
        }

        try:
            requests.post("http://logging:8000/log", json=log_data, timeout=5)
        except Exception as e:
            logger.error(f"Failed to send log: {e}")

    def check_db_connection(self) -> bool:
        """Prüft die Datenbankverbindung"""
        try:
            with self.db.get_session() as session:
                session.execute(text('SELECT 1'))
            return True
        except Exception as e:
            self.send_log(f"Database connection error: {e}", LogLevel.ERROR)
            return False

    def wait_for_database(self, max_attempts: int = 30, delay: int = 10) -> bool:
        """Wartet auf verfügbare Datenbankverbindung"""
        attempt = 0
        while attempt < max_attempts:
            if self.check_db_connection():
                return True
            attempt += 1
            time.sleep(delay)
        return False

    def process_symbol(self) -> None:
        """
        Hauptmethode zur Verarbeitung eines Symbols
        Koordiniert die Kommunikation zwischen den Layern
        """
        try:
            if not self.wait_for_database():
                raise Exception("Could not establish database connection")

            self.send_log(f"Starting processing for symbol {self.symbol}")

            # Endlosschleife für kontinuierliche Verarbeitung
            while True:
                try:
                    # Verarbeite Raw Layer Events
                    raw_event = self.raw_to_normalized_queue.get()

                    if raw_event.get('symbol') != self.symbol:
                        self.send_log(
                            f"Received event for wrong symbol. Expected {self.symbol}, got {raw_event.get('symbol')}",
                            LogLevel.WARNING
                        )
                        continue

                    self.send_log(f"Processing raw event for {self.symbol}")

                    # Normalized Layer Event
                    normalized_event = self.normalized_to_feature_queue.get()

                    if normalized_event.get('symbol') != self.symbol:
                        self.send_log(
                            f"Received normalized event for wrong symbol. Expected {self.symbol}, got {normalized_event.get('symbol')}",
                            LogLevel.WARNING
                        )
                        continue

                    self.send_log(f"Processing normalized event for {self.symbol}")

                    # Kurze Pause zwischen Verarbeitungen
                    time.sleep(1)

                except Exception as e:
                    error_msg = f"Error processing {self.symbol}: {str(e)}"
                    logger.error(error_msg)
                    self.send_log(error_msg, LogLevel.ERROR)
                    time.sleep(5)  # Pause vor erneutem Versuch

        except Exception as e:
            error_msg = f"Fatal error in worker for {self.symbol}: {str(e)}"
            logger.error(error_msg)
            self.send_log(error_msg, LogLevel.ERROR)
            raise

    @staticmethod
    def create_and_start(symbol: str, raw_to_normalized_queue: Queue, normalized_to_feature_queue: Queue) -> None:
        """
        Factory-Methode zum Erstellen und Starten eines Workers
        """
        worker = SymbolWorker(symbol, raw_to_normalized_queue, normalized_to_feature_queue)
        worker.process_symbol()


def main(symbol: str, raw_to_normalized_queue: Queue, normalized_to_feature_queue: Queue):
    """
    Hauptfunktion zum Starten eines Symbol-Workers
    """
    try:
        SymbolWorker.create_and_start(symbol, raw_to_normalized_queue, normalized_to_feature_queue)
    except KeyboardInterrupt:
        logger.info(f"Received keyboard interrupt for {symbol}, shutting down...")
    except Exception as e:
        logger.error(f"Error in worker for {symbol}: {str(e)}")
        raise


if __name__ == "__main__":
    # Dieser Block wird normalerweise nicht ausgeführt, da Worker über manager.py gestartet werden
    pass