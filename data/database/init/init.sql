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

CREATE TABLE IF NOT EXISTS pci_market_data (
    date DATE NOT NULL,
    symbol_pair TEXT NOT NULL,  -- z.B. "AAPL_MSFT"
    symbol1 TEXT NOT NULL,
    symbol2 TEXT NOT NULL,

    -- State Space Components
    beta DOUBLE PRECISION,      -- Hedge Ratio
    rho DOUBLE PRECISION,       -- AR(1) Koeffizient
    sigma_m DOUBLE PRECISION,   -- Std.Dev Mean-Reverting
    sigma_r DOUBLE PRECISION,   -- Std.Dev Random Walk

    -- Trading Signals
    mt DOUBLE PRECISION,        -- Mean-Reverting Component
    rt DOUBLE PRECISION,        -- Random Walk Component
    zscore DOUBLE PRECISION,    -- Normalisierter Trading Signal

    -- Statistiken
    r2_mr DOUBLE PRECISION,     -- R² Mean-Reversion
    lr_score DOUBLE PRECISION,  -- Likelihood Ratio Score

    last_updated TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pci_market_data_pkey PRIMARY KEY (date, symbol_pair)
);

-- Create hypertable
SELECT create_hypertable('pci_market_data', 'date', if_not_exists => TRUE);

-- Create indices
CREATE INDEX IF NOT EXISTS idx_pci_pair_date ON pci_market_data (symbol_pair, date DESC);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO trading;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO trading;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO trading;