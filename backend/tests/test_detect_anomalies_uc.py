"""Tests for domain.usecases.detect_anomalies module."""

from unittest.mock import MagicMock
import pytest

from domain.usecases.detect_anomalies import DetectAnomaliesUC


@pytest.fixture
def mock_repo():
    """Create a mock repository."""
    repo = MagicMock()
    return repo


def test_detect_anomalies_with_outliers(mock_repo):
    """Test anomaly detection finds outliers correctly."""
    # Normal sales around 5000, with one high outlier and one low outlier
    sales_data = [
        {"date": "2025-10-01", "amount": 5000.0},
        {"date": "2025-10-02", "amount": 5100.0},
        {"date": "2025-10-03", "amount": 4900.0},
        {"date": "2025-10-04", "amount": 5000.0},
        {"date": "2025-10-05", "amount": 10000.0},  # High anomaly
        {"date": "2025-10-06", "amount": 1000.0},   # Low anomaly
        {"date": "2025-10-07", "amount": 5000.0},
    ]
    mock_repo.get_sales_series.return_value = sales_data
    
    # Use lower threshold since outliers affect std dev
    uc = DetectAnomaliesUC(mock_repo, threshold=1.5)
    result = uc.execute(period="last_60d")
    
    assert result["period"] == "last_60d"
    assert result["total_days"] == 7
    assert result["anomaly_count"] == 2
    assert len(result["anomalies"]) == 2
    
    # Check high anomaly
    high_anomaly = next(a for a in result["anomalies"] if a["date"] == "2025-10-05")
    assert high_anomaly["amount"] == 10000.0
    assert high_anomaly["deviation"] == "high"
    
    # Check low anomaly
    low_anomaly = next(a for a in result["anomalies"] if a["date"] == "2025-10-06")
    assert low_anomaly["amount"] == 1000.0
    assert low_anomaly["deviation"] == "low"


def test_detect_anomalies_no_outliers(mock_repo):
    """Test anomaly detection with no outliers."""
    # All sales very similar
    sales_data = [
        {"date": f"2025-10-{i+1:02d}", "amount": 5000.0 + (i * 10)}
        for i in range(30)
    ]
    mock_repo.get_sales_series.return_value = sales_data
    
    uc = DetectAnomaliesUC(mock_repo, threshold=2.0)
    result = uc.execute(period="last_60d")
    
    assert result["total_days"] == 30
    assert result["anomaly_count"] == 0
    assert result["anomalies"] == []


def test_detect_anomalies_all_same_values(mock_repo):
    """Test anomaly detection when all values are identical."""
    sales_data = [
        {"date": f"2025-10-{i+1:02d}", "amount": 5000.0}
        for i in range(30)
    ]
    mock_repo.get_sales_series.return_value = sales_data
    
    uc = DetectAnomaliesUC(mock_repo, threshold=2.0)
    result = uc.execute(period="last_60d")
    
    assert result["total_days"] == 30
    assert result["std_dev"] == 0.0
    assert result["anomaly_count"] == 0


def test_detect_anomalies_insufficient_data(mock_repo):
    """Test anomaly detection with insufficient data."""
    mock_repo.get_sales_series.return_value = [
        {"date": "2025-10-01", "amount": 5000.0}
    ]
    
    uc = DetectAnomaliesUC(mock_repo, threshold=2.0)
    
    with pytest.raises(ValueError, match="Insufficient data"):
        uc.execute(period="last_60d")


def test_detect_anomalies_custom_threshold(mock_repo):
    """Test anomaly detection with custom threshold."""
    sales_data = [
        {"date": "2025-10-01", "amount": 5000.0},
        {"date": "2025-10-02", "amount": 5000.0},
        {"date": "2025-10-03", "amount": 7000.0},  # Moderate outlier
    ]
    mock_repo.get_sales_series.return_value = sales_data
    
    # With high threshold, no anomalies
    uc_high = DetectAnomaliesUC(mock_repo, threshold=5.0)
    result_high = uc_high.execute(period="last_60d")
    assert result_high["anomaly_count"] == 0
    
    # With low threshold, finds anomaly
    uc_low = DetectAnomaliesUC(mock_repo, threshold=0.5)
    result_low = uc_low.execute(period="last_60d")
    assert result_low["anomaly_count"] >= 1


def test_detect_anomalies_period_parsing(mock_repo):
    """Test period string parsing extracts correct number of days."""
    sales_data = [
        {"date": f"2025-09-{i+1:02d}", "amount": 5000.0}
        for i in range(90)
    ]
    mock_repo.get_sales_series.return_value = sales_data
    
    uc = DetectAnomaliesUC(mock_repo)
    result = uc.execute(period="last_90d")
    
    mock_repo.get_sales_series.assert_called_once_with(days=90)


def test_detect_anomalies_repository_error(mock_repo):
    """Test anomaly detection propagates repository errors."""
    mock_repo.get_sales_series.side_effect = Exception("Database error")
    
    uc = DetectAnomaliesUC(mock_repo)
    
    with pytest.raises(Exception, match="Database error"):
        uc.execute(period="last_60d")


def test_detect_anomalies_sorted_by_significance(mock_repo):
    """Test anomalies are sorted by absolute z-score."""
    sales_data = [
        {"date": "2025-10-01", "amount": 5000.0},
        {"date": "2025-10-02", "amount": 5000.0},
        {"date": "2025-10-03", "amount": 5000.0},
        {"date": "2025-10-04", "amount": 5000.0},
        {"date": "2025-10-05", "amount": 8000.0},   # z-score ~2.2
        {"date": "2025-10-06", "amount": 12000.0},  # z-score ~5.3 (most significant)
        {"date": "2025-10-07", "amount": 2000.0},   # z-score ~-2.2
    ]
    mock_repo.get_sales_series.return_value = sales_data
    
    # Use lower threshold to detect these outliers
    uc = DetectAnomaliesUC(mock_repo, threshold=1.0)
    result = uc.execute(period="last_60d")
    
    anomalies = result["anomalies"]
    assert len(anomalies) >= 2
    
    # First anomaly should have highest absolute z-score
    z_scores = [abs(a["z_score"]) for a in anomalies]
    assert z_scores == sorted(z_scores, reverse=True)
