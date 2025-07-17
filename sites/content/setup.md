---
title: "Backtesting Demonstrator Setup Guide"
math: true  
readTime: true
---


clone

```bash
git clone --recurse-submodules https://github.com/mxmueller/optimizing-pairs-trading
```

check if docker is setup and running 

```bash
docker --version
docker compose version
```


```bash
docker-compose up --build --detach
```


# Costum Setup 

#### Configuration (`config.yaml`)

### MinIO Credentials
```yaml
minio:
  user: minioadmin       
  password: minioadmin   
```

### Storage Configuration
```yaml
storage:
  base_bucket: markets    # Root bucket name
  markets:
    - name: FTSE100       # Market identifier
      data_file: market_data.parquet          # Target filename in bucket
      data_path: /host-data/raw/ftse_daily.parquet  # Source file path
      strategies:
        - file: Cluster_Bollinger_Sliding.parquet   # Target filename
          source_path: /host-data/results/ftse100/Cluster_Bollinger_Sliding.parquet  # Source path
          type: Bollinger                     # Strategy type (metadata)
          description: Cluster Bollinger Sliding Strategy  # Description (metadata)
          pair_finding: Clustering            # Pair finding method (metadata)
```

## Storage Structure

### MinIO Bucket Layout
```
markets/                          # base_bucket
├── FTSE100/                      # markets[].name
│   ├── market_data.parquet       # markets[].data_file
│   └── strategies/
│       ├── strategy1.parquet     # strategies[].file
│       └── strategy2.parquet
└── NASDAQ100/
    ├── market_data.parquet
    └── strategies/
        ├── strategy1.parquet
        └── strategy2.parquet
```

### Host Filesystem Requirements
```
data/                            # Mounted as /host-data in container
├── raw/                         # Market data source
│   ├── ftse_daily.parquet       # → data_path
│   └── nasdaq_daily.parquet
└── results/                     # Strategy data source
    ├── ftse100/                 # → source_path
    │   ├── Cluster_Bollinger_Sliding.parquet
    │   ├── Cluster_Z-Score_Sliding.parquet
    │   └── ...
    └── nasdaq100/
        ├── Cluster_Bollinger_Sliding.parquet
        ├── Cluster_Z-Score_Sliding.parquet
        └── ...
```