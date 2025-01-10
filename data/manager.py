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
        "component": "pci-manager",
        "status": "active",
        "timestamp": datetime.now(UTC).isoformat()
    }

    try:
        requests.post("http://logging:8000/log", json=log_data, timeout=5)
    except Exception as e:
        logger.error(f"Failed to send log: {e}")


def run_pair_pipeline(pair_id: str):
    try:
        symbol1, symbol2 = pair_id.split('_')
        from layer.raw.collector import main as collector_main
        from layer.pci.pci_layer import main as pci_main

        raw_to_pci_queue = multiprocessing.Queue()
        pci_to_feature_queue = multiprocessing.Queue()

        collector1 = Process(target=collector_main, args=(raw_to_pci_queue, symbol1))
        collector2 = Process(target=collector_main, args=(raw_to_pci_queue, symbol2))

        collector1.start()
        logger.info(f"Started collector for {symbol1}")
        time.sleep(1)
        collector2.start()
        logger.info(f"Started collector for {symbol2}")

        config = load_config()
        if config['settings'].get('pci_enabled', True):
            pci_processor = Process(target=pci_main, args=(raw_to_pci_queue, pci_to_feature_queue, pair_id))
            pci_processor.start()
            logger.info(f"Started PCI processor for pair {pair_id}")
            pci_processor.join()

        collector1.join()
        collector2.join()

    except Exception as e:
        logger.error(f"Error in pipeline for pair {pair_id}: {str(e)}")
        send_log(f"Error in pipeline for pair {pair_id}: {str(e)}", LogLevel.ERROR)
        raise


def load_config() -> Dict:
    """Lädt die Konfiguration aus der YAML-Datei"""
    try:
        with open('/app/config/settings.yaml', 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        raise


def main():
    try:
        # Konfiguration laden
        config = load_config()

        # Aktive Paare aus der PCI-Sektion filtern
        active_pairs = [
            f"{pair['primary']}_{pair['secondary']}"
            for pair in config.get('pci_pairs', [])
            if pair.get('active', False)
        ]

        total_pairs = len(active_pairs)
        send_log(f"Starting processing for {total_pairs} pairs")
        logger.info(f"Processing pairs: {active_pairs}")

        # Prozesse für jedes Paar erstellen
        processes = []
        for pair_id in active_pairs:
            p = Process(target=run_pair_pipeline, args=(pair_id,))
            processes.append(p)
            p.start()
            logger.info(f"Started pipeline for pair {pair_id}")
            time.sleep(2)  # Verzögerung zwischen Pair-Starts

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