CREATE TABLE IF NOT EXISTS stock_constituents
(
    symbol String,
    security String,
    gics_sector String,
    gics_sub_industry String,
    headquarters_location String,
    date_added Date,
    cik UInt64,
    founded UInt16
) ENGINE = MergeTree()
ORDER BY symbol;

-- Insert data from CSV file
INSERT INTO stock_constituents
SELECT
    Symbol as symbol,
    Security as security,
    `GICS Sector` as gics_sector,
    `GICS Sub-Industry` as gics_sub_industry,
    `Headquarters Location` as headquarters_location,
    toDate(`Date added`) as date_added,
    CIK as cik,
    Founded as founded
FROM file('/var/lib/clickhouse/user_files/sp500_constituents.csv', CSVWithNames);
