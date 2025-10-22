"""Tests for tools.seed_data module."""

from unittest.mock import MagicMock, patch, call
import pytest

from tools.seed_data import (
    generate_customers,
    generate_sales,
    generate_kpis,
    generate_actions,
    batch_write_items,
)


def test_generate_customers():
    """Test customer generation creates correct structure."""
    customers = generate_customers(count=5)
    
    assert len(customers) == 5
    
    for customer in customers:
        assert customer["pk"].startswith("AR_AGING#CUST")
        assert "customer_id" in customer
        assert "customer_name" in customer
        assert "current" in customer
        assert "days_30" in customer
        assert "days_60" in customer
        assert "days_90" in customer
        assert "days_over_90" in customer
        assert "total" in customer
        
        # Verify total is sum of aging buckets
        total = (
            customer["current"] + customer["days_30"] + 
            customer["days_60"] + customer["days_90"] + 
            customer["days_over_90"]
        )
        assert customer["total"] == total


def test_generate_sales():
    """Test sales generation creates correct structure."""
    sales = generate_sales(days=10)
    
    assert len(sales) == 10
    
    for sale in sales:
        assert sale["pk"].startswith("SALES#")
        assert "date" in sale
        assert "amount" in sale
        assert sale["amount"] > 0


def test_generate_sales_chronological():
    """Test sales are generated in chronological order."""
    sales = generate_sales(days=5)
    
    dates = [sale["date"] for sale in sales]
    assert dates == sorted(dates)  # Should be in ascending order


def test_generate_kpis():
    """Test KPI generation creates correct structure."""
    kpis = generate_kpis()
    
    assert len(kpis) == 3
    
    periods = {kpi["period"] for kpi in kpis}
    assert "last_30d" in periods
    assert "last_60d" in periods
    assert "last_90d" in periods
    
    for kpi in kpis:
        assert kpi["pk"].startswith("KPI#")
        assert "revenue" in kpi
        assert "gross_margin" in kpi
        assert "ar_total" in kpi
        assert "ar_over_60" in kpi


def test_generate_actions():
    """Test action generation creates correct structure."""
    actions = generate_actions(count=5)
    
    assert len(actions) == 5
    
    for action in actions:
        assert action["pk"].startswith("ACTION#")
        assert "action_id" in action
        assert "action" in action
        assert "payload" in action
        assert "performed_by" in action
        assert "timestamp" in action
        assert "created_at" in action


@patch("tools.seed_data.boto3.resource")
def test_batch_write_items_success(mock_boto_resource):
    """Test batch_write_items writes items successfully."""
    mock_table = MagicMock()
    mock_dynamodb = MagicMock()
    mock_dynamodb.Table.return_value = mock_table
    mock_boto_resource.return_value = mock_dynamodb
    
    # Create mock batch writer context manager
    mock_writer = MagicMock()
    mock_table.batch_writer.return_value.__enter__.return_value = mock_writer
    mock_table.batch_writer.return_value.__exit__.return_value = None
    
    items = [
        {"pk": "TEST#1", "data": "item1"},
        {"pk": "TEST#2", "data": "item2"},
    ]
    
    batch_write_items("test-table", "us-east-1", items)
    
    # Verify boto3.resource was called
    mock_boto_resource.assert_called_once_with("dynamodb", region_name="us-east-1")
    
    # Verify table was accessed
    mock_dynamodb.Table.assert_called_once_with("test-table")
    
    # Verify items were written
    assert mock_writer.put_item.call_count == 2


@patch("tools.seed_data.boto3.resource")
def test_batch_write_items_large_batch(mock_boto_resource):
    """Test batch_write_items handles batches > 25 items."""
    mock_table = MagicMock()
    mock_dynamodb = MagicMock()
    mock_dynamodb.Table.return_value = mock_table
    mock_boto_resource.return_value = mock_dynamodb
    
    mock_writer = MagicMock()
    mock_table.batch_writer.return_value.__enter__.return_value = mock_writer
    mock_table.batch_writer.return_value.__exit__.return_value = None
    
    # Create 30 items (should be split into 2 batches)
    items = [{"pk": f"TEST#{i}", "data": f"item{i}"} for i in range(30)]
    
    batch_write_items("test-table", "us-east-1", items)
    
    # Should write all 30 items
    assert mock_writer.put_item.call_count == 30
    
    # Should call batch_writer twice (2 batches)
    assert mock_table.batch_writer.call_count == 2


def test_generate_customers_unique_ids():
    """Test that customer IDs are unique."""
    customers = generate_customers(count=50)
    
    customer_ids = [c["customer_id"] for c in customers]
    assert len(customer_ids) == len(set(customer_ids))  # All unique


def test_generate_actions_realistic_timestamps():
    """Test that action timestamps are within expected range."""
    from datetime import datetime, timedelta
    
    actions = generate_actions(count=10)
    
    now = datetime.utcnow()
    thirty_days_ago = now - timedelta(days=30)
    
    for action in actions:
        timestamp = datetime.fromisoformat(action["timestamp"])
        assert thirty_days_ago <= timestamp <= now
