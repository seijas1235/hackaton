"""Use case: Detect anomalies in sales using z-score analysis."""

from statistics import mean, stdev
from typing import Any, Dict, List, Protocol

from loguru import logger


class SalesRepository(Protocol):
    """Protocol for sales data access (dependency inversion)."""
    
    def get_sales_series(self, days: int) -> List[Dict[str, Any]]:
        """Retrieve daily sales data."""
        ...


class DetectAnomaliesUC:
    """Use case for detecting anomalies in sales data using z-score.
    
    Identifies unusual sales patterns that may require attention.
    Follows SRP: single responsibility of anomaly detection.
    """
    
    def __init__(self, repo: SalesRepository, threshold: float = 2.0):
        """Initialize use case with repository.
        
        Args:
            repo: Repository implementing get_sales_series method
            threshold: Z-score threshold for anomaly (default: 2.0)
        """
        self.repo = repo
        self.threshold = threshold
    
    def execute(self, period: str = "last_60d") -> Dict[str, Any]:
        """Execute anomaly detection on sales data.
        
        Calculates z-scores for daily sales and flags outliers.
        Z-score = (value - mean) / std_dev
        Values with |z-score| > threshold are considered anomalies.
        
        Args:
            period: Time period to analyze (e.g., "last_60d", "last_90d")
            
        Returns:
            Dict with keys:
                - period: Period analyzed (str)
                - total_days: Number of days analyzed (int)
                - mean_sales: Average daily sales (float)
                - std_dev: Standard deviation (float)
                - anomalies: List of anomalous days with date, amount, z_score
                - anomaly_count: Number of anomalies detected (int)
                
        Raises:
            ValueError: If insufficient data for analysis
            Exception: If repository access fails
        """
        logger.info(f"Executing DetectAnomaliesUC for period: {period}")
        
        try:
            # Extract number of days from period string
            days = self._parse_period_days(period)
            
            # Retrieve sales data
            sales_series = self.repo.get_sales_series(days=days)
            
            if len(sales_series) < 2:
                raise ValueError("Insufficient data for anomaly detection (need at least 2 days)")
            
            # Calculate statistics
            amounts = [sale["amount"] for sale in sales_series]
            mean_val = mean(amounts)
            
            # Need at least 2 different values for std dev
            if len(set(amounts)) < 2:
                logger.warning("All sales values are identical, no anomalies detected")
                return {
                    "period": period,
                    "total_days": len(sales_series),
                    "mean_sales": round(mean_val, 2),
                    "std_dev": 0.0,
                    "anomalies": [],
                    "anomaly_count": 0,
                }
            
            std_dev = stdev(amounts)
            
            # Calculate z-scores and detect anomalies
            anomalies = []
            for sale in sales_series:
                amount = sale["amount"]
                z_score = (amount - mean_val) / std_dev if std_dev > 0 else 0.0
                
                if abs(z_score) > self.threshold:
                    anomalies.append({
                        "date": sale["date"],
                        "amount": round(amount, 2),
                        "z_score": round(z_score, 2),
                        "deviation": "high" if z_score > 0 else "low",
                    })
            
            # Sort anomalies by absolute z-score (most significant first)
            anomalies.sort(key=lambda x: abs(x["z_score"]), reverse=True)
            
            result = {
                "period": period,
                "total_days": len(sales_series),
                "mean_sales": round(mean_val, 2),
                "std_dev": round(std_dev, 2),
                "anomalies": anomalies,
                "anomaly_count": len(anomalies),
            }
            
            logger.info(
                f"Anomaly detection complete: {result['anomaly_count']} anomalies "
                f"detected out of {result['total_days']} days"
            )
            
            return result
            
        except ValueError as e:
            logger.warning(f"Anomaly detection validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to detect anomalies: {e}")
            raise
    
    def _parse_period_days(self, period: str) -> int:
        """Extract number of days from period string.
        
        Args:
            period: Period string like "last_30d", "last_60d"
            
        Returns:
            Number of days as integer
        """
        # Simple parsing: extract number from "last_XXd" format
        try:
            if period.startswith("last_") and period.endswith("d"):
                days_str = period[5:-1]  # Extract number between "last_" and "d"
                return int(days_str)
            else:
                # Default to 60 if format not recognized
                logger.warning(f"Unrecognized period format '{period}', defaulting to 60 days")
                return 60
        except (ValueError, IndexError):
            logger.warning(f"Failed to parse period '{period}', defaulting to 60 days")
            return 60
