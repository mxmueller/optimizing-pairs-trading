import yaml
import logging
import multiprocessing
from pathlib import Path
import sys
import time
from typing import List, Dict
from datetime import datetime, UTC
import requests
from enum import Enum
from multiprocessing import Process, Manager

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


def send_log(message: str, level: LogLevel = LogLevel.INFO) -> None:
    """Sendet Logs an den Logging Service"""
    log_data = {
        "source": LogSource.SYSTEM,
        "level": level,
        "message": message,
        "component": "process-manager",
        "status": "active",
        "timestamp": datetime.now(UTC).isoformat()
    }

    try:
        requests.post("http://logging:8000/log", json=log_data, timeout=5)
    except Exception as e:
        logger.error(f"Failed to send log: {e}")


def run_symbol_pipeline(symbol: str):
    """
    Führt die komplette Pipeline für ein Symbol aus
    """
    try:
        from layer.raw.collector import main as collector_main
        from layer.normalized.processor import main as processor_main
        from layer.feature.processor import main as feature_main

        # Queues für Layer-Kommunikation
        raw_to_normalized_queue = multiprocessing.Queue()
        normalized_to_feature_queue = multiprocessing.Queue()

        # Prozesse für jeden Layer
        collector = Process(
            target=collector_main,
            args=(raw_to_normalized_queue, symbol),
            name=f"collector_{symbol}"
        )

        normalizer = Process(
            target=processor_main,
            args=(raw_to_normalized_queue, normalized_to_feature_queue, symbol),
            name=f"normalizer_{symbol}"
        )

        feature_processor = Process(
            target=feature_main,
            args=(normalized_to_feature_queue, symbol),
            name=f"feature_{symbol}"
        )

        # Prozesse starten
        collector.start()
        logger.info(f"Started collector for {symbol}")

        normalizer.start()
        logger.info(f"Started normalizer for {symbol}")

        feature_processor.start()
        logger.info(f"Started feature processor for {symbol}")

        # Auf Prozesse warten
        collector.join()
        normalizer.join()
        feature_processor.join()

    except Exception as e:
        logger.error(f"Error in pipeline for {symbol}: {str(e)}")
        send_log(f"Error in pipeline for {symbol}: {str(e)}", LogLevel.ERROR)
        raise


def load_config() -> Dict:
    """Lädt die Konfiguration aus der YAML-Datei"""
    try:
        with open('/app/config/symbols.yaml', 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        raise


def main():
    try:
        # Konfiguration laden
        config = load_config()
        symbols = [symbol['pair'] for symbol in config['symbols']]
        total_symbols = len(symbols)

        send_log(f"Starting processing for {total_symbols} symbols")
        logger.info(f"Processing symbols: {symbols}")

        # Prozesse für jedes Symbol erstellen
        processes = []
        for symbol in symbols:
            p = Process(target=run_symbol_pipeline, args=(symbol,))
            processes.append(p)
            p.start()
            logger.info(f"Started pipeline for {symbol}")
            time.sleep(1)  # Kleine Verzögerung zwischen Starts

        # Auf alle Prozesse warten
        for p in processes:
            p.join()

    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error in main process: {str(e)}")
        send_log(f"Error in main process: {str(e)}", LogLevel.ERROR)
        sys.exit(1)


if __name__ == "__main__":
    main()