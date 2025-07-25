---
title: "Backtesting Demonstrator Setup Guide"
math: true  
readTime: true
---

The microservices architecture demonstrates a complete backtesting pipeline for pairs trading strategies. Each service fulfills a specific role in the data processing and analysis workflow.

{{< figure src="/images/archi.drawio.png" width="800" style="text-align: center; margin: 0 auto;" >}}

The **Notebook Runner** (`notebook_runner`) service leverages papermill to execute all possible permutations of pair-finding algorithms and trading strategies through parameterized Jupyter notebooks. This allows for systematic generation and testing of different strategy combinations across various market conditions. The **MinIO** blob storage service serves as the central data repository, containing both the theoretical results presented in the research and raw market data. Additionally, all newly generated strategy runs are automatically stored here, creating a comprehensive historical record of backtesting results. The **Analytics** (`analytics`) service processes trade data from the blob storage along with raw market data to calculate comprehensive performance metrics. This backend service handles all computational-heavy operations including risk metrics, return calculations, and portfolio statistics. The **Streamlit** application provides a unified interface for data visualization, performance analysis, and strategy management. Users can explore raw data, examine trading results, analyze performance metrics, and commission new notebook runs directly through the web interface. All services are located under `src/backtester/services/` and communicate through REST APIs and shared storage.

## Quick Setup

The following steps will deploy the complete backtesting environment with all required services and pre-configured data. The initial setup automatically provisions MinIO storage, loads market data, and prepares the analytical backend for immediate use.

**Clone Repository**

Download the complete project repository including all submodules and navigate to the project directory.

```bash
git clone --recurse-submodules https://github.com/mxmueller/optimizing-pairs-trading
cd optimizing-pairs-trading
```

**Verify Docker Installation**

Ensure Docker and Docker Compose are properly installed on your system before proceeding with the deployment.

```bash
docker --version
docker compose version
```

**Start Services**

The Docker Compose configuration handles service dependencies and health checks automatically. MinIO will initialize first, followed by the analytics backend, notebook runner, and finally the Streamlit frontend. The initial startup may take several minutes as Docker builds images and provisions storage.

```bash
docker-compose up --build --detach
```

**Verify Deployment**

Monitor the deployment progress and ensure all services reach healthy status. The MinIO service includes a health check that verifies data loading completion before dependent services start.

```bash
docker-compose ps
```

All services should show `healthy` or `running` status.

## Service Access

The following services will be available once deployment completes. Each service provides different capabilities for strategy development, backtesting, and analysis. Access credentials for MinIO are configured in the setup and can be modified in the configuration file.

| Service | URL |
|---------|-----|
| **Streamlit** | http://localhost:8501 |
| **Analytics API** | http://localhost:8000/docs |
| **Notebook Runner API** | http://localhost:8080/docs |
| **MinIO Console** | http://localhost:9001 |

****

## Troubleshooting

Common deployment issues often relate to Docker resource constraints, port conflicts, or data file accessibility. The containerized architecture includes health checks and dependency management, but initial setup may require troubleshooting depending on your local environment configuration.

**Service Won't Start**

Check service logs and restart individual services if needed to resolve startup issues.

```bash
# Check logs
docker-compose logs [service-name]

# Restart specific service
docker-compose restart [service-name]
```

**Data Not Loading**

Verify data files exist in the expected locations and check file permissions and configuration settings.

- Verify data files exist in `./data/` directory
- Check file paths in `config.yaml` match actual structure
- Ensure MinIO has read access to mounted volumes

**Port Conflicts**

Modify port mappings in the Docker Compose configuration if default ports are already in use.

```yaml
ports:
  - "8501:8501"  # Change first number only
```

****

## Configuration (Expert Mode)

The system configuration is centralized in a single YAML file that defines storage locations, access credentials, and data mapping between the host filesystem and MinIO buckets. This configuration drives the automatic setup process and determines how market data and strategies are organized within the storage layer.

**Basic Configuration (config.yaml)**

The configuration file maps local data sources to MinIO bucket structures and includes metadata for strategy classification. Each market requires both raw price data and any pre-computed trading strategies that should be loaded during initialization.

```yaml
minio:
  user: minioadmin
  password: minioadmin

storage:
  base_bucket: markets
  markets:
    - name: FTSE100
      data_file: market_data.parquet
      data_path: /host-data/raw/ftse_daily.parquet
      strategies:
        - file: Cluster_Bollinger_Sliding.parquet
          source_path: /host-data/results/ftse100/Cluster_Bollinger_Sliding.parquet
          type: Bollinger
          description: Cluster Bollinger Sliding Strategy
          pair_finding: Clustering
```

**Required Data Structure**

The host filesystem must be organized according to the expected directory structure. Raw market data files contain OHLCV price series for all symbols in each market, while the results directory stores pre-computed strategy outputs from previous backtesting runs.

```
data/                                    
├── raw/
│   ├── ftse_daily.parquet              
│   └── nasdaq_daily.parquet
└── results/
    ├── ftse100/                        
    │   ├── Cluster_Bollinger_Sliding.parquet
    │   ├── Cluster_Z-Score_Sliding.parquet
    │   └── ...
    └── nasdaq100/
        └── ...
```

**MinIO Storage Layout**

The MinIO object storage organizes data in a hierarchical bucket structure that mirrors the analytical requirements of the backtesting system. Each market maintains its own namespace with dedicated areas for raw data and strategy results.

```
markets/                                
├── FTSE100/
│   ├── market_data.parquet            
│   └── strategies/
│       ├── strategy1.parquet          
│       └── strategy2.parquet
└── NASDAQ100/
    ├── market_data.parquet
    └── strategies/
        └── ...
```

Strategy files within MinIO include embedded metadata tags that classify the pair-finding algorithm (Clustering, Distance-based, Correlation), trading strategy type (Bollinger, Z-Score, Cointegration), and descriptive information for analysis workflows.

## Custom Markets

The system supports dynamic addition of new markets through configuration updates. Adding custom markets enables backtesting strategies across different geographical regions, market segments, or asset classes. The process requires preparing market data in the expected format and updating the central configuration to register the new market with the storage and analytical services.

To add new markets, update `config.yaml`:

```yaml
storage:
  markets:
    - name: SP500
      data_file: market_data.parquet
      data_path: /host-data/raw/sp500_daily.parquet
      strategies: []  # Initially empty, strategies added via notebook runs
```

Place corresponding data file in `./data/raw/` and restart services. The market data should follow the standardized schema with date indexing and symbol-based columns for OHLCV data. Once registered, the new market becomes available for strategy generation through the notebook runner and analysis through the Streamlit interface.

## Development

The containerized development environment supports real-time code changes and debugging across all services. Log aggregation and service introspection capabilities facilitate development workflows and system monitoring during strategy development and testing phases.

**Accessing Service Logs**

View real-time logs from any service to monitor system behavior and debug issues.

```bash
docker-compose logs -f [service-name]
```

**Rebuilding After Changes**

Rebuild and restart services after making code changes to the application.

```bash
docker-compose down
docker-compose up --build
```

**Direct Service Access**

Execute commands directly inside running containers for debugging and development tasks.

```bash
# Execute commands in running container
docker-compose exec analytics bash
docker-compose exec streamlit bash
```
