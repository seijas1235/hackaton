"""Tests for infra.dynamo_repo module."""

from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch
import pytest

from botocore.exceptions import ClientError
from infra.dynamo_repo import DynamoRepo


@pytest.fixture
def mock_table():
    """Create a mock DynamoDB table."""
    table = MagicMock()
    return table


@pytest.fixture
def repo(mock_table):
    """Create a DynamoRepo instance with mocked table."""
    with patch("infra.dynamo_repo.boto3.resource") as mock_resource:
        mock_dynamodb = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_resource.return_value = mock_dynamodb
        
        repo = DynamoRepo(table_name="test-table", region="us-east-1")
        return repo


def test_dynamo_repo_initialization(repo):
    """Test DynamoRepo initializes correctly."""
    assert repo.table_name == "test-table"
    assert repo.region == "us-east-1"
    assert repo.table is not None


def test_get_kpis_success(repo, mock_table):
    """Test get_kpis returns KPI data."""
    mock_table.get_item.return_value = {
        "Item": {
            "pk": "KPI#last_30d",
            "revenue": Decimal("150000.50"),
            "gross_margin": Decimal("0.35"),
            "ar_total": Decimal("45000.00"),
            "ar_over_60": Decimal("12000.00"),
        }
    }
    
    kpis = repo.get_kpis("last_30d")
    
    assert kpis["revenue"] == 150000.50
    assert kpis["gross_margin"] == 0.35
    assert kpis["ar_total"] == 45000.00
    assert kpis["ar_over_60"] == 12000.00
    
    mock_table.get_item.assert_called_once_with(Key={"pk": "KPI#last_30d"})


def test_get_kpis_not_found(repo, mock_table):
    """Test get_kpis returns defaults when KPI not found."""
    mock_table.get_item.return_value = {}
    
    kpis = repo.get_kpis("last_30d")
    
    assert kpis["revenue"] == 0.0
    assert kpis["gross_margin"] == 0.0
    assert kpis["ar_total"] == 0.0
    assert kpis["ar_over_60"] == 0.0


def test_get_kpis_client_error(repo, mock_table):
    """Test get_kpis raises ClientError on DynamoDB error."""
    mock_table.get_item.side_effect = ClientError(
        {"Error": {"Code": "ResourceNotFoundException", "Message": "Table not found"}},
        "GetItem"
    )
    
    with pytest.raises(ClientError):
        repo.get_kpis("last_30d")


def test_get_sales_series_success(repo, mock_table):
    """Test get_sales_series returns sales data."""
    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)
    
    mock_table.scan.return_value = {
        "Items": [
            {
                "pk": f"SALES#{today.isoformat()}",
                "amount": Decimal("5000.00"),
            },
            {
                "pk": f"SALES#{yesterday.isoformat()}",
                "amount": Decimal("4500.00"),
            },
        ]
    }
    
    sales = repo.get_sales_series(days=7)
    
    assert len(sales) == 2
    # Should be sorted by date
    assert sales[0]["date"] == yesterday.isoformat()
    assert sales[0]["amount"] == 4500.00
    assert sales[1]["date"] == today.isoformat()
    assert sales[1]["amount"] == 5000.00


def test_get_sales_series_empty(repo, mock_table):
    """Test get_sales_series returns empty list when no data."""
    mock_table.scan.return_value = {"Items": []}
    
    sales = repo.get_sales_series(days=30)
    
    assert sales == []


