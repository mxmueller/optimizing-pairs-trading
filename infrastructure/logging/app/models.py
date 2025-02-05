from pydantic import BaseModel
from typing import Optional, Any, Dict, List
from enum import Enum
from datetime import datetime

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

class LogSource(str, Enum):
    AGENT = "agent"
    SYSTEM = "system"
    TRADING = "trading"
    API = "api"
    DATABASE = "database"
    PIPELINE = "pipeline"
    DATA_PROCESSOR = "data_processor"
    TRANSFORMER = "transformer"

class PipelineStage(str, Enum):
    INGESTION = "ingestion"
    TRANSFORMATION = "transformation"
    VALIDATION = "validation"
    ENRICHMENT = "enrichment"
    AGGREGATION = "aggregation"
    STORAGE = "storage"
    EXPORT = "export"

class PipelineStatus(str, Enum):
    STARTED = "started"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class BaseLog(BaseModel):
    source: LogSource
    level: LogLevel
    message: str
    trace_id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None

class PipelineLog(BaseLog):
    pipeline_id: str
    stage: PipelineStage
    status: PipelineStatus
    data_size: Optional[int] = None
    processing_time: Optional[float] = None
    input_type: Optional[str] = None
    output_type: Optional[str] = None
    batch_id: Optional[str] = None
    transformations_applied: Optional[List[str]] = None
    validation_results: Optional[Dict[str, Any]] = None
    error_details: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, float]] = None

class DataValidationLog(BaseLog):
    pipeline_id: str
    batch_id: str
    schema_version: Optional[str] = None
    validation_rules: Dict[str, Any]
    validation_results: Dict[str, Any]
    failed_records: Optional[int] = None
    total_records: Optional[int] = None
    error_samples: Optional[List[Dict[str, Any]]] = None

class DataTransformationLog(BaseLog):
    pipeline_id: str
    batch_id: str
    transformation_type: str
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    records_processed: Optional[int] = None
    transformation_details: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, float]] = None

class PipelineMetricsLog(BaseLog):
    pipeline_id: str
    batch_id: str
    stage: PipelineStage
    metrics: Dict[str, float]
    resource_usage: Optional[Dict[str, float]] = None
    throughput: Optional[float] = None
    latency: Optional[float] = None

class TradeLog(BaseLog):
    trade_id: Optional[str] = None
    trade_type: Optional[str] = None
    amount: Optional[float] = None
    symbol: Optional[str] = None

class ErrorLog(BaseLog):
    error_type: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    stack_trace: Optional[str] = None

class SystemLog(BaseLog):
    component: Optional[str] = None
    action: Optional[str] = None
    status: Optional[str] = None