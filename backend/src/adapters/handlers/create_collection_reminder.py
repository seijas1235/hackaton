"""Lambda handler: POST /agent/actions/collection-reminder

Creates a collection reminder action for overdue invoices.
Requires agent:actions scope.
"""

import json
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator
from loguru import logger

from domain.usecases.create_collection_reminder import CreateCollectionReminderUC
from infra.dynamo_repo import DynamoRepo
from shared.auth import get_claims_from_event, require_scope
from shared.responses import ok, bad_request, server_error
from shared.settings import get_settings


class CreateReminderRequest(BaseModel):
    """Request model for creating collection reminder."""
    
    customer_id: str = Field(description="Customer identifier")
    invoice_id: Optional[str] = Field(default=None, description="Specific invoice ID (optional)")
    remind_date: Optional[str] = Field(default=None, description="Date to send reminder (ISO format)")
    
    @field_validator("customer_id")
    @classmethod
    def customer_id_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("customer_id cannot be empty")
        return v.strip()
    
    @field_validator("invoice_id")
    @classmethod
    def invoice_id_strip(cls, v):
        if v:
            return v.strip()
        return v
    
    @field_validator("remind_date")
    @classmethod
    def remind_date_strip(cls, v):
        if v:
            return v.strip()
        return v


class CreateReminderResponse(BaseModel):
    """Response model for created reminder."""
    
    action_id: str = Field(description="Unique action identifier")
    action: str = Field(default="collection_reminder", description="Action type")
    customer_id: str = Field(description="Customer identifier")
    invoice_id: Optional[str] = Field(default=None, description="Invoice identifier")
    remind_date: str = Field(description="Reminder date")
    performed_by: str = Field(description="User who created the action")


@require_scope("agent:actions")
def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for creating collection reminders.
    
    Requires JWT scope: agent:actions
    
    Request Body:
        {
            "customer_id": "CUST001",
            "invoice_id": "INV123",  // optional
            "remind_date": "2025-10-20"  // optional, defaults to today
        }
        
    Returns:
        API Gateway response with created action details
    """
    try:
        # Extract claims
        claims = get_claims_from_event(event)
        user_id = claims.get("sub", "unknown")
        logger.info(f"Collection reminder creation request from user: {user_id}")
        
        # Parse request body
        body = event.get("body", "{}")
        if isinstance(body, str):
            body = json.loads(body)
        
        # Validate request with Pydantic
        try:
            request_data = CreateReminderRequest(**body)
        except Exception as e:
            return bad_request(f"Invalid request body: {e}")
        
        logger.debug(
            f"Creating reminder for customer: {request_data.customer_id}, "
            f"invoice: {request_data.invoice_id or 'all'}"
        )
        
        # Initialize repository and use case
        settings = get_settings()
        repo = DynamoRepo(
            table_name=settings.table_name,
            region=settings.aws_region or "us-east-1"
        )
        
        uc = CreateCollectionReminderUC(repo)
        action_id = uc.execute(
            customer_id=request_data.customer_id,
            performed_by=user_id,
            invoice_id=request_data.invoice_id,
            remind_date=request_data.remind_date,
        )
        
        # Build response
        response_data = CreateReminderResponse(
            action_id=action_id,
            customer_id=request_data.customer_id,
            invoice_id=request_data.invoice_id,
            remind_date=request_data.remind_date or "",  # UC sets default
            performed_by=user_id,
        )
        
        logger.info(f"Collection reminder created: action_id={action_id}")
        return ok(response_data.model_dump(), status_code=201)
        
    except ValueError as e:
        logger.warning(f"Invalid request data: {e}")
        return bad_request(str(e))
    except json.JSONDecodeError as e:
        logger.warning(f"Invalid JSON in request body: {e}")
        return bad_request("Invalid JSON in request body")
    except Exception as e:
        logger.error(f"Error creating collection reminder: {e}", exc_info=True)
        return server_error("Failed to create collection reminder")
