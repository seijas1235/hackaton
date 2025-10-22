"""Tests for domain.usecases.get_kpis module."""

from unittest.mock import MagicMock
import pytest

from domain.usecases.get_kpis import GetKPIsUC


@pytest.fixture
def mock_repo():
    """Create a mock repository."""
    repo = MagicMock()
    return repo


def test_get_kpis_success(mock_repo):
    """Test GetKPIsUC returns KPI data successfully."""
    mock_repo.get_kpis.return_value = {
        "revenue": 150000.0,
        "gross_margin": 0.35,
        "ar_total": 45000.0,
        "ar_over_60": 12000.0,
    }
    
    uc = GetKPIsUC(mock_repo)
    result = uc.execute(period="last_30d")
    
    assert result["revenue"] == 150000.0
    assert result["gross_margin"] == 0.35
    assert result["ar_total"] == 45000.0
    assert result["ar_over_60"] == 12000.0
    
    mock_repo.get_kpis.assert_called_once_with("last_30d")


def test_get_kpis_default_period(mock_repo):
    """Test GetKPIsUC uses default period."""
    mock_repo.get_kpis.return_value = {
        "revenue": 100000.0,
        "gross_margin": 0.30,
        "ar_total": 30000.0,
        "ar_over_60": 8000.0,
    }
    
    uc = GetKPIsUC(mock_repo)
    result = uc.execute()  # No period specified
    
    assert result["revenue"] == 100000.0
    mock_repo.get_kpis.assert_called_once_with("last_30d")


def test_get_kpis_different_periods(mock_repo):
    """Test GetKPIsUC works with different period values."""
    mock_repo.get_kpis.return_value = {
        "revenue": 250000.0,
        "gross_margin": 0.40,
        "ar_total": 60000.0,
        "ar_over_60": 15000.0,
    }
    
    uc = GetKPIsUC(mock_repo)
    result = uc.execute(period="last_60d")
    
    assert result["revenue"] == 250000.0
    mock_repo.get_kpis.assert_called_once_with("last_60d")


def test_get_kpis_repository_error(mock_repo):
    """Test GetKPIsUC propagates repository errors."""
    mock_repo.get_kpis.side_effect = Exception("Database connection failed")
    
    uc = GetKPIsUC(mock_repo)
    
    with pytest.raises(Exception, match="Database connection failed"):
        uc.execute(period="last_30d")
