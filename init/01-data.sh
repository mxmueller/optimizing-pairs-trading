#!/bin/bash
cp /data/sp500_stock_data.parquet /var/lib/clickhouse/user_files/
chown clickhouse:clickhouse /var/lib/clickhouse/user_files/sp500_stock_data.parquet
