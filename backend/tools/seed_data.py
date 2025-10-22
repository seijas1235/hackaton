"""Seed synthetic data into DynamoDB for testing and demo purposes.

Generates:
- 50 customers with AR aging data
- 120 days of daily sales data
- KPI aggregations for different periods
- Sample agent actions

Run with:
    python -m tools.seed_data
"""

import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal
import random
from typing import List, Dict, Any

import boto3
from botocore.exceptions import ClientError
from loguru import logger


# Customer names for realistic data
CUSTOMER_NAMES = [
    "Acme Corp", "TechVision Inc", "Global Solutions", "Metro Systems",
    "Apex Innovations", "Quantum Enterprises", "Fusion Technologies",
    "Stellar Industries", "Horizon Group", "Velocity Partners",
    "Nexus Solutions", "Pinnacle Systems", "Vanguard Corp",
    "Summit Technologies", "Catalyst Industries", "Beacon Systems",
    "Precision Manufacturing", "Dynamic Solutions", "Eclipse Group",
    "Infinity Technologies", "Meridian Enterprises", "Titan Industries",
    "Atlas Corporation", "Phoenix Systems", "Omega Solutions",
    "Genesis Technologies", "Cascade Industries", "Zenith Group",
    "Triumph Enterprises", "Vertex Solutions", "Quantum Dynamics",
    "Noble Technologies", "Crown Industries", "Unity Systems",
    "Prestige Solutions", "Legacy Enterprises", "Fortis Group",
    "Paramount Industries", "Sovereign Systems", "Imperial Solutions",
    "Paramount Technologies", "Radiant Enterprises", "Supreme Industries",
    "Valor Systems", "Majestic Solutions", "Elite Technologies",
    "Premier Industries", "Noble Enterprises", "Regal Systems",
    "Grand Solutions", "Prime Technologies"
]


def get_config() -> tuple[str, str]:
    """Get configuration from environment variables."""
    table_name = os.getenv("TABLE_NAME", "finance")
    aws_region = os.getenv("AWS_REGION", "us-east-1")
    
    logger.info(f"Configuration: table={table_name}, region={aws_region}")
    return table_name, aws_region


def generate_customers(count: int = 50) -> List[Dict[str, Any]]:
    """Generate customer records with AR aging data.
    
    Args:
        count: Number of customers to generate
        
    Returns:
        List of customer items for DynamoDB
    """
    customers = []
    
    for i in range(count):
        customer_id = f"CUST{i+1:03d}"
        customer_name = CUSTOMER_NAMES[i % len(CUSTOMER_NAMES)]
        
        # Generate AR aging buckets with realistic distribution
        current = Decimal(str(random.randint(5000, 50000)))
        days_30 = Decimal(str(random.randint(2000, 20000)))
        days_60 = Decimal(str(random.randint(1000, 10000)))
        days_90 = Decimal(str(random.randint(500, 5000)))
        days_over_90 = Decimal(str(random.randint(0, 3000)))
        
        total = current + days_30 + days_60 + days_90 + days_over_90
        
        item = {
            "pk": f"AR_AGING#{customer_id}",
            "customer_id": customer_id,
            "customer_name": customer_name,
            "current": current,
            "days_30": days_30,
            "days_60": days_60,
            "days_90": days_90,
            "days_over_90": days_over_90,
            "total": total,
        }
        customers.append(item)
    
    logger.info(f"Generated {len(customers)} customer records")
    return customers


def generate_sales(days: int = 120) -> List[Dict[str, Any]]:
    """Generate daily sales data with realistic patterns.
    
    Args:
        days: Number of days of sales history
        
    Returns:
        List of sales items for DynamoDB
    """
    sales = []
    base_amount = 5000.0
    
    end_date = datetime.utcnow().date()
    
    for i in range(days):
        date = end_date - timedelta(days=days - i - 1)
        
        # Add some variation: trend + seasonality + random noise
        trend = i * 10  # Slight upward trend
        seasonality = 1000 * (1 + 0.3 * ((i % 7) / 7))  # Weekly pattern
        noise = random.gauss(0, 500)  # Random variation
        
        amount = max(1000, base_amount + trend + seasonality + noise)
        
        item = {
            "pk": f"SALES#{date.isoformat()}",
            "date": date.isoformat(),
            "amount": Decimal(str(round(amount, 2))),
        }
        sales.append(item)
    
    logger.info(f"Generated {len(sales)} sales records")
    return sales


