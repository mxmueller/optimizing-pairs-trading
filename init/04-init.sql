CREATE TABLE IF NOT EXISTS stock_data
(
    symbol String,
    date Date,
    open Float64,
    high Float64,
    low Float64,
    close Float64,
    volume Int64
) ENGINE = MergeTree()
ORDER BY (symbol, date);

INSERT INTO stock_data
SELECT *
FROM file('/var/lib/clickhouse/user_files/sp500_stock_data.parquet', Parquet);
