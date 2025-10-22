"""Tests for adapter handlers (API Gateway Lambda functions)."""

import json
from unittest.mock import MagicMock, patch
import pytest

# Import handlers
from adapters.handlers import get_kpis, cashflow_forecast, detect_anomalies
from adapters.handlers import create_collection_reminder, list_actions, agent_chat


@pytest.fixture
def mock_event_with_claims():
    """Create a mock API Gateway event with JWT claims."""
    return {
        "requestContext": {
            "authorizer": {
                "jwt": {
                    "claims": {
                        "sub": "user@example.com",
                        "scope": "agent:read agent:actions",
                    }
                }
            }
        },
        "queryStringParameters": {},
    }


@pytest.fixture
def mock_context():
    """Create a mock Lambda context."""
    return MagicMock()


# Tests for get_kpis handler
@patch("adapters.handlers.get_kpis.DynamoRepo")
def test_get_kpis_success(mock_repo_class, mock_event_with_claims, mock_context):
    """Test get_kpis handler returns KPIs successfully."""
    mock_repo = MagicMock()
    mock_repo.get_kpis.return_value = {
        "revenue": 150000.0,
        "gross_margin": 0.35,
        "ar_total": 45000.0,
        "ar_over_60": 12000.0,
    }
    mock_repo_class.return_value = mock_repo
    
    mock_event_with_claims["queryStringParameters"] = {"period": "last_30d"}
    
    response = get_kpis.handler(mock_event_with_claims, mock_context)
    
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["revenue"] == 150000.0
    assert body["gross_margin"] == 0.35


@patch("adapters.handlers.get_kpis.DynamoRepo")
def test_get_kpis_default_period(mock_repo_class, mock_event_with_claims, mock_context):
    """Test get_kpis handler uses default period."""
    mock_repo = MagicMock()
    mock_repo.get_kpis.return_value = {
        "revenue": 100000.0,
        "gross_margin": 0.30,
        "ar_total": 30000.0,
        "ar_over_60": 8000.0,
    }
    mock_repo_class.return_value = mock_repo
    
    response = get_kpis.handler(mock_event_with_claims, mock_context)
    
    assert response["statusCode"] == 200
    mock_repo.get_kpis.assert_called_once()


# Tests for cashflow_forecast handler
@patch("adapters.handlers.cashflow_forecast.DynamoRepo")
def test_cashflow_forecast_success(mock_repo_class, mock_event_with_claims, mock_context):
    """Test cashflow_forecast handler returns forecast."""
    mock_repo = MagicMock()
    mock_repo.get_sales_series.return_value = [
        {"date": "2025-10-01", "amount": 5000.0} for _ in range(60)
    ]
    mock_repo_class.return_value = mock_repo
    
    mock_event_with_claims["queryStringParameters"] = {"horizon": "30"}
    
    response = cashflow_forecast.handler(mock_event_with_claims, mock_context)
    
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert "average_daily_cashflow" in body
    assert "total_forecast" in body


@patch("adapters.handlers.cashflow_forecast.DynamoRepo")
def test_cashflow_forecast_invalid_horizon(mock_repo_class, mock_event_with_claims, mock_context):
    """Test cashflow_forecast handler rejects invalid horizon."""
    mock_event_with_claims["queryStringParameters"] = {"horizon": "invalid"}
    
    response = cashflow_forecast.handler(mock_event_with_claims, mock_context)
    
    assert response["statusCode"] == 400


# Tests for detect_anomalies handler
@patch("adapters.handlers.detect_anomalies.DynamoRepo")
def test_detect_anomalies_success(mock_repo_class, mock_event_with_claims, mock_context):
    """Test detect_anomalies handler returns anomalies."""
    mock_repo = MagicMock()
    mock_repo.get_sales_series.return_value = [
        {"date": f"2025-10-{i+1:02d}", "amount": 5000.0} for i in range(30)
    ]
    mock_repo_class.return_value = mock_repo
    
    mock_event_with_claims["queryStringParameters"] = {"period": "last_60d"}
    
    response = detect_anomalies.handler(mock_event_with_claims, mock_context)
    
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert "anomalies" in body
    assert "anomaly_count" in body


@patch("adapters.handlers.detect_anomalies.DynamoRepo")
def test_detect_anomalies_custom_threshold(mock_repo_class, mock_event_with_claims, mock_context):
    """Test detect_anomalies handler with custom threshold."""
    mock_repo = MagicMock()
    mock_repo.get_sales_series.return_value = [
        {"date": f"2025-10-{i+1:02d}", "amount": 5000.0} for i in range(30)
    ]
    mock_repo_class.return_value = mock_repo
    
    mock_event_with_claims["queryStringParameters"] = {
        "period": "last_60d",
        "threshold": "1.5"
    }
    
    response = detect_anomalies.handler(mock_event_with_claims, mock_context)
    
    assert response["statusCode"] == 200


