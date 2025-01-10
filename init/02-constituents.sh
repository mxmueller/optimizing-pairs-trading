#!/bin/bash
cp /data/sp500_constituents.csv /var/lib/clickhouse/user_files/
chown clickhouse:clickhouse /var/lib/clickhouse/user_files/sp500_constituents.csv
