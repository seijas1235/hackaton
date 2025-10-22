"""Lambda handler: GET /agent/tools/kpis

Retrieves key performance indicators for a specified period.
"""

from typing import Any, Dict

from pydantic import BaseModel, Field
from loguru import logger

from domain.usecases.get_kpis import GetKPIsUC
from infra.dynamo_repo import DynamoRepo
from shared.auth import get_claims_from_event
from shared.responses import ok, bad_request, server_error
from shared.settings import get_settings


class KPIResponse(BaseModel):
    """Response model for KPI data."""
    
    revenue: float = Field(description="Total revenue")
    gross_margin: float = Field(description="Gross margin percentage")
    ar_total: float = Field(description="Total accounts receivable")
    ar_over_60: float = Field(description="AR aged over 60 days")


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for getting KPIs.
    
    Query Parameters:
        period: Time period (e.g., "last_30d", "last_60d", "last_90d")
        
    Returns:
        API Gateway response with KPI data
    """
    try:
        # Extract claims (for logging/audit)
        try:
            claims = get_claims_from_event(event)
            user_id = claims.get("sub", "unknown")
            logger.info(f"KPI request from user: {user_id}")
        except KeyError:
            logger.warning("No JWT claims found in request")
            user_id = "anonymous"
        
        # Parse query parameters
        params = event.get("queryStringParameters") or {}
        period = params.get("period", "last_30d")
        
        logger.debug(f"Fetching KPIs for period: {period}")
        
        # Initialize repository and use case
        settings = get_settings()
        repo = DynamoRepo(
            table_name=settings.table_name,
            region=settings.aws_region or "us-east-1"
        )
        
        uc = GetKPIsUC(repo)
        kpis = uc.execute(period=period)
        
        # Validate response with Pydantic
        response_data = KPIResponse(**kpis)
        
        logger.info(f"KPIs retrieved successfully for period {period}")
        return ok(response_data.model_dump())
        
    except ValueError as e:
        logger.warning(f"Invalid request parameters: {e}")
        return bad_request(str(e))
    except Exception as e:
        logger.error(f"Error retrieving KPIs: {e}", exc_info=True)
        return server_error("Failed to retrieve KPIs")
