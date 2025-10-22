"""Lambda handler: GET /agent/tools/anomalies

Detects anomalies in sales data using z-score analysis.
"""

from typing import Any, Dict, List

from pydantic import BaseModel, Field
from loguru import logger

from domain.usecases.detect_anomalies import DetectAnomaliesUC
from infra.dynamo_repo import DynamoRepo
from shared.auth import get_claims_from_event
from shared.responses import ok, bad_request, server_error
from shared.settings import get_settings


class AnomalyItem(BaseModel):
    """Model for individual anomaly."""
    
    date: str = Field(description="Date of anomaly")
    amount: float = Field(description="Sales amount")
    z_score: float = Field(description="Z-score value")
    deviation: str = Field(description="Deviation type: high or low")


class AnomaliesResponse(BaseModel):
    """Response model for anomaly detection."""
    
    period: str = Field(description="Period analyzed")
    total_days: int = Field(description="Number of days analyzed")
    mean_sales: float = Field(description="Average daily sales")
    std_dev: float = Field(description="Standard deviation")
    anomalies: List[AnomalyItem] = Field(description="List of detected anomalies")
    anomaly_count: int = Field(description="Number of anomalies detected")


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for anomaly detection.
    
    Query Parameters:
        period: Time period to analyze (e.g., "last_60d", "last_90d")
        threshold: Z-score threshold (optional, default: 2.0)
        
    Returns:
        API Gateway response with anomaly data
    """
    try:
        # Extract claims (for logging/audit)
        try:
            claims = get_claims_from_event(event)
            user_id = claims.get("sub", "unknown")
            logger.info(f"Anomaly detection request from user: {user_id}")
        except KeyError:
            logger.warning("No JWT claims found in request")
            user_id = "anonymous"
        
        # Parse query parameters
        params = event.get("queryStringParameters") or {}
        period = params.get("period", "last_60d")
        threshold_str = params.get("threshold", "2.0")
        
        try:
            threshold = float(threshold_str)
            if threshold <= 0:
                raise ValueError("Threshold must be positive")
        except ValueError as e:
            return bad_request(f"Invalid threshold parameter: {e}")
        
        logger.debug(f"Detecting anomalies for period: {period}, threshold: {threshold}")
        
        # Initialize repository and use case
        settings = get_settings()
        repo = DynamoRepo(
            table_name=settings.table_name,
            region=settings.aws_region or "us-east-1"
        )
        
        uc = DetectAnomaliesUC(repo, threshold=threshold)
        anomalies_data = uc.execute(period=period)
        
        # Validate response with Pydantic
        response_data = AnomaliesResponse(**anomalies_data)
        
        logger.info(
            f"Anomaly detection completed: {response_data.anomaly_count} "
            f"anomalies found in {response_data.total_days} days"
        )
        return ok(response_data.model_dump())
        
    except ValueError as e:
        logger.warning(f"Invalid request or insufficient data: {e}")
        return bad_request(str(e))
    except Exception as e:
        logger.error(f"Error detecting anomalies: {e}", exc_info=True)
        return server_error("Failed to detect anomalies")
