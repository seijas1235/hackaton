"""Use case: Create collection reminder action."""

from datetime import datetime
from typing import Any, Dict, Optional, Protocol

from loguru import logger


class ActionRepository(Protocol):
    """Protocol for agent action data access (dependency inversion)."""
    
    def create_agent_action(
        self,
        action: str,
        payload: Dict[str, Any],
        performed_by: str,
    ) -> str:
        """Create an agent action record."""
        ...


class CreateCollectionReminderUC:
    """Use case for creating collection reminder actions.
    
    Records a collection reminder action for overdue invoices.
    Follows SRP: single responsibility of creating collection reminders.
    """
    
    def __init__(self, repo: ActionRepository):
        """Initialize use case with repository.
        
        Args:
            repo: Repository implementing create_agent_action method
        """
        self.repo = repo
    
    def execute(
        self,
        customer_id: str,
        performed_by: str,
        invoice_id: Optional[str] = None,
        remind_date: Optional[str] = None,
    ) -> str:
        """Execute creation of collection reminder action.
        
        Args:
            customer_id: Customer identifier (required)
            performed_by: User/agent who performed action (from JWT sub)
            invoice_id: Specific invoice to remind about (optional)
            remind_date: Date to send reminder in ISO format (optional, defaults to today)
            
        Returns:
            action_id: Unique identifier for created action
            
        Raises:
            ValueError: If required parameters are invalid
            Exception: If repository access fails
        """
        logger.info(
            f"Executing CreateCollectionReminderUC for customer: {customer_id}, "
            f"invoice: {invoice_id or 'all'}"
        )
        
        # Validate required parameters
        if not customer_id or not customer_id.strip():
            raise ValueError("customer_id is required and cannot be empty")
        
        if not performed_by or not performed_by.strip():
            raise ValueError("performed_by is required and cannot be empty")
        
        # Default remind_date to today if not provided
        if not remind_date:
            remind_date = datetime.utcnow().date().isoformat()
        
        # Validate date format
        try:
            datetime.fromisoformat(remind_date)
        except ValueError:
            raise ValueError(f"Invalid remind_date format: {remind_date}. Expected ISO format (YYYY-MM-DD)")
        
        try:
            # Build payload
            payload = {
                "customer_id": customer_id.strip(),
                "remind_date": remind_date,
            }
            
            if invoice_id:
                payload["invoice_id"] = invoice_id.strip()
            
            # Create action via repository
            action_id = self.repo.create_agent_action(
                action="collection_reminder",
                payload=payload,
                performed_by=performed_by.strip(),
            )
            
            logger.info(
                f"Collection reminder created: action_id={action_id}, "
                f"customer={customer_id}, invoice={invoice_id or 'N/A'}"
            )
            
            return action_id
            
        except ValueError as e:
            logger.warning(f"Collection reminder validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to create collection reminder: {e}")
            raise