def test_get_ar_aging_success(repo, mock_table):
    """Test get_ar_aging returns aging data."""
    mock_table.scan.return_value = {
        "Items": [
            {
                "pk": "AR_AGING#CUST001",
                "customer_name": "Acme Corp",
                "current": Decimal("10000"),
                "days_30": Decimal("5000"),
                "days_60": Decimal("2000"),
                "days_90": Decimal("1000"),
                "days_over_90": Decimal("500"),
                "total": Decimal("18500"),
            },
            {
                "pk": "AR_AGING#CUST002",
                "customer_name": "TechCo",
                "current": Decimal("8000"),
                "days_30": Decimal("3000"),
                "days_60": Decimal("0"),
                "days_90": Decimal("0"),
                "days_over_90": Decimal("0"),
                "total": Decimal("11000"),
            },
        ]
    }
    
    ar_aging = repo.get_ar_aging()
    
    assert len(ar_aging) == 2
    assert ar_aging[0]["customer_id"] == "CUST001"
    assert ar_aging[0]["customer_name"] == "Acme Corp"
    assert ar_aging[0]["total"] == 18500.0
    assert ar_aging[1]["customer_id"] == "CUST002"
    assert ar_aging[1]["customer_name"] == "TechCo"


def test_get_ar_aging_empty(repo, mock_table):
    """Test get_ar_aging returns empty list when no data."""
    mock_table.scan.return_value = {"Items": []}
    
    ar_aging = repo.get_ar_aging()
    
    assert ar_aging == []


def test_create_agent_action_success(repo, mock_table):
    """Test create_agent_action creates action record."""
    action_id = repo.create_agent_action(
        action="collection_reminder",
        payload={"customer_id": "CUST001", "invoice_id": "INV123"},
        performed_by="user@example.com",
    )
    
    assert isinstance(action_id, str)
    assert len(action_id) == 36  # UUID format
    
    mock_table.put_item.assert_called_once()
    call_args = mock_table.put_item.call_args
    item = call_args.kwargs["Item"]
    
    assert item["pk"] == f"ACTION#{action_id}"
    assert item["action"] == "collection_reminder"
    assert item["performed_by"] == "user@example.com"
    assert "timestamp" in item


def test_create_agent_action_client_error(repo, mock_table):
    """Test create_agent_action raises ClientError on DynamoDB error."""
    mock_table.put_item.side_effect = ClientError(
        {"Error": {"Code": "ValidationException", "Message": "Invalid item"}},
        "PutItem"
    )
    
    with pytest.raises(ClientError):
        repo.create_agent_action(
            action="test_action",
            payload={},
            performed_by="user",
        )


def test_list_agent_actions_success(repo, mock_table):
    """Test list_agent_actions returns action list."""
    mock_table.scan.return_value = {
        "Items": [
            {
                "pk": "ACTION#123",
                "action_id": "123",
                "action": "collection_reminder",
                "payload": {"customer_id": "CUST001"},
                "performed_by": "user1",
                "timestamp": "2025-10-16T10:00:00",
            },
            {
                "pk": "ACTION#456",
                "action_id": "456",
                "action": "payment_plan",
                "payload": {"customer_id": "CUST002"},
                "performed_by": "user2",
                "timestamp": "2025-10-16T11:00:00",
            },
        ]
    }
    
    actions = repo.list_agent_actions(limit=50)
    
    assert len(actions) == 2
    # Should be sorted by timestamp descending
    assert actions[0]["action_id"] == "456"
    assert actions[0]["timestamp"] == "2025-10-16T11:00:00"
    assert actions[1]["action_id"] == "123"


def test_list_agent_actions_with_limit(repo, mock_table):
    """Test list_agent_actions respects limit parameter."""
    # Create 10 mock actions
    items = []
    for i in range(10):
        items.append({
            "pk": f"ACTION#{i}",
            "action_id": str(i),
            "action": "test",
            "payload": {},
            "performed_by": "user",
            "timestamp": f"2025-10-16T{i:02d}:00:00",
        })
    
    mock_table.scan.return_value = {"Items": items}
    
    actions = repo.list_agent_actions(limit=5)
    
    assert len(actions) == 5
    # Should return most recent (sorted descending)
    assert actions[0]["action_id"] == "9"


def test_list_agent_actions_empty(repo, mock_table):
    """Test list_agent_actions returns empty list when no actions."""
    mock_table.scan.return_value = {"Items": []}
    
    actions = repo.list_agent_actions()
    
    assert actions == []
