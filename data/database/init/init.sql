-- Aktiviere die TimescaleDB Extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Raw Market Data Table
CREATE TABLE IF NOT EXISTS raw_market_data (
    date DATE NOT NULL,
    symbol TEXT NOT NULL,
    open DOUBLE PRECISION,
    high DOUBLE PRECISION,
    low DOUBLE PRECISION,
    close DOUBLE PRECISION,
    volume DOUBLE PRECISION,
    CONSTRAINT raw_market_data_pkey PRIMARY KEY (date, symbol)
);

-- Normalized Market Data Table
CREATE TABLE IF NOT EXISTS normalized_market_data (
    date DATE NOT NULL,
    symbol TEXT NOT NULL,

    -- Original Werte
    raw_open DOUBLE PRECISION,
    raw_high DOUBLE PRECISION,
    raw_low DOUBLE PRECISION,
    raw_close DOUBLE PRECISION,
    raw_volume DOUBLE PRECISION,

    -- Preis Normalisierung
    returns DOUBLE PRECISION,              -- (close[t]/close[t-1] - 1)
    log_returns DOUBLE PRECISION,          -- log(close[t]/close[t-1])
    zscore_price DOUBLE PRECISION,         -- (price - rolling_mean) / rolling_std

    -- Volumen Normalisierung
    volume_minmax DOUBLE PRECISION,        -- (volume - min) / (max - min)
    log_volume DOUBLE PRECISION,           -- log(1 + volume)
    zscore_volume DOUBLE PRECISION,        -- (volume - rolling_mean) / rolling_std

    -- Turbulence Index Components
    rolling_mean_return DOUBLE PRECISION,  -- Für Turbulence Berechnung
    rolling_std_return DOUBLE PRECISION,   -- Für Turbulence Berechnung
    turbulence_index DOUBLE PRECISION,     -- Finaler Turbulence Index
    rel_turbulence DOUBLE PRECISION,       -- turbulence/historical_mean

    -- Metadata
    last_updated TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT normalized_market_data_pkey PRIMARY KEY (date, symbol)
);

-- Feature Market Data Table
CREATE TABLE IF NOT EXISTS feature_market_data (
    -- Primary Key Columns
    date DATE NOT NULL,
    symbol TEXT NOT NULL,

    -- Original Raw Values from normalized_market_data
    raw_open DOUBLE PRECISION,
    raw_high DOUBLE PRECISION,
    raw_low DOUBLE PRECISION,
    raw_close DOUBLE PRECISION,
    raw_volume DOUBLE PRECISION,

    -- Normalized Price Values
    returns DOUBLE PRECISION,              -- (close[t]/close[t-1] - 1)
    log_returns DOUBLE PRECISION,          -- log(close[t]/close[t-1])
    zscore_price DOUBLE PRECISION,         -- (price - rolling_mean) / rolling_std

    -- Normalized Volume Values
    volume_minmax DOUBLE PRECISION,        -- (volume - min) / (max - min)
    log_volume DOUBLE PRECISION,           -- log(1 + volume)
    zscore_volume DOUBLE PRECISION,        -- (volume - rolling_mean) / rolling_std

    -- Turbulence Index Components
    rolling_mean_return DOUBLE PRECISION,  -- Für Turbulence Berechnung
    rolling_std_return DOUBLE PRECISION,   -- Für Turbulence Berechnung
    turbulence_index DOUBLE PRECISION,     -- Finaler Turbulence Index
    rel_turbulence DOUBLE PRECISION,       -- turbulence/historical_mean

    -- MACD Components (Moving Average Convergence Divergence)
    macd_line DOUBLE PRECISION,           -- MACD Line (12-day EMA - 26-day EMA)
    macd_signal DOUBLE PRECISION,         -- 9-day EMA of MACD Line
    macd_histogram DOUBLE PRECISION,      -- MACD Line - Signal Line

    -- RSI Components (Relative Strength Index)
    rsi_14 DOUBLE PRECISION,             -- 14-period RSI
    rsi_avg_gain DOUBLE PRECISION,        -- Average Gain component of RSI
    rsi_avg_loss DOUBLE PRECISION,        -- Average Loss component of RSI

    -- CCI Components (Commodity Channel Index)
    cci_20 DOUBLE PRECISION,             -- 20-period CCI
    cci_typical_price DOUBLE PRECISION,   -- (High + Low + Close)/3
    cci_sma_tp DOUBLE PRECISION,         -- 20-period SMA of Typical Price
    cci_mean_deviation DOUBLE PRECISION,  -- Mean Deviation

    -- ADX Components (Average Directional Index)
    adx_14 DOUBLE PRECISION,             -- 14-period ADX
    plus_di_14 DOUBLE PRECISION,         -- +DI 14 period
    minus_di_14 DOUBLE PRECISION,        -- -DI 14 period
    dx_14 DOUBLE PRECISION,              -- Directional Index
    tr_14 DOUBLE PRECISION,              -- True Range 14 period

    -- Metadata
    last_updated TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT feature_market_data_pkey PRIMARY KEY (date, symbol)
);

-- Create hypertable
SELECT create_hypertable('normalized_market_data', 'date', if_not_exists => TRUE);
SELECT create_hypertable('feature_market_data', 'date', if_not_exists => TRUE);

-- Create indices
CREATE INDEX IF NOT EXISTS idx_norm_symbol_date ON normalized_market_data (symbol, date DESC);
CREATE INDEX IF NOT EXISTS idx_norm_turbulence ON normalized_market_data (date, turbulence_index);

CREATE INDEX IF NOT EXISTS idx_feature_symbol_date ON feature_market_data (symbol, date DESC);
CREATE INDEX IF NOT EXISTS idx_feature_returns ON feature_market_data (symbol, returns);
CREATE INDEX IF NOT EXISTS idx_feature_turbulence ON feature_market_data (date, turbulence_index);
CREATE INDEX IF NOT EXISTS idx_feature_macd ON feature_market_data (date, macd_line);
CREATE INDEX IF NOT EXISTS idx_feature_rsi ON feature_market_data (date, rsi_14);
CREATE INDEX IF NOT EXISTS idx_feature_cci ON feature_market_data (date, cci_20);
CREATE INDEX IF NOT EXISTS idx_feature_adx ON feature_market_data (date, adx_14);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO trading;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO trading;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO trading;