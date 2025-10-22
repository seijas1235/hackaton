"""Tests for domain.usecases.cashflow_forecast module."""

from unittest.mock import MagicMock
import pytest

from domain.usecases.cashflow_forecast import CashflowForecastUC


@pytest.fixture
def mock_repo():
    """Create a mock repository."""
    repo = MagicMock()
    return repo


def test_cashflow_forecast_success(mock_repo):
    """Test CashflowForecastUC calculates forecast correctly."""
    # Mock 60 days of sales with average of 5000/day
    sales_data = [
        {"date": f"2025-{i//30 + 1:02d}-{i%30 + 1:02d}", "amount": 5000.0}
        for i in range(60)
    ]
    mock_repo.get_sales_series.return_value = sales_data
    
    uc = CashflowForecastUC(mock_repo)
    result = uc.execute(horizon_days=30)
    
    assert result["forecast_days"] == 30
    assert result["average_daily_cashflow"] == 5000.0
    assert result["total_forecast"] == 150000.0  # 5000 * 30
    assert result["historical_period_days"] == 60
    
    mock_repo.get_sales_series.assert_called_once_with(days=60)


def test_cashflow_forecast_varying_sales(mock_repo):
    """Test forecast with varying sales amounts."""
    sales_data = [
        {"date": "2025-10-01", "amount": 4000.0},
        {"date": "2025-10-02", "amount": 5000.0},
        {"date": "2025-10-03", "amount": 6000.0},
    ]
    mock_repo.get_sales_series.return_value = sales_data
    
    uc = CashflowForecastUC(mock_repo)
    result = uc.execute(horizon_days=10)
    
    # Average: (4000 + 5000 + 6000) / 3 = 5000
    assert result["average_daily_cashflow"] == 5000.0
    assert result["total_forecast"] == 50000.0  # 5000 * 10


def test_cashflow_forecast_default_horizon(mock_repo):
    """Test forecast uses default horizon of 30 days."""
    sales_data = [{"date": f"2025-10-{i+1:02d}", "amount": 3000.0} for i in range(60)]
    mock_repo.get_sales_series.return_value = sales_data
    
    uc = CashflowForecastUC(mock_repo)
    result = uc.execute()  # No horizon specified
    
    assert result["forecast_days"] == 30
    assert result["total_forecast"] == 90000.0  # 3000 * 30


def test_cashflow_forecast_no_data(mock_repo):
    """Test forecast raises error with no historical data."""
    mock_repo.get_sales_series.return_value = []
    
    uc = CashflowForecastUC(mock_repo)
    
    with pytest.raises(ValueError, match="No historical sales data"):
        uc.execute(horizon_days=30)


def test_cashflow_forecast_repository_error(mock_repo):
    """Test forecast propagates repository errors."""
    mock_repo.get_sales_series.side_effect = Exception("Database error")
    
    uc = CashflowForecastUC(mock_repo)
    
    with pytest.raises(Exception, match="Database error"):
        uc.execute(horizon_days=30)


def test_cashflow_forecast_large_horizon(mock_repo):
    """Test forecast with large horizon uses appropriate lookback."""
    sales_data = [{"date": f"2025-{i//30 + 1:02d}-01", "amount": 10000.0} for i in range(120)]
    mock_repo.get_sales_series.return_value = sales_data
    
    uc = CashflowForecastUC(mock_repo)
    result = uc.execute(horizon_days=90)
    
    assert result["forecast_days"] == 90
    # Should request 180 days (2x horizon) or minimum 60
    mock_repo.get_sales_series.assert_called_once_with(days=180)
