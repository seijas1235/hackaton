"""Tests for domain.usecases.create_collection_reminder module."""

from datetime import datetime
from unittest.mock import MagicMock
import pytest

from domain.usecases.create_collection_reminder import CreateCollectionReminderUC


@pytest.fixture
def mock_repo():
    """Create a mock repository."""
    repo = MagicMock()
    return repo


def test_create_collection_reminder_success(mock_repo):
    """Test CreateCollectionReminderUC creates reminder successfully."""
    mock_repo.create_agent_action.return_value = "action-123"
    
    uc = CreateCollectionReminderUC(mock_repo)
    action_id = uc.execute(
        customer_id="CUST001",
        performed_by="user@example.com",
        invoice_id="INV123",
        remind_date="2025-10-20",
    )
    
    assert action_id == "action-123"
    
    mock_repo.create_agent_action.assert_called_once()
    call_args = mock_repo.create_agent_action.call_args
    
    assert call_args.kwargs["action"] == "collection_reminder"
    assert call_args.kwargs["performed_by"] == "user@example.com"
    
    payload = call_args.kwargs["payload"]
    assert payload["customer_id"] == "CUST001"
    assert payload["invoice_id"] == "INV123"
    assert payload["remind_date"] == "2025-10-20"


def test_create_collection_reminder_without_invoice(mock_repo):
    """Test creating reminder without specific invoice."""
    mock_repo.create_agent_action.return_value = "action-456"
    
    uc = CreateCollectionReminderUC(mock_repo)
    action_id = uc.execute(
        customer_id="CUST002",
        performed_by="agent@example.com",
    )
    
    assert action_id == "action-456"
    
    call_args = mock_repo.create_agent_action.call_args
    payload = call_args.kwargs["payload"]
    
    assert payload["customer_id"] == "CUST002"
    assert "invoice_id" not in payload
    assert "remind_date" in payload  # Should have default


def test_create_collection_reminder_default_date(mock_repo):
    """Test reminder uses today's date by default."""
    mock_repo.create_agent_action.return_value = "action-789"
    
    today = datetime.utcnow().date().isoformat()
    
    uc = CreateCollectionReminderUC(mock_repo)
    action_id = uc.execute(
        customer_id="CUST003",
        performed_by="user@example.com",
    )
    
    call_args = mock_repo.create_agent_action.call_args
    payload = call_args.kwargs["payload"]
    
    assert payload["remind_date"] == today


def test_create_collection_reminder_empty_customer_id(mock_repo):
    """Test validation rejects empty customer_id."""
    uc = CreateCollectionReminderUC(mock_repo)
    
    with pytest.raises(ValueError, match="customer_id is required"):
        uc.execute(
            customer_id="",
            performed_by="user@example.com",
        )


def test_create_collection_reminder_whitespace_customer_id(mock_repo):
    """Test validation rejects whitespace-only customer_id."""
    uc = CreateCollectionReminderUC(mock_repo)
    
    with pytest.raises(ValueError, match="customer_id is required"):
        uc.execute(
            customer_id="   ",
            performed_by="user@example.com",
        )


def test_create_collection_reminder_empty_performed_by(mock_repo):
    """Test validation rejects empty performed_by."""
    uc = CreateCollectionReminderUC(mock_repo)
    
    with pytest.raises(ValueError, match="performed_by is required"):
        uc.execute(
            customer_id="CUST001",
            performed_by="",
        )


def test_create_collection_reminder_invalid_date_format(mock_repo):
    """Test validation rejects invalid date format."""
    uc = CreateCollectionReminderUC(mock_repo)
    
    with pytest.raises(ValueError, match="Invalid remind_date format"):
        uc.execute(
            customer_id="CUST001",
            performed_by="user@example.com",
            remind_date="10/20/2025",  # Wrong format
        )


def test_create_collection_reminder_strips_whitespace(mock_repo):
    """Test that whitespace is stripped from inputs."""
    mock_repo.create_agent_action.return_value = "action-999"
    
    uc = CreateCollectionReminderUC(mock_repo)
    uc.execute(
        customer_id="  CUST001  ",
        performed_by="  user@example.com  ",
        invoice_id="  INV123  ",
    )
    
    call_args = mock_repo.create_agent_action.call_args
    payload = call_args.kwargs["payload"]
    
    assert payload["customer_id"] == "CUST001"
    assert payload["invoice_id"] == "INV123"
    assert call_args.kwargs["performed_by"] == "user@example.com"


def test_create_collection_reminder_repository_error(mock_repo):
    """Test reminder creation propagates repository errors."""
    mock_repo.create_agent_action.side_effect = Exception("Database error")
    
    uc = CreateCollectionReminderUC(mock_repo)
    
    with pytest.raises(Exception, match="Database error"):
        uc.execute(
            customer_id="CUST001",
            performed_by="user@example.com",
        )


def test_create_collection_reminder_valid_iso_dates(mock_repo):
    """Test various valid ISO date formats."""
    mock_repo.create_agent_action.return_value = "action-000"
    
    uc = CreateCollectionReminderUC(mock_repo)
    
    # Should all succeed
    valid_dates = [
        "2025-10-20",
        "2025-12-31",
        "2024-01-01",
    ]
    
    for date_str in valid_dates:
        action_id = uc.execute(
            customer_id="CUST001",
            performed_by="user@example.com",
            remind_date=date_str,
        )
        assert action_id == "action-000"
