"""Use case: Forecast cashflow using simple moving average."""

from statistics import mean
from typing import Any, Dict, List, Protocol

from loguru import logger


class SalesRepository(Protocol):
    """Protocol for sales data access (dependency inversion)."""
    
    def get_sales_series(self, days: int) -> List[Dict[str, Any]]:
        """Retrieve daily sales data."""
        ...


class CashflowForecastUC:
    """Use case for forecasting cashflow using simple moving average.
    
    Analyzes historical sales data to predict future cashflow.
    Follows SRP: single responsibility of cashflow forecasting.
    """
    
    def __init__(self, repo: SalesRepository):
        """Initialize use case with repository.
        
        Args:
            repo: Repository implementing get_sales_series method
        """
        self.repo = repo
    
    def execute(self, horizon_days: int = 30) -> Dict[str, Any]:
        """Execute cashflow forecast for specified horizon.
        
        Uses simple moving average of historical sales to forecast future cashflow.
        Assumes sales history is available for at least the horizon period.
        
        Args:
            horizon_days: Number of days to forecast (default: 30)
            
        Returns:
            Dict with keys:
                - forecast_days: Number of days forecasted (int)
                - average_daily_cashflow: Predicted daily cashflow (float)
                - total_forecast: Total predicted cashflow for horizon (float)
                - historical_period_days: Number of days of historical data used (int)
                
        Raises:
            ValueError: If insufficient historical data
            Exception: If repository access fails
        """
        logger.info(f"Executing CashflowForecastUC for {horizon_days} days")
        
        try:
            # Retrieve historical sales (use 2x horizon for better average)
            lookback_days = max(horizon_days * 2, 60)
            sales_series = self.repo.get_sales_series(days=lookback_days)
            
            if not sales_series:
                raise ValueError("No historical sales data available for forecast")
            
            # Calculate simple moving average
            amounts = [sale["amount"] for sale in sales_series]
            avg_daily = mean(amounts) if amounts else 0.0
            
            # Project forward
            total_forecast = avg_daily * horizon_days
            
            result = {
                "forecast_days": horizon_days,
                "average_daily_cashflow": round(avg_daily, 2),
                "total_forecast": round(total_forecast, 2),
                "historical_period_days": len(sales_series),
            }
            
            logger.info(
                f"Cashflow forecast: {result['average_daily_cashflow']}/day, "
                f"total {result['total_forecast']} over {horizon_days} days"
            )
            
            return result
            
        except ValueError as e:
            logger.warning(f"Cashflow forecast validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to forecast cashflow: {e}")
            raise
