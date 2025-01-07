import numpy as np
import pandas as pd
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """
    Klasse für die Berechnung verschiedener technischer Indikatoren.
    Implementiert MACD, RSI, CCI und ADX.
    """

    @staticmethod
    def calculate_macd(data: List[Dict], fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Dict[
        str, List[Optional[float]]]:
        """
        Berechnet den MACD (Moving Average Convergence Divergence)
        - MACD Line = 12-EMA - 26-EMA
        - Signal Line = 9-EMA of MACD Line
        - MACD Histogram = MACD Line - Signal Line
        """
        try:
            df = pd.DataFrame(data)
            df = df.sort_values('date')

            # Berechne EMAs
            close_prices = pd.to_numeric(df['raw_close'], errors='coerce')
            fast_ema = close_prices.ewm(span=fast_period, adjust=False).mean()
            slow_ema = close_prices.ewm(span=slow_period, adjust=False).mean()

            # MACD Line
            macd_line = fast_ema - slow_ema

            # Signal Line
            signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()

            # MACD Histogram
            macd_histogram = macd_line - signal_line

            return {
                'macd_line': macd_line.replace([np.inf, -np.inf, np.nan], None).tolist(),
                'macd_signal': signal_line.replace([np.inf, -np.inf, np.nan], None).tolist(),
                'macd_histogram': macd_histogram.replace([np.inf, -np.inf, np.nan], None).tolist()
            }

        except Exception as e:
            logger.error(f"Error in calculate_macd: {str(e)}")
            logger.error(f"Data sample: {data[0] if data else 'No data'}")
            raise

    @staticmethod
    def calculate_rsi(data: List[Dict], period: int = 14) -> Dict[str, List[Optional[float]]]:
        """
        Berechnet den RSI (Relative Strength Index)
        RSI = 100 - (100 / (1 + RS))
        RS = Average Gain / Average Loss
        """
        try:
            df = pd.DataFrame(data)
            df = df.sort_values('date')

            close_prices = pd.to_numeric(df['raw_close'], errors='coerce')
            price_diff = close_prices.diff()

            # Separate gains and losses
            gains = price_diff.copy()
            losses = price_diff.copy()
            gains[gains < 0] = 0
            losses[losses > 0] = 0
            losses = abs(losses)

            # Calculate average gains and losses
            avg_gains = gains.rolling(window=period, min_periods=1).mean()
            avg_losses = losses.rolling(window=period, min_periods=1).mean()

            # Calculate RS and RSI
            rs = avg_gains / avg_losses
            rsi = 100 - (100 / (1 + rs))

            return {
                'rsi_14': rsi.replace([np.inf, -np.inf, np.nan], None).tolist(),
                'rsi_avg_gain': avg_gains.replace([np.inf, -np.inf, np.nan], None).tolist(),
                'rsi_avg_loss': avg_losses.replace([np.inf, -np.inf, np.nan], None).tolist()
            }

        except Exception as e:
            logger.error(f"Error in calculate_rsi: {str(e)}")
            logger.error(f"Data sample: {data[0] if data else 'No data'}")
            raise

    @staticmethod
    def calculate_mean_deviation(series: pd.Series, window: int) -> pd.Series:
        """Berechnet die Mean Absolute Deviation für eine rolling window"""

        def mad(x):
            return np.abs(x - x.mean()).mean()

        return series.rolling(window=window).apply(mad, raw=True)

    @staticmethod
    def calculate_cci(data: List[Dict], period: int = 20) -> Dict[str, List[Optional[float]]]:
        """
        Berechnet den CCI (Commodity Channel Index)
        CCI = (Typical Price - SMA(TP)) / (0.015 * Mean Deviation)
        Typical Price = (High + Low + Close) / 3
        """
        try:
            df = pd.DataFrame(data)
            df = df.sort_values('date')

            # Berechne Typical Price
            high = pd.to_numeric(df['raw_high'], errors='coerce')
            low = pd.to_numeric(df['raw_low'], errors='coerce')
            close = pd.to_numeric(df['raw_close'], errors='coerce')

            typical_price = (high + low + close) / 3
            tp_sma = typical_price.rolling(window=period).mean()

            # Berechne Mean Deviation manuell
            mean_deviation = TechnicalIndicators.calculate_mean_deviation(typical_price, period)

            # Berechne CCI
            cci = (typical_price - tp_sma) / (0.015 * mean_deviation)

            return {
                'cci_20': cci.replace([np.inf, -np.inf, np.nan], None).tolist(),
                'cci_typical_price': typical_price.replace([np.inf, -np.inf, np.nan], None).tolist(),
                'cci_sma_tp': tp_sma.replace([np.inf, -np.inf, np.nan], None).tolist(),
                'cci_mean_deviation': mean_deviation.replace([np.inf, -np.inf, np.nan], None).tolist()
            }

        except Exception as e:
            logger.error(f"Error in calculate_cci: {str(e)}")
            logger.error(f"Data sample: {data[0] if data else 'No data'}")
            raise

    @staticmethod
    def calculate_adx(data: List[Dict], period: int = 14) -> Dict[str, List[Optional[float]]]:
        """
        Berechnet den ADX (Average Directional Index)
        ADX = SMA(DX, period)
        DX = 100 * |+DI - -DI| / (+DI + -DI)
        """
        try:
            df = pd.DataFrame(data)
            df = df.sort_values('date')

            high = pd.to_numeric(df['raw_high'], errors='coerce')
            low = pd.to_numeric(df['raw_low'], errors='coerce')
            close = pd.to_numeric(df['raw_close'], errors='coerce')

            # True Range
            high_low = high - low
            high_close = abs(high - close.shift(1))
            low_close = abs(low - close.shift(1))
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            tr_period = true_range.rolling(window=period).mean()

            # Directional Movement
            plus_dm = high.diff()
            minus_dm = low.diff()
            plus_dm[plus_dm < 0] = 0
            minus_dm[minus_dm > 0] = 0
            minus_dm = abs(minus_dm)

            # Smooth DM
            plus_di = 100 * (plus_dm.rolling(window=period).mean() / tr_period)
            minus_di = 100 * (minus_dm.rolling(window=period).mean() / tr_period)

            # Directional Index
            dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)

            # Average Directional Index
            adx = dx.rolling(window=period).mean()

            return {
                'adx_14': adx.replace([np.inf, -np.inf, np.nan], None).tolist(),
                'plus_di_14': plus_di.replace([np.inf, -np.inf, np.nan], None).tolist(),
                'minus_di_14': minus_di.replace([np.inf, -np.inf, np.nan], None).tolist(),
                'dx_14': dx.replace([np.inf, -np.inf, np.nan], None).tolist(),
                'tr_14': tr_period.replace([np.inf, -np.inf, np.nan], None).tolist()
            }

        except Exception as e:
            logger.error(f"Error in calculate_adx: {str(e)}")
            logger.error(f"Data sample: {data[0] if data else 'No data'}")
            raise

    def calculate_all_indicators(self,
                                 data: List[Dict],
                                 calculate_macd: bool = True,
                                 calculate_rsi: bool = True,
                                 calculate_cci: bool = True,
                                 calculate_adx: bool = True) -> List[Dict]:
        """
        Hauptmethode zur Berechnung aller gewünschten technischen Indikatoren
        """
        try:
            logger.info(f"Starting technical indicators calculation for {len(data)} records")
            logger.info(f"First row of input data: {data[0] if data else 'No data'}")

            results = []
            indicator_values = {}

            if calculate_macd:
                logger.info("Calculating MACD...")
                macd_data = self.calculate_macd(data)
                indicator_values.update(macd_data)

            if calculate_rsi:
                logger.info("Calculating RSI...")
                rsi_data = self.calculate_rsi(data)
                indicator_values.update(rsi_data)

            if calculate_cci:
                logger.info("Calculating CCI...")
                cci_data = self.calculate_cci(data)
                indicator_values.update(cci_data)

            if calculate_adx:
                logger.info("Calculating ADX...")
                adx_data = self.calculate_adx(data)
                indicator_values.update(adx_data)

            # Kombiniere Original-Daten mit berechneten Indikatoren
            for i, row in enumerate(data):
                result = row.copy()
                for indicator_name, indicator_values_list in indicator_values.items():
                    result[indicator_name] = indicator_values_list[i] if i < len(indicator_values_list) else None
                results.append(result)

            logger.info(f"Successfully calculated indicators for {len(results)} records")
            logger.info(f"First calculated row: {results[0] if results else 'No results'}")

            return results

        except Exception as e:
            logger.error(f"Error in calculate_all_indicators: {str(e)}")
            logger.error(f"Data type: {type(data)}")
            if data:
                logger.error(f"First row type: {type(data[0])}")
                logger.error(f"First row content: {data[0]}")
            raise