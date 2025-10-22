# Backend (Python 3.12)

Project scaffold for the backend. Includes packaging via `pyproject.toml`, testing with `pytest`, and common runtime deps.

## Quickstart (Windows PowerShell)

0. Install Python 3.12 (if not installed):

```powershell
# List available Python versions
py -0p

# Install Python 3.12 via winget (requires approval)
winget install -e --id Python.Python.3.12
```

1. Create and activate a virtual environment with Python 3.12:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install package in editable mode with test extras:

```powershell
python -m pip install -U pip
python -m pip install -e .[test]
```

3. Run tests with coverage:

```powershell
pytest
```

4. Optional: Set environment variables for local dev (examples):

```powershell
$env:ENV = "local"
$env:LOG_LEVEL = "DEBUG"
$env:AWS_REGION = "us-east-1"
$env:AWS_PROFILE = "default"
$env:JWT_SECRET = "change-me"
$env:JWT_ALGORITHM = "HS256"
```

## Project layout

```
/backend/
  pyproject.toml
  README_BACKEND.md
  src/
    adapters/
      handlers/
      services/
    domain/
      models/
      usecases/
    infra/
    shared/
      settings.py    # Pydantic settings from env vars
      responses.py   # API Gateway response helpers with CORS
      auth.py        # JWT claims extraction & scope decorator
      log.py         # Loguru configuration for Lambda
  tools/
  tests/
```

## Adapter Layer

### API Gateway Handlers (`adapters/handlers/`)

Lambda functions for API Gateway HTTP API integration:

#### `get_kpis.py` — GET /agent/tools/kpis
Query params: `period` (default: last_30d)
Returns: KPI data (revenue, gross_margin, ar_total, ar_over_60)

#### `cashflow_forecast.py` — GET /agent/tools/cashflow
Query params: `horizon` (default: 30, max: 365)
Returns: Cashflow forecast with daily average and total

#### `detect_anomalies.py` — GET /agent/tools/anomalies
Query params: `period` (default: last_60d), `threshold` (default: 2.0)
Returns: List of sales anomalies with z-scores

#### `create_collection_reminder.py` — POST /agent/actions/collection-reminder
**Requires scope**: `agent:actions`
Body: `{customer_id, invoice_id?, remind_date?}`
Returns: Created action with action_id (201)

#### `list_actions.py` — GET /agent/actions
Query params: `limit` (default: 50, max: 100)
Returns: List of recent agent actions

#### `agent_chat.py` — POST /agent/chat
Body: `{message, session_id?}`
Returns: Bedrock Agent response (or mock if not configured)

All handlers use:
- Pydantic DTOs for request/response validation
- JWT claims extraction for user identification
- Shared response helpers with CORS
- Comprehensive error handling and logging

## Environment Variables

- **ENV**: local | dev | staging | prod (default: local)
- **LOG_LEVEL**: DEBUG | INFO | WARNING | ERROR | CRITICAL (default: INFO)
- **AWS_REGION**: AWS region name (optional, default: us-east-1)
- **AWS_PROFILE**: AWS named profile to use (optional)
- **TABLE_NAME**: DynamoDB table name (default: finance)
- **JWT_SECRET**: Secret for signing/validating JWTs (optional in dev)
- **JWT_ALGORITHM**: JWT algorithm, e.g., HS256 (default: HS256)
- **AGENT_ID**: Bedrock Agent ID for agent_chat handler (optional)
- **AGENT_ALIAS_ID**: Bedrock Agent Alias ID (optional)

## Shared Utilities

### `shared/responses.py`
API Gateway response helpers with CORS headers:
- `ok(data, status_code=200)` — Success response
- `bad_request(message, details=None)` — 400 error
- `unauthorized(message)` — 401 error
- `server_error(message, details=None)` — 500 error

### `shared/auth.py`
JWT authentication utilities (API Gateway JWT Authorizer pre-validates tokens):
- `get_claims_from_event(event)` — Extract JWT claims from API Gateway event
- `@require_scope("agent:actions")` — Decorator to enforce scope requirements

### `shared/log.py`
Loguru logging configuration:
- Auto-configures on import with level from `LOG_LEVEL` env var
- Structured logging to stdout (CloudWatch-friendly)

