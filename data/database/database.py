import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, UTC
import logging
from contextlib import contextmanager


class DatabaseConnection:
    def __init__(self, logger_url="http://logging:8000"):
        self.engine = create_engine(
            "postgresql://trading:trading@timescaledb:5432/trading_data"  # Angepasstes Passwort
        )
        self.Session = sessionmaker(bind=self.engine)
        self.logger_url = logger_url

    @contextmanager
    def get_session(self):
        session = self.Session()
        try:
            yield session
            session.commit()
            self._log_db_operation("session_commit", "success")
        except Exception as e:
            session.rollback()
            self._log_db_operation("session_rollback", "error", str(e))
            raise
        finally:
            session.close()

    def _log_db_operation(self, action: str, status: str, error_details: str = None):
        log_data = {
            "source": "database",
            "level": "ERROR" if status == "error" else "INFO",
            "message": f"Database operation {action}: {status}",
            "component": "raw_layer",
            "action": action,
            "status": status,
            "metadata": {
                "timestamp": datetime.now(UTC).isoformat(),
                "error_details": error_details
            } if error_details else None
        }

        try:
            requests.post(f"{self.logger_url}/log", json=log_data)
        except Exception as e:
            logging.error(f"Failed to send log: {e}")