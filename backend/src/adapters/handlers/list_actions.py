"""Lambda handler: GET /agent/actions

Lists recent agent actions with optional limit.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from loguru import logger

from infra.dynamo_repo import DynamoRepo
from shared.auth import get_claims_from_event
from shared.responses import ok, bad_request, server_error
from shared.settings import get_settings


class AgentAction(BaseModel):
    """Model for individual agent action."""
    
    action_id: Optional[str] = Field(description="Action identifier")
    action: Optional[str] = Field(description="Action type")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Action payload")
    performed_by: Optional[str] = Field(description="User who performed action")
    timestamp: Optional[str] = Field(description="Timestamp of action")


class ListActionsResponse(BaseModel):
    """Response model for listing actions."""
    
    actions: List[AgentAction] = Field(description="List of agent actions")
    count: int = Field(description="Number of actions returned")


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for listing agent actions.
    
    Query Parameters:
        limit: Maximum number of actions to return (default: 50, max: 100)
        
    Returns:
        API Gateway response with list of actions
    """
    try:
        # Extract claims (for logging/audit)
        try:
            claims = get_claims_from_event(event)
            user_id = claims.get("sub", "unknown")
            logger.info(f"List actions request from user: {user_id}")
        except KeyError:
            logger.warning("No JWT claims found in request")
            user_id = "anonymous"
        
        # Parse query parameters
        params = event.get("queryStringParameters") or {}
        limit_str = params.get("limit", "50")
        
        try:
            limit = int(limit_str)
            if limit <= 0:
                raise ValueError("Limit must be positive")
            if limit > 100:
                limit = 100  # Cap at 100
        except ValueError as e:
            return bad_request(f"Invalid limit parameter: {e}")
        
        logger.debug(f"Listing agent actions with limit: {limit}")
        
        # Initialize repository
        settings = get_settings()
        repo = DynamoRepo(
            table_name=settings.table_name,
            region=settings.aws_region or "us-east-1"
        )
        
        # Get actions
        actions = repo.list_agent_actions(limit=limit)
        
        # Validate response with Pydantic
        response_data = ListActionsResponse(
            actions=[AgentAction(**action) for action in actions],
            count=len(actions),
        )
        
        logger.info(f"Listed {response_data.count} agent actions")
        return ok(response_data.model_dump())
        
    except ValueError as e:
        logger.warning(f"Invalid request parameters: {e}")
        return bad_request(str(e))
    except Exception as e:
        logger.error(f"Error listing agent actions: {e}", exc_info=True)
        return server_error("Failed to list agent actions")
