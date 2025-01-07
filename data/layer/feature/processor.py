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
from layer.feature.indicators import TechnicalIndicators

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


class FeatureDataProcessor:
    def __init__(self, input_queue: Queue, symbol: str) -> None:
        """
        Initialisiert den Feature Processor für ein spezifisches Symbol
        """
        self.symbol = symbol
        self.db = DatabaseConnection()
        self.config = self._load_config()
        self.input_queue = input_queue
        self.indicators = TechnicalIndicators()

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
        """Send log message to logging service"""
        log_data = {
            "source": LogSource.SYSTEM,
            "level": level,
            "message": message,
            "component": f"feature-processor-{self.symbol}",
            "status": "active",
            "timestamp": datetime.now(UTC).isoformat()
        }

        try:
            requests.post("http://logging:8000/log", json=log_data, timeout=5)
        except Exception as e:
            logger.error(f"Failed to send log: {e}")

    def process_normalized_data(self, start_date: str, end_date: str) -> None:
        """Verarbeitet die normalisierten Daten und berechnet Features"""
        try:
            time.sleep(1)  # Kleine Verzögerung um Race Conditions zu vermeiden

            with self.db.get_session() as session:
                # Hole normalisierte Daten
                query = text("""
                    SELECT *
                    FROM normalized_market_data
                    WHERE symbol = :symbol
                    AND date BETWEEN :start_date AND :end_date
                    ORDER BY date
                """)

                result = session.execute(
                    query,
                    {"symbol": self.symbol, "start_date": start_date, "end_date": end_date}
                )

                # Konvertiere in Liste von Dictionaries
                normalized_data = []
                for row in result:
                    row_dict = dict(row._mapping)
                    normalized_data.append(row_dict)

                if not normalized_data:
                    self.send_log(
                        "No normalized data found",
                        LogLevel.WARNING
                    )
                    return

                self.send_log(
                    f"Processing {len(normalized_data)} records",
                    LogLevel.INFO
                )

                # Berechne technische Indikatoren
                feature_data = self.indicators.calculate_all_indicators(
                    normalized_data,
                    calculate_macd=True,
                    calculate_rsi=True,
                    calculate_cci=True,
                    calculate_adx=True
                )

                # Speichere Feature-Daten
                for record in feature_data:
                    # Erstelle INSERT Statement
                    insert_stmt = text("""
                        INSERT INTO feature_market_data (
                            date, symbol, 
                            -- Raw und normalisierte Daten
                            raw_open, raw_high, raw_low, raw_close, raw_volume,
                            returns, log_returns, volume_minmax, log_volume, zscore_volume,
                            zscore_price, rolling_mean_return, rolling_std_return,
                            turbulence_index, rel_turbulence,
                            -- MACD
                            macd_line, macd_signal, macd_histogram,
                            -- RSI
                            rsi_14, rsi_avg_gain, rsi_avg_loss,
                            -- CCI
                            cci_20, cci_typical_price, cci_sma_tp, cci_mean_deviation,
                            -- ADX
                            adx_14, plus_di_14, minus_di_14, dx_14, tr_14
                        ) VALUES (
                            :date, :symbol,
                            -- Raw und normalisierte Daten
                            :raw_open, :raw_high, :raw_low, :raw_close, :raw_volume,
                            :returns, :log_returns, :volume_minmax, :log_volume, :zscore_volume,
                            :zscore_price, :rolling_mean_return, :rolling_std_return,
                            :turbulence_index, :rel_turbulence,
                            -- MACD
                            :macd_line, :macd_signal, :macd_histogram,
                            -- RSI
                            :rsi_14, :rsi_avg_gain, :rsi_avg_loss,
                            -- CCI
                            :cci_20, :cci_typical_price, :cci_sma_tp, :cci_mean_deviation,
                            -- ADX
                            :adx_14, :plus_di_14, :minus_di_14, :dx_14, :tr_14
                        )
                        ON CONFLICT (date, symbol) DO UPDATE SET
                            -- Raw und normalisierte Daten
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
                            -- MACD
                            macd_line = EXCLUDED.macd_line,
                            macd_signal = EXCLUDED.macd_signal,
                            macd_histogram = EXCLUDED.macd_histogram,
                            -- RSI
                            rsi_14 = EXCLUDED.rsi_14,
                            rsi_avg_gain = EXCLUDED.rsi_avg_gain,
                            rsi_avg_loss = EXCLUDED.rsi_avg_loss,
                            -- CCI
                            cci_20 = EXCLUDED.cci_20,
                            cci_typical_price = EXCLUDED.cci_typical_price,
                            cci_sma_tp = EXCLUDED.cci_sma_tp,
                            cci_mean_deviation = EXCLUDED.cci_mean_deviation,
                            -- ADX
                            adx_14 = EXCLUDED.adx_14,
                            plus_di_14 = EXCLUDED.plus_di_14,
                            minus_di_14 = EXCLUDED.minus_di_14,
                            dx_14 = EXCLUDED.dx_14,
                            tr_14 = EXCLUDED.tr_14,
                            last_updated = CURRENT_TIMESTAMP
                    """)

                    session.execute(insert_stmt, record)

                session.commit()
                success_msg = "Successfully processed and stored feature data"
                logger.info(success_msg)
                self.send_log(success_msg, LogLevel.INFO)

        except Exception as e:
            error_msg = f"Error processing data: {str(e)}"
            logger.error(error_msg)
            self.send_log(error_msg, LogLevel.ERROR)
            raise

    def process_normalized_event(self, event: Dict[str, Any]) -> None:
        """Verarbeitet eingehende Events vom Normalized Layer"""
        try:
            # Validiere Event Symbol
            if event['symbol'] != self.symbol:
                self.send_log(
                    f"Received event for wrong symbol: {event['symbol']}",
                    LogLevel.WARNING
                )
                return

            logger.info("Processing normalized event")
            self.send_log(
                f"Received normalized event from {event['start_date']} to {event['end_date']} with {event['record_count']} records"
            )

            if event['record_count'] > 0:
                self.process_normalized_data(
                    event['start_date'],
                    event['end_date']
                )
                self.send_log(
                    f"Completed feature processing from {event['start_date']} to {event['end_date']}"
                )

        except Exception as e:
            error_msg = f"Error processing normalized event: {str(e)}"
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


def main(input_queue: Queue, symbol: str) -> None:
    """
    Hauptfunktion für die Symbol-spezifische Feature-Berechnung
    """
    wait_for_database()
    processor = FeatureDataProcessor(input_queue, symbol)

    processor.send_log("Starting feature layer processor")
    logger.info(f"Feature layer processor started for {symbol}")

    while True:
        try:
            # Warte auf Events vom Normalized Layer
            event = input_queue.get()
            processor.process_normalized_event(event)

        except Exception as e:
            error_msg = f"Main loop error: {str(e)}"
            logger.error(error_msg)
            processor.send_log(error_msg, LogLevel.ERROR)
            time.sleep(5)


if __name__ == "__main__":
    pass