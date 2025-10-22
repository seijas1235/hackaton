"""Use case: Get KPIs for a specified period."""

from typing import Any, Dict, Protocol

from loguru import logger


class KPIRepository(Protocol):
    """Protocol for KPI data access (dependency inversion)."""
    
    def get_kpis(self, period: str) -> Dict[str, Any]:
        """Retrieve KPIs for a given period."""
        ...


class GetKPIsUC:
    """Use case for retrieving key performance indicators.
    
    Fetches financial KPIs (revenue, gross margin, AR totals) for analysis.
    Follows SRP: single responsibility of coordinating KPI retrieval.
    """
    
    def __init__(self, repo: KPIRepository):
        """Initialize use case with repository.
        
        Args:
            repo: Repository implementing get_kpis method
        """
        self.repo = repo
    
    def execute(self, period: str = "last_30d") -> Dict[str, Any]:
        """Execute the use case to retrieve KPIs.
        
        Args:
            period: Time period identifier (e.g., "last_30d", "last_60d", "last_90d")
            
        Returns:
            Dict with keys:
                - revenue: Total revenue (float)
                - gross_margin: Gross margin percentage (float)
                - ar_total: Total accounts receivable (float)
                - ar_over_60: AR aged over 60 days (float)
                
        Raises:
            Exception: If repository access fails
        """
        logger.info(f"Executing GetKPIsUC for period: {period}")
        
        try:
            kpis = self.repo.get_kpis(period)
            logger.debug(f"KPIs retrieved: {kpis}")
            return kpis
        except Exception as e:
            logger.error(f"Failed to retrieve KPIs for period {period}: {e}")
            raise
