"""Lambda handler: GET /agent/tools/cashflow

Forecasts cashflow for a specified horizon using historical sales data.
"""

from typing import Any, Dict

from pydantic import BaseModel, Field, validator
from loguru import logger

from domain.usecases.cashflow_forecast import CashflowForecastUC
from infra.dynamo_repo import DynamoRepo
from shared.auth import get_claims_from_event
from shared.responses import ok, bad_request, server_error
from shared.settings import get_settings


class CashflowForecastResponse(BaseModel):
    """Response model for cashflow forecast."""
    
    forecast_days: int = Field(description="Number of days forecasted")
    average_daily_cashflow: float = Field(description="Predicted daily cashflow")
    total_forecast: float = Field(description="Total predicted cashflow for horizon")
    historical_period_days: int = Field(description="Days of historical data used")


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for cashflow forecasting.
    
    Query Parameters:
        horizon: Number of days to forecast (default: 30)
        
    Returns:
        API Gateway response with forecast data
    """
    try:
        # Extract claims (for logging/audit)
        try:
            claims = get_claims_from_event(event)
            user_id = claims.get("sub", "unknown")
            logger.info(f"Cashflow forecast request from user: {user_id}")
        except KeyError:
            logger.warning("No JWT claims found in request")
            user_id = "anonymous"
        
        # Parse query parameters
        params = event.get("queryStringParameters") or {}
        horizon_str = params.get("horizon", "30")
        
        try:
            horizon_days = int(horizon_str)
            if horizon_days <= 0:
                raise ValueError("Horizon must be positive")
            if horizon_days > 365:
                raise ValueError("Horizon cannot exceed 365 days")
        except ValueError as e:
            return bad_request(f"Invalid horizon parameter: {e}")
        
        logger.debug(f"Forecasting cashflow for {horizon_days} days")
        
        # Initialize repository and use case
        settings = get_settings()
        repo = DynamoRepo(
            table_name=settings.table_name,
            region=settings.aws_region or "us-east-1"
        )
        
        uc = CashflowForecastUC(repo)
        forecast = uc.execute(horizon_days=horizon_days)
        
        # Validate response with Pydantic
        response_data = CashflowForecastResponse(**forecast)
        
        logger.info(f"Cashflow forecast completed: {horizon_days} days")
        return ok(response_data.model_dump())
        
    except ValueError as e:
        logger.warning(f"Invalid request or insufficient data: {e}")
        return bad_request(str(e))
    except Exception as e:
        logger.error(f"Error forecasting cashflow: {e}", exc_info=True)
        return server_error("Failed to forecast cashflow")
