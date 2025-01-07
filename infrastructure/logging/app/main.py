from fastapi import FastAPI, HTTPException
from fluent import sender
import uuid
from datetime import datetime
from typing import Union
import logging
from models import TradeLog, ErrorLog, SystemLog, LogLevel, LogSource

# FastAPI app setup
app = FastAPI()

# Fluentd logger setup
FLUENTD_TAG = "trading.logs"
logger = sender.FluentSender(FLUENTD_TAG, host='fluentd', port=24224)


def create_structured_log(log: Union[TradeLog, ErrorLog, SystemLog]):
    base_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "trace_id": log.trace_id or str(uuid.uuid4()),
        "source": log.source,
        "level": log.level,
        "message": log.message,
        "user_id": log.user_id,
    }

    if isinstance(log, TradeLog):
        base_data.update({
            "event_type": "trade",
            "trade_id": log.trade_id,
            "trade_type": log.trade_type,
            "amount": log.amount,
            "symbol": log.symbol
        })
    elif isinstance(log, ErrorLog):
        base_data.update({
            "event_type": "error",
            "error_type": log.error_type,
            "error_details": log.error_details,
            "stack_trace": log.stack_trace
        })
    elif isinstance(log, SystemLog):
        base_data.update({
            "event_type": "system",
            "component": log.component,
            "action": log.action,
            "status": log.status
        })

    if log.metadata:
        base_data["metadata"] = log.metadata

    return base_data


@app.post("/log")
async def create_log(log: Union[TradeLog, ErrorLog, SystemLog]):
    """Hauptendpunkt für Log-Erstellung"""
    try:
        structured_log = create_structured_log(log)

        if not logger.emit(None, structured_log):
            raise HTTPException(status_code=500, detail="Failed to send log to Fluentd")

        return {"status": "success", "trace_id": structured_log["trace_id"]}

    except Exception as e:
        # System-Error logging
        error_log = ErrorLog(
            source=LogSource.SYSTEM,
            level=LogLevel.ERROR,
            message=f"Failed to process log: {str(e)}",
            error_type=type(e).__name__,
            error_details={"original_log": log.dict()}
        )
        logger.emit(None, create_structured_log(error_log))
        raise HTTPException(status_code=500, detail="Failed to process log")


@app.post("/trade")
async def log_trade(trade: TradeLog):
    """Spezifischer Endpunkt für Trade-Logs"""
    try:
        structured_log = create_structured_log(trade)

        if not logger.emit(None, structured_log):
            raise HTTPException(status_code=500, detail="Failed to send trade log to Fluentd")

        return {"status": "success", "trade_id": trade.trade_id, "trace_id": structured_log["trace_id"]}

    except Exception as e:
        error_log = ErrorLog(
            source=LogSource.TRADING,
            level=LogLevel.ERROR,
            message=f"Failed to log trade: {str(e)}",
            error_type=type(e).__name__,
            error_details={"trade_data": trade.dict()}
        )
        logger.emit(None, create_structured_log(error_log))
        raise HTTPException(status_code=500, detail="Failed to log trade")


@app.get("/health")
async def health_check():
    health_log = SystemLog(
        source=LogSource.SYSTEM,
        level=LogLevel.INFO,
        message="Health check performed",
        component="api",
        action="health_check",
        status="active"
    )
    structured_log = create_structured_log(health_log)
    logger.emit(None, structured_log)
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)