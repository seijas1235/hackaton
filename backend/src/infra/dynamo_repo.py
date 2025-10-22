"""DynamoDB repository for finance data and agent actions.

This module provides data access methods for KPIs, sales series, AR aging,
and agent action tracking using DynamoDB as the persistence layer.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional
import uuid

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from loguru import logger


class DynamoRepo:
    """Repository for DynamoDB operations on finance data and agent actions.
    
    Data model:
    - KPIs: pk="KPI#<period>", contains aggregated metrics
    - Sales: pk="SALES#<date>", contains daily sales data
    - AR Aging: pk="AR_AGING#<customer_id>", contains aging buckets
    - Agent Actions: pk="ACTION#<action_id>", contains action details
    """
    
    def __init__(self, table_name: str, region: str):
        """Initialize DynamoDB repository.
        
        Args:
            table_name: DynamoDB table name
            region: AWS region (e.g., "us-east-1")
        """
        self.table_name = table_name
        self.region = region
        
        try:
            dynamodb = boto3.resource("dynamodb", region_name=region)
            self.table = dynamodb.Table(table_name)
            logger.info(f"DynamoDB repository initialized: table={table_name}, region={region}")
        except Exception as e:
            logger.error(f"Failed to initialize DynamoDB resource: {e}")
            raise
    
    def get_kpis(self, period: str = "last_30d") -> Dict[str, Any]:
        """Retrieve KPIs for a given period.
        
        Args:
            period: Time period identifier (e.g., "last_30d", "last_60d")
            
        Returns:
            Dict with keys: revenue, gross_margin, ar_total, ar_over_60
            
        Raises:
            ClientError: If DynamoDB operation fails
        """
        pk = f"KPI#{period}"
        
        try:
            logger.debug(f"Fetching KPIs for period: {period}")
            response = self.table.get_item(Key={"pk": pk})
            
            if "Item" not in response:
                logger.warning(f"No KPIs found for period: {period}")
                # Return default values if not found
                return {
                    "revenue": 0.0,
                    "gross_margin": 0.0,
                    "ar_total": 0.0,
                    "ar_over_60": 0.0,
                }
            
            item = response["Item"]
            kpis = {
                "revenue": float(item.get("revenue", 0)),
                "gross_margin": float(item.get("gross_margin", 0)),
                "ar_total": float(item.get("ar_total", 0)),
                "ar_over_60": float(item.get("ar_over_60", 0)),
            }
            
            logger.info(f"KPIs retrieved for period {period}: {kpis}")
            return kpis
            
        except ClientError as e:
            logger.error(f"DynamoDB error fetching KPIs: {e.response['Error']}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching KPIs: {e}")
            raise
    
    def get_sales_series(self, days: int = 30) -> List[Dict[str, Any]]:
        """Retrieve daily sales data for the last N days.
        
        Args:
            days: Number of days to retrieve (default: 30)
            
        Returns:
            List of dicts with keys: date, amount
            Sorted by date ascending
            
        Raises:
            ClientError: If DynamoDB operation fails
        """
        try:
            logger.debug(f"Fetching sales series for last {days} days")
            
            # Calculate date range
            end_date = datetime.utcnow().date()
            start_date = end_date - timedelta(days=days - 1)
            
            # Query sales items (assumes partition key starts with "SALES#")
            # For simplicity, we'll scan with filter (in production, use GSI or better key design)
            response = self.table.scan(
                FilterExpression=Key("pk").begins_with("SALES#")
            )
            
            items = response.get("Items", [])
            
            # Parse and filter by date range
            sales_series = []
            for item in items:
                # Extract date from pk: "SALES#YYYY-MM-DD"
                pk = item.get("pk", "")
                if not pk.startswith("SALES#"):
                    continue
                
                date_str = pk.split("#", 1)[1]
                try:
                    sale_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    if start_date <= sale_date <= end_date:
                        sales_series.append({
                            "date": date_str,
                            "amount": float(item.get("amount", 0)),
                        })
                except ValueError:
                    logger.warning(f"Invalid date format in pk: {pk}")
                    continue
            
            # Sort by date
            sales_series.sort(key=lambda x: x["date"])
            
            logger.info(f"Retrieved {len(sales_series)} sales records for {days} days")
            return sales_series
            
        except ClientError as e:
            logger.error(f"DynamoDB error fetching sales series: {e.response['Error']}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching sales series: {e}")
            raise
    
    def get_ar_aging(self) -> List[Dict[str, Any]]:
        """Retrieve accounts receivable aging data for all customers.
        
        Returns:
            List of dicts with keys: customer_id, customer_name, 
            current, days_30, days_60, days_90, days_over_90, total
            
        Raises:
            ClientError: If DynamoDB operation fails
        """
        try:
            logger.debug("Fetching AR aging data")
            
            # Scan for all AR_AGING items
            response = self.table.scan(
                FilterExpression=Key("pk").begins_with("AR_AGING#")
            )
            
            items = response.get("Items", [])
            
            ar_aging = []
            for item in items:
                pk = item.get("pk", "")
                customer_id = pk.split("#", 1)[1] if "#" in pk else "unknown"
                
                ar_aging.append({
                    "customer_id": customer_id,
                    "customer_name": item.get("customer_name", "Unknown"),
                    "current": float(item.get("current", 0)),
                    "days_30": float(item.get("days_30", 0)),
                    "days_60": float(item.get("days_60", 0)),
                    "days_90": float(item.get("days_90", 0)),
                    "days_over_90": float(item.get("days_over_90", 0)),
                    "total": float(item.get("total", 0)),
                })
            
            logger.info(f"Retrieved AR aging for {len(ar_aging)} customers")
            return ar_aging
            
        except ClientError as e:
            logger.error(f"DynamoDB error fetching AR aging: {e.response['Error']}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching AR aging: {e}")
            raise
    
    def create_agent_action(
        self,
        action: str,
        payload: Dict[str, Any],
        performed_by: str,
    ) -> str:
        """Create a new agent action record.
        
        Args:
            action: Action type (e.g., "collection_reminder", "payment_plan")
            payload: Action-specific data (dict)
            performed_by: User/agent identifier (from JWT sub claim)
            
        Returns:
            action_id: Unique ID for the created action
            
        Raises:
            ClientError: If DynamoDB operation fails
        """
        action_id = str(uuid.uuid4())
        pk = f"ACTION#{action_id}"
        timestamp = datetime.utcnow().isoformat()
        
        try:
            logger.debug(f"Creating agent action: {action} by {performed_by}")
            
            item = {
                "pk": pk,
                "action_id": action_id,
                "action": action,
                "payload": payload,
                "performed_by": performed_by,
                "timestamp": timestamp,
                "created_at": timestamp,
            }
            
            self.table.put_item(Item=item)
            
            logger.info(f"Agent action created: action_id={action_id}, action={action}")
            return action_id
            
        except ClientError as e:
            logger.error(f"DynamoDB error creating agent action: {e.response['Error']}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating agent action: {e}")
            raise
    
    def list_agent_actions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List recent agent actions.
        
        Args:
            limit: Maximum number of actions to return (default: 50)
            
        Returns:
            List of action dicts with keys: action_id, action, payload, 
            performed_by, timestamp
            Sorted by timestamp descending (most recent first)
            
        Raises:
            ClientError: If DynamoDB operation fails
        """
        try:
            logger.debug(f"Listing agent actions with limit={limit}")
            
            # Scan for all ACTION items
            response = self.table.scan(
                FilterExpression=Key("pk").begins_with("ACTION#"),
                Limit=limit * 2,  # Over-fetch to allow for filtering/sorting
            )
            
            items = response.get("Items", [])
            
            actions = []
            for item in items:
                actions.append({
                    "action_id": item.get("action_id"),
                    "action": item.get("action"),
                    "payload": item.get("payload", {}),
                    "performed_by": item.get("performed_by"),
                    "timestamp": item.get("timestamp"),
                })
            
            # Sort by timestamp descending
            actions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            # Apply limit
            actions = actions[:limit]
            
            logger.info(f"Retrieved {len(actions)} agent actions")
            return actions
            
        except ClientError as e:
            logger.error(f"DynamoDB error listing agent actions: {e.response['Error']}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error listing agent actions: {e}")
            raise