# Tests for create_collection_reminder handler
@patch("adapters.handlers.create_collection_reminder.DynamoRepo")
def test_create_collection_reminder_success(mock_repo_class, mock_event_with_claims, mock_context):
    """Test create_collection_reminder handler creates reminder."""
    mock_repo = MagicMock()
    mock_repo.create_agent_action.return_value = "action-123"
    mock_repo_class.return_value = mock_repo
    
    mock_event_with_claims["body"] = json.dumps({
        "customer_id": "CUST001",
        "invoice_id": "INV123",
        "remind_date": "2025-10-20"
    })
    
    response = create_collection_reminder.handler(mock_event_with_claims, mock_context)
    
    assert response["statusCode"] == 201
    body = json.loads(response["body"])
    assert body["action_id"] == "action-123"
    assert body["customer_id"] == "CUST001"


@patch("adapters.handlers.create_collection_reminder.DynamoRepo")
def test_create_collection_reminder_missing_scope(mock_repo_class, mock_context):
    """Test create_collection_reminder handler rejects without scope."""
    event_no_scope = {
        "requestContext": {
            "authorizer": {
                "jwt": {
                    "claims": {
                        "sub": "user@example.com",
                        "scope": "agent:read",  # Missing agent:actions
                    }
                }
            }
        },
        "body": json.dumps({"customer_id": "CUST001"}),
    }
    
    response = create_collection_reminder.handler(event_no_scope, mock_context)
    
    assert response["statusCode"] == 401


@patch("adapters.handlers.create_collection_reminder.DynamoRepo")
def test_create_collection_reminder_invalid_body(mock_repo_class, mock_event_with_claims, mock_context):
    """Test create_collection_reminder handler rejects invalid body."""
    mock_event_with_claims["body"] = json.dumps({"invalid": "data"})
    
    response = create_collection_reminder.handler(mock_event_with_claims, mock_context)
    
    assert response["statusCode"] == 400


# Tests for list_actions handler
@patch("adapters.handlers.list_actions.DynamoRepo")
def test_list_actions_success(mock_repo_class, mock_event_with_claims, mock_context):
    """Test list_actions handler returns actions."""
    mock_repo = MagicMock()
    mock_repo.list_agent_actions.return_value = [
        {
            "action_id": "123",
            "action": "collection_reminder",
            "payload": {"customer_id": "CUST001"},
            "performed_by": "user@example.com",
            "timestamp": "2025-10-16T10:00:00",
        }
    ]
    mock_repo_class.return_value = mock_repo
    
    response = list_actions.handler(mock_event_with_claims, mock_context)
    
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["count"] == 1
    assert len(body["actions"]) == 1


@patch("adapters.handlers.list_actions.DynamoRepo")
def test_list_actions_with_limit(mock_repo_class, mock_event_with_claims, mock_context):
    """Test list_actions handler with custom limit."""
    mock_repo = MagicMock()
    mock_repo.list_agent_actions.return_value = []
    mock_repo_class.return_value = mock_repo
    
    mock_event_with_claims["queryStringParameters"] = {"limit": "10"}
    
    response = list_actions.handler(mock_event_with_claims, mock_context)
    
    assert response["statusCode"] == 200
    mock_repo.list_agent_actions.assert_called_once_with(limit=10)


# Tests for agent_chat handler
@patch("adapters.handlers.agent_chat.boto3.client")
def test_agent_chat_mock_response(mock_boto_client, mock_event_with_claims, mock_context):
    """Test agent_chat handler returns mock response when not configured."""
    mock_event_with_claims["body"] = json.dumps({
        "message": "What are the KPIs?",
        "session_id": "test-session"
    })
    
    response = agent_chat.handler(mock_event_with_claims, mock_context)
    
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert "response" in body
    assert "session_id" in body


@patch("adapters.handlers.agent_chat.boto3.client")
def test_agent_chat_empty_message(mock_boto_client, mock_event_with_claims, mock_context):
    """Test agent_chat handler rejects empty message."""
    mock_event_with_claims["body"] = json.dumps({
        "message": "   ",
        "session_id": "test-session"
    })
    
    response = agent_chat.handler(mock_event_with_claims, mock_context)
    
    assert response["statusCode"] == 400


@patch("adapters.handlers.agent_chat.boto3.client")
def test_agent_chat_invalid_json(mock_boto_client, mock_event_with_claims, mock_context):
    """Test agent_chat handler rejects invalid JSON."""
    mock_event_with_claims["body"] = "invalid json"
    
    response = agent_chat.handler(mock_event_with_claims, mock_context)
    
    assert response["statusCode"] == 400
