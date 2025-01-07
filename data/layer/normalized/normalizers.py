import numpy as np
import pandas as pd
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class MarketDataNormalizer:
    """
    Klasse für verschiedene Normalisierungsberechnungen von Marktdaten.
    Enthält verschiedene statistische Transformationen und Normalisierungen.
    """

    @staticmethod
    def calculate_returns(data: List[Dict]) -> Dict[str, List[Optional[float]]]:
        """
        Berechnet einfache und logarithmische Returns
        """
        try:
            df = pd.DataFrame(data)
            logger.info(f"Returns calculation - DataFrame columns: {df.columns.tolist()}")
            logger.info(f"First row data: {df.iloc[0].to_dict() if not df.empty else 'Empty DataFrame'}")

            # Sortiere nach Datum
            df = df.sort_values('date')

            # Returns berechnen
            returns = df['raw_close'].pct_change()
            log_returns = np.log(df['raw_close'] / df['raw_close'].shift(1))

            # Konvertiere NaN, inf zu None
            returns = returns.replace([np.inf, -np.inf, np.nan], None)
            log_returns = log_returns.replace([np.inf, -np.inf, np.nan], None)

            return {
                'returns': returns.tolist(),
                'log_returns': log_returns.tolist()
            }

        except Exception as e:
            logger.error(f"Error in calculate_returns: {str(e)}")
            logger.error(f"Data sample: {data[0] if data else 'No data'}")
            raise

    @staticmethod
    def calculate_volume_metrics(data: List[Dict], window_size: int = 20) -> Dict[str, List[Optional[float]]]:
        """
        Berechnet verschiedene Volumen-Normalisierungen:
        - Min-Max Skalierung
        - Log Transformation
        - Z-Score (Rolling Window)
        """
        try:
            df = pd.DataFrame(data)
            df = df.sort_values('date')  # Sicherstellen, dass Daten zeitlich sortiert sind

            logger.info(f"Volume metrics calculation - DataFrame columns: {df.columns.tolist()}")

            # Konvertiere zu numeric, ersetze 0 durch NaN für log
            volumes = pd.to_numeric(df['raw_volume'], errors='coerce')

            # Min-Max Normalisierung
            vol_min = volumes.min()
            vol_max = volumes.max()
            volume_minmax = (volumes - vol_min) / (vol_max - vol_min)

            # Log Transformation (add small constant to handle zeros)
            log_volume = np.log1p(volumes)

            # Z-Score
            rolling_mean = volumes.rolling(window=window_size, min_periods=1).mean()
            rolling_std = volumes.rolling(window=window_size, min_periods=1).std()
            zscore_volume = (volumes - rolling_mean) / rolling_std

            # Konvertiere NaN, inf zu None
            volume_minmax = volume_minmax.replace([np.inf, -np.inf, np.nan], None)
            log_volume = log_volume.replace([np.inf, -np.inf, np.nan], None)
            zscore_volume = zscore_volume.replace([np.inf, -np.inf, np.nan], None)

            return {
                'volume_minmax': volume_minmax.tolist(),
                'log_volume': log_volume.tolist(),
                'zscore_volume': zscore_volume.tolist()
            }

        except Exception as e:
            logger.error(f"Error in calculate_volume_metrics: {str(e)}")
            logger.error(f"Data sample: {data[0] if data else 'No data'}")
            raise

    @staticmethod
    def calculate_price_metrics(data: List[Dict], window_size: int = 20) -> Dict[str, List[Optional[float]]]:
        """
        Berechnet Preis-basierte Metriken:
        - Z-Score der Preise
        """
        try:
            df = pd.DataFrame(data)
            df = df.sort_values('date')

            logger.info(f"Price metrics calculation - DataFrame columns: {df.columns.tolist()}")

            prices = pd.to_numeric(df['raw_close'], errors='coerce')

            # Z-Score
            rolling_mean = prices.rolling(window=window_size, min_periods=1).mean()
            rolling_std = prices.rolling(window=window_size, min_periods=1).std()
            zscore_price = (prices - rolling_mean) / rolling_std

            # Konvertiere NaN, inf zu None
            zscore_price = zscore_price.replace([np.inf, -np.inf, np.nan], None)

            return {
                'zscore_price': zscore_price.tolist()
            }

        except Exception as e:
            logger.error(f"Error in calculate_price_metrics: {str(e)}")
            logger.error(f"Data sample: {data[0] if data else 'No data'}")
            raise

    @staticmethod
    def calculate_turbulence_metrics(data: List[Dict], window_size: int = 60) -> Dict[str, List[Optional[float]]]:
        """
        Berechnet den Turbulence Index nach Kritzman und Li (2010)
        sowie die relative Turbulence
        """
        try:
            df = pd.DataFrame(data)
            df = df.sort_values('date')

            logger.info(f"Turbulence calculation - DataFrame columns: {df.columns.tolist()}")

            # Preise zu Returns konvertieren
            returns = pd.to_numeric(df['raw_close'], errors='coerce').pct_change()

            # Rolling Statistiken für Turbulence berechnen
            rolling_mean = returns.rolling(window=window_size, min_periods=1).mean()
            rolling_std = returns.rolling(window=window_size, min_periods=1).std()

            # Turbulence Index berechnen: (y_t - μ)^2 / σ^2
            # Vereinfachte Version der Mahalanobis-Distanz für einzelne Zeitreihe
            differences = returns - rolling_mean
            turbulence_index = (differences ** 2) / (rolling_std ** 2)

            # Relative Turbulence: Verhältnis zum historischen Durchschnitt
            hist_turbulence_mean = turbulence_index.rolling(window=window_size, min_periods=1).mean()
            relative_turbulence = turbulence_index / hist_turbulence_mean

            # Speichere auch die Rolling-Statistiken für spätere Verwendung
            metrics = {
                'rolling_mean_return': rolling_mean.replace([np.inf, -np.inf, np.nan], None).tolist(),
                'rolling_std_return': rolling_std.replace([np.inf, -np.inf, np.nan], None).tolist(),
                'turbulence_index': turbulence_index.replace([np.inf, -np.inf, np.nan], None).tolist(),
                'rel_turbulence': relative_turbulence.replace([np.inf, -np.inf, np.nan], None).tolist()
            }

            logger.info(f"Turbulence metrics calculated successfully")
            return metrics

        except Exception as e:
            logger.error(f"Error in calculate_turbulence_metrics: {str(e)}")
            logger.error(f"Data sample: {data[0] if data else 'No data'}")
            raise

    def normalize_batch(self,
                     data: List[Dict],
                     calculate_returns: bool = True,
                     calculate_volume: bool = True,
                     calculate_price: bool = True,
                     calculate_turbulence: bool = True,
                     volume_window: int = 20,
                     price_window: int = 20,
                     turbulence_window: int = 60) -> List[Dict]:
        """
        Hauptmethode zur Batch-Normalisierung aller gewünschten Metriken
        """
        try:
            logger.info(f"Starting batch normalization for {len(data)} records")
            logger.info(f"First row of input data: {data[0] if data else 'No data'}")

            results = []
            metrics = {}

            if calculate_returns:
                logger.info("Calculating returns...")
                ret_metrics = self.calculate_returns(data)
                metrics.update(ret_metrics)
                logger.info(f"Returns metrics keys: {ret_metrics.keys()}")

            if calculate_volume:
                logger.info("Calculating volume metrics...")
                vol_metrics = self.calculate_volume_metrics(data, volume_window)
                metrics.update(vol_metrics)
                logger.info(f"Volume metrics keys: {vol_metrics.keys()}")

            if calculate_price:
                logger.info("Calculating price metrics...")
                price_metrics = self.calculate_price_metrics(data, price_window)
                metrics.update(price_metrics)
                logger.info(f"Price metrics keys: {price_metrics.keys()}")

            if calculate_turbulence:
                logger.info("Calculating turbulence metrics...")
                turb_metrics = self.calculate_turbulence_metrics(data, turbulence_window)
                metrics.update(turb_metrics)
                logger.info(f"Turbulence metrics keys: {turb_metrics.keys()}")

            # Kombiniere Original-Daten mit berechneten Metriken
            for i, row in enumerate(data):
                result = row.copy()
                for metric_name, metric_values in metrics.items():
                    result[metric_name] = metric_values[i] if i < len(metric_values) else None
                results.append(result)

            logger.info(f"Successfully normalized {len(results)} records")
            logger.info(f"First normalized row: {results[0] if results else 'No results'}")

            return results

        except Exception as e:
            logger.error(f"Error in normalize_batch: {str(e)}")
            logger.error(f"Data type: {type(data)}")
            if data:
                logger.error(f"First row type: {type(data[0])}")
                logger.error(f"First row content: {data[0]}")
            raise