### `shared/settings.py`
Pydantic settings with environment variables:
- `get_settings()` — Cached singleton returning `Settings` instance

## Domain Layer

### Use Cases (`domain/usecases/`)

Business logic following Clean Architecture principles (SRP, DIP). Use cases depend on repository protocols, not concrete implementations.

#### `get_kpis.py` — GetKPIsUC
```python
GetKPIsUC(repo).execute(period="last_30d")
```
Retrieves financial KPIs for analysis. Returns revenue, gross_margin, ar_total, ar_over_60.

#### `cashflow_forecast.py` — CashflowForecastUC
```python
CashflowForecastUC(repo).execute(horizon_days=30)
```
Forecasts cashflow using simple moving average of historical sales. Returns average daily cashflow and total forecast.

#### `detect_anomalies.py` — DetectAnomaliesUC
```python
DetectAnomaliesUC(repo, threshold=2.0).execute(period="last_60d")
```
Detects anomalies in sales data using z-score analysis. Returns list of anomalous days with z-scores and deviations.

#### `create_collection_reminder.py` — CreateCollectionReminderUC
```python
CreateCollectionReminderUC(repo).execute(
    customer_id="CUST001",
    performed_by="user@example.com",
    invoice_id="INV123",  # optional
    remind_date="2025-10-20"  # optional, defaults to today
)
```
Creates collection reminder action. Returns action_id.

## Infrastructure Layer

### `infra/dynamo_repo.py`
DynamoDB repository for finance data and agent actions:
- `DynamoRepo(table_name, region)` — Initialize repository
- `get_kpis(period)` — Retrieve KPIs (revenue, gross_margin, ar_total, ar_over_60)
- `get_sales_series(days)` — Get daily sales data for last N days
- `get_ar_aging()` — Get accounts receivable aging buckets for all customers
- `create_agent_action(action, payload, performed_by)` — Create action record, returns action_id
- `list_agent_actions(limit=50)` — List recent agent actions

**Data Model:**
- KPIs: `pk="KPI#<period>"`
- Sales: `pk="SALES#<YYYY-MM-DD>"`
- AR Aging: `pk="AR_AGING#<customer_id>"`
- Agent Actions: `pk="ACTION#<action_id>"`

## Tools

### `tools/seed_data.py` — Data Seeding Utility

Seeds synthetic data into DynamoDB for testing and demo purposes.

**Generates:**
- 50 customers with AR aging data
- 120 days of daily sales data
- KPI aggregations (last_30d, last_60d, last_90d)
- 10 sample agent actions

**Usage:**
```powershell
# Set environment variables
$env:TABLE_NAME = "finance"
$env:AWS_REGION = "us-east-1"

# Run seed script
python -m tools.seed_data
```

**What it creates:**
- `AR_AGING#CUST001` through `AR_AGING#CUST050` — Customer aging buckets
- `SALES#YYYY-MM-DD` — 120 days of sales records
- `KPI#last_30d`, `KPI#last_60d`, `KPI#last_90d` — Aggregated metrics
- `ACTION#action-001` through `ACTION#action-010` — Sample actions

## Testing

Run the full test suite with coverage:

```powershell
pytest -v --cov=src --cov=tools --cov-report=term-missing
```

**Test Coverage:**
- **79 tests** covering all modules
- **78% overall coverage**
- Use cases: 90-100% coverage
- Handlers: 71-79% coverage
- Infrastructure: 73-75% coverage

**Test Structure:**
- `test_*_uc.py` — Use case tests with mock repositories
- `test_handlers.py` — Handler tests with simulated API Gateway events
- `test_dynamo_repo.py` — Repository tests with mocked boto3
- `test_seed_data.py` — Data generation and batch write tests
- `test_responses.py`, `test_auth.py`, `test_log.py` — Shared utilities

## Notes

- Packaging is configured with setuptools; the `src` layout is used.
- To install only runtime deps: `pip install -e .`.
- To add new runtime deps, edit `pyproject.toml` under `[project].dependencies`.
- To add dev/test tools, use `[project.optional-dependencies].test`.