def generate_kpis() -> List[Dict[str, Any]]:
    """Generate KPI aggregations for different periods.
    
    Returns:
        List of KPI items for DynamoDB
    """
    kpis = []
    
    periods = [
        ("last_30d", 150000, 0.35, 45000, 12000),
        ("last_60d", 290000, 0.34, 52000, 15000),
        ("last_90d", 420000, 0.36, 58000, 18000),
    ]
    
    for period, revenue, margin, ar_total, ar_over_60 in periods:
        item = {
            "pk": f"KPI#{period}",
            "period": period,
            "revenue": Decimal(str(revenue)),
            "gross_margin": Decimal(str(margin)),
            "ar_total": Decimal(str(ar_total)),
            "ar_over_60": Decimal(str(ar_over_60)),
        }
        kpis.append(item)
    
    logger.info(f"Generated {len(kpis)} KPI records")
    return kpis


def generate_actions(count: int = 10) -> List[Dict[str, Any]]:
    """Generate sample agent actions.
    
    Args:
        count: Number of actions to generate
        
    Returns:
        List of action items for DynamoDB
    """
    actions = []
    action_types = ["collection_reminder", "payment_plan", "credit_review"]
    
    for i in range(count):
        action_id = f"action-{i+1:03d}"
        action_type = random.choice(action_types)
        customer_id = f"CUST{random.randint(1, 50):03d}"
        
        timestamp = (datetime.utcnow() - timedelta(days=random.randint(0, 30))).isoformat()
        
        item = {
            "pk": f"ACTION#{action_id}",
            "action_id": action_id,
            "action": action_type,
            "payload": {
                "customer_id": customer_id,
                "notes": f"Sample {action_type} action"
            },
            "performed_by": "seed_script@system.local",
            "timestamp": timestamp,
            "created_at": timestamp,
        }
        actions.append(item)
    
    logger.info(f"Generated {len(actions)} action records")
    return actions


def batch_write_items(table_name: str, region: str, items: List[Dict[str, Any]]) -> None:
    """Write items to DynamoDB in batches.
    
    Args:
        table_name: DynamoDB table name
        region: AWS region
        items: List of items to write
        
    Raises:
        ClientError: If DynamoDB operation fails
    """
    dynamodb = boto3.resource("dynamodb", region_name=region)
    table = dynamodb.Table(table_name)
    
    batch_size = 25  # DynamoDB batch_write limit
    total_written = 0
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        
        try:
            with table.batch_writer() as writer:
                for item in batch:
                    writer.put_item(Item=item)
            
            total_written += len(batch)
            logger.debug(f"Wrote batch: {total_written}/{len(items)} items")
            
        except ClientError as e:
            logger.error(f"Error writing batch: {e.response['Error']}")
            raise
    
    logger.info(f"Successfully wrote {total_written} items to {table_name}")


def main() -> None:
    """Main entry point for data seeding."""
    logger.info("Starting data seed process...")
    
    # Get configuration
    table_name, aws_region = get_config()
    
    # Generate all data
    logger.info("Generating synthetic data...")
    customers = generate_customers(50)
    sales = generate_sales(120)
    kpis = generate_kpis()
    actions = generate_actions(10)
    
    # Combine all items
    all_items = customers + sales + kpis + actions
    total_items = len(all_items)
    
    logger.info(f"Total items to write: {total_items}")
    logger.info(f"  - Customers (AR Aging): {len(customers)}")
    logger.info(f"  - Sales: {len(sales)}")
    logger.info(f"  - KPIs: {len(kpis)}")
    logger.info(f"  - Actions: {len(actions)}")
    
    # Write to DynamoDB
    try:
        logger.info(f"Writing to DynamoDB table: {table_name}")
        batch_write_items(table_name, aws_region, all_items)
        logger.info("✓ Data seeding completed successfully!")
        
    except ClientError as e:
        logger.error(f"✗ Failed to seed data: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"✗ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
