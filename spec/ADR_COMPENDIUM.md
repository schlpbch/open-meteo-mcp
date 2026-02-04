# Open Meteo MCP (Python) - Architecture Decision Records (ADR) Compendium

**Document Version**: 2.0.0 **Last Updated**: 2026-02-04 **Total ADRs**: 15 (11 Accepted, 4 Proposed)

**Related Documents**:
- [README.md](../README.md) - User guide and installation
- [CHANGELOG.md](../CHANGELOG.md) - Version history

---

## Status Legend

- ✅ **Accepted** - Currently in use and actively maintained
- 🔄 **Proposed** - Under consideration, not yet implemented
- ⛔ **Superseded** - Replaced by another ADR (see cross-reference)
- 🗑️ **Deprecated** - No longer applicable, kept for historical context

---

## Quick Reference by Category

### Core Architecture

- [ADR-001: Use FastMCP Framework for MCP Protocol](#adr-001-use-fastmcp-framework-for-mcp-protocol)
  ✅
- [ADR-002: Pydantic v2 for Data Models](#adr-002-pydantic-v2-for-data-models)
  ✅
- [ADR-003: Async/Await with httpx for API Calls](#adr-003-asyncawait-with-httpx-for-api-calls)
  ✅
- [ADR-004: Python 3.11+ as Minimum Version](#adr-004-python-311-as-minimum-version)
  ✅

### Development Standards

- [ADR-005: Semantic Versioning (SemVer)](#adr-005-semantic-versioning-semver)
  ✅
- [ADR-006: MCP Tool Naming Convention (snake_case with meteo__ prefix)](#adr-006-mcp-tool-naming-convention)
  ✅
- [ADR-007: Package Management with uv](#adr-007-package-management-with-uv)
  ✅

### Quality & Observability

- [ADR-008: Structured Logging with structlog](#adr-008-structured-logging-with-structlog)
  ✅
- [ADR-009: pytest for Testing with 80%+ Coverage](#adr-009-pytest-for-testing-with-80-coverage)
  ✅
- [ADR-010: MyPy Strict Type Checking](#adr-010-mypy-strict-type-checking)
  ✅

### Deployment & Integration

- [ADR-011: FastMCP Cloud Deployment](#adr-011-fastmcp-cloud-deployment)
  🔄

### v4.0.0 Features (Proposed)

- [ADR-012: REST API with FastAPI](#adr-012-rest-api-with-fastapi) 🔄
- [ADR-013: Simple Chat API with Anthropic SDK](#adr-013-simple-chat-api-with-anthropic-sdk) 🔄
- [ADR-014: Service Layer Pattern for Python](#adr-014-service-layer-pattern-for-python) 🔄
- [ADR-015: Remove meteo__ Tool Prefix (Breaking Change)](#adr-015-remove-meteo-tool-prefix-breaking-change) 🔄

---

## ADR-001: Use FastMCP Framework for MCP Protocol

**Status**: ✅ Accepted **Date**: 2026-01-15 **Context**: Core Architecture

### [ADR-001] Decision

Use **FastMCP** (Anthropic's lightweight MCP server framework) for implementing the Model Context Protocol server.

**Rationale**:

- **Minimal Overhead**: Designed specifically for Python MCP servers with zero unnecessary dependencies
- **Async-First**: Built on Python's async/await for efficient concurrency
- **Declarative Tools**: Simple decorators (@mcp.tool, @mcp.resource, @mcp.prompt) for tool definitions
- **FastMCP Cloud**: Native deployment support via FastMCP Cloud infrastructure
- **Protocol Compliance**: Maintains strict MCP specification compliance
- **Type Safety**: Integrates seamlessly with Pydantic for type validation
- **Developer Experience**: Minimal boilerplate compared to custom MCP implementations

### [ADR-001] Example

```python
from fastmcp import FastMCP

mcp = FastMCP("open-meteo")

@mcp.tool()
async def get_weather(latitude: float, longitude: float) -> dict:
    """Get weather forecast for coordinates."""
    client = OpenMeteoClient()
    forecast = await client.get_weather(latitude, longitude)
    return forecast.to_dict()

@mcp.resource(uri="weather://codes")
def weather_codes() -> str:
    """WMO weather code reference."""
    return load_json_resource("data/weather-codes.json")
```

### [ADR-001] Benefits

- **Protocol Compliance**: Automatic MCP JSON-RPC message handling
- **Standards Alignment**: Follows industry best practices for MCP servers
- **Extensibility**: Supports all MCP features (tools, resources, prompts, subscriptions)
- **Community**: Active maintenance and support from Anthropic

### [ADR-001] Related ADRs

- [ADR-003](#adr-003-asyncawait-with-httpx-for-api-calls) - Async operations with httpx
- [ADR-006](#adr-006-mcp-tool-naming-convention) - Tool naming conventions

---

## ADR-002: Pydantic v2 for Data Models

**Status**: ✅ Accepted **Date**: 2026-01-15 **Context**: Core Architecture

### [ADR-002] Decision

Use **Pydantic v2** for all data models, DTOs, and request/response validation.

**Benefits**:

- **Type Safety**: Full type hints with runtime validation
- **Performance**: ~5-10x faster than v1 with Rust-backed validation
- **JSON Schema**: Automatic OpenAPI/JSON Schema generation
- **Serialization**: Built-in to_dict() and model_dump_json() methods
- **Validators**: Field and model validators with error messages
- **Immutability**: ConfigDict(frozen=True) for immutable models

### [ADR-002] Example

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional

class WeatherInput(BaseModel):
    """Type-safe weather query input."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")
    forecast_days: Optional[int] = Field(default=7, ge=1, le=16)

    @field_validator('latitude', 'longitude')
    @classmethod
    def validate_coordinates(cls, v: float) -> float:
        if v == 0:
            raise ValueError("Coordinates cannot be zero")
        return v

class WeatherResponse(BaseModel):
    """Type-safe weather response."""
    model_config = ConfigDict(frozen=True)  # Immutable

    temperature: float
    precipitation: float
    weather_code: int
    timestamp: datetime
```

### [ADR-002] Configuration

```python
# pyproject.toml
[project]
requires-python = ">=3.11"

[project.optional-dependencies]
dev = [
    "pydantic>=2.0",
    "pydantic[email]",
]
```

---

## ADR-003: Async/Await with httpx for API Calls

**Status**: ✅ Accepted **Date**: 2026-01-15 **Context**: Core Architecture

### [ADR-003] Decision

Use **async/await pattern with httpx** (async HTTP client) for all Open-Meteo API calls.

**Rationale**:

- **Non-Blocking**: Async operations prevent blocking during I/O operations
- **Concurrency**: Handle multiple simultaneous API requests efficiently
- **httpx**: Modern, maintainable alternative to requests with native async support
- **Timeout Handling**: Built-in timeout and retry mechanisms
- **Gzip Support**: Automatic compression for bandwidth efficiency

### [ADR-003] Example

```python
import httpx
from typing import Optional

class OpenMeteoClient:
    """Async Open-Meteo API client."""

    BASE_URL = "https://api.open-meteo.com/v1"
    TIMEOUT = 30.0

    async def get_weather(
        self,
        latitude: float,
        longitude: float,
        forecast_days: Optional[int] = None
    ) -> WeatherForecast:
        """Fetch weather forecast asynchronously."""
        async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "forecast_days": forecast_days or 7,
                "hourly": "temperature_2m,precipitation",
                "daily": "temperature_2m_max,weather_code"
            }

            response = await client.get(
                f"{self.BASE_URL}/forecast",
                params=params
            )
            response.raise_for_status()

            data = response.json()
            return WeatherForecast.model_validate(data)
```

### [ADR-003] Benefits

- **Efficiency**: Single-threaded async model with 1000+ concurrent connections
- **Resource Usage**: Minimal memory overhead compared to threading
- **Error Handling**: Structured exception handling with retry logic
- **Testing**: Easy to mock async calls with pytest-asyncio

### [ADR-003] Configuration

```python
# pyproject.toml
[project.optional-dependencies]
main = [
    "httpx>=0.27.0",  # Async HTTP client
]

# src/open_meteo_mcp/client.py
TIMEOUT = 30.0  # seconds
RETRIES = 3     # retry count
BACKOFF = 1.5   # exponential backoff multiplier
```

### [ADR-003] Related ADRs

- [ADR-001](#adr-001-use-fastmcp-framework-for-mcp-protocol) - FastMCP async operations
- [ADR-002](#adr-002-pydantic-v2-for-data-models) - Pydantic validation

---

## ADR-004: Python 3.11+ as Minimum Version

**Status**: ✅ Accepted **Date**: 2026-01-15 **Context**: Core Architecture

### [ADR-004] Decision

Require **Python 3.11+** as the minimum supported version, with targeting Python 3.12+ for new features.

**Rationale**:

- **PEP 604 Union Syntax**: Use `X | Y` instead of `Union[X, Y]`
- **Type Hints Standard**: Improved typing support and static analysis
- **ExceptionGroup**: Better exception handling patterns
- **Performance**: 10-15% faster than Python 3.10
- **Asyncio Improvements**: Enhanced async/await with proper error handling
- **Security**: Modern cryptography and SSL/TLS support
- **Long-term Support**: Python 3.11 supported until 2027, 3.12 until 2028

### [ADR-004] Example

```python
# Use PEP 604 union syntax (Python 3.11+)
def process_location(location: dict | str | None) -> Location:
    """Type hints with modern union syntax."""
    ...

# Python 3.11+ async enhancements
async def fetch_data() -> dict[str, float]:
    """Async function with modern dict type hints."""
    ...
```

### [ADR-004] Configuration

```toml
# pyproject.toml
[project]
name = "open-meteo-mcp"
requires-python = ">=3.11"

[build-system]
requires = ["setuptools>=68", "wheel"]

# .python-version (for pyenv/uv)
3.12
```

### [ADR-004] Benefits

- **Language Features**: Access to latest Python improvements
- **Dependency Compatibility**: Most modern packages target 3.11+
- **Support Window**: Extended support timeline (3+ years)
- **Performance**: Baseline 10%+ performance improvement

---

## ADR-005: Semantic Versioning (SemVer)

**Status**: ✅ Accepted **Date**: 2026-01-15 **Context**: Development Standards

### [ADR-005] Decision

Follow **Semantic Versioning 2.0** (MAJOR.MINOR.PATCH) for version numbering.

**Versioning Rules**:

- **MAJOR** (e.g., 3.0.0): Breaking changes to MCP tool signatures, resource URIs, or data models
- **MINOR** (e.g., 3.2.0): New features (tools, resources, prompts), backward-compatible enhancements
- **PATCH** (e.g., 3.2.1): Bug fixes, non-breaking improvements, dependency updates

### [ADR-005] Current Version Strategy

| Version | Status | Release Date | Support |
|---------|--------|--------------|---------|
| v3.2.0  | Current | 2026-01-22 | Active |
| v3.1.0  | Previous | 2026-01-15 | Active (bugfix only) |
| v3.0.0  | Stable | 2025-12-01 | Active |
| v2.0.x  | Legacy | 2025-10-01 | EOL 2026-02-01 |

### [ADR-005] Release Process

1. **Feature Branch**: Develop on feature branches (`feat/new-tool`)
2. **Version Bump**: Update version in `src/open_meteo_mcp/__init__.py`
3. **Changelog**: Document in CHANGELOG.md with "Added/Changed/Fixed" sections
4. **Git Tag**: Create annotated tag (`git tag -a v3.2.0 -m "Release v3.2.0"`)
5. **Publish**: Release to PyPI (via CI/CD)

### [ADR-005] Example

```python
# src/open_meteo_mcp/__init__.py
__version__ = "3.2.0"  # Update on release

# Version parsing
from packaging import version
current = version.parse(__version__)
```

---

## ADR-006: MCP Tool Naming Convention

**Status**: ✅ Accepted **Date**: 2026-01-15 **Context**: Development Standards

### [ADR-006] Decision

Use **snake_case** for MCP tool names with **`meteo__` prefix** to namespace tools within Claude Desktop.

**Pattern**: `meteo__{action}_{subject}`

**Examples**:

- `meteo__search_location` - Geocoding search
- `meteo__get_weather` - Weather forecast
- `meteo__get_snow_conditions` - Alpine snow data
- `meteo__get_air_quality` - Air quality index
- `meteo__get_weather_alerts` - Alert generation
- `meteo__get_comfort_index` - Activity suitability
- `meteo__get_astronomy` - Sunrise/sunset data
- `meteo__search_location_swiss` - Switzerland-specific search
- `meteo__compare_locations` - Multi-location comparison
- `meteo__get_historical_weather` - Historical data queries
- `meteo__get_marine_conditions` - Wave/swell data

### [ADR-006] Implementation

```python
from fastmcp import FastMCP

mcp = FastMCP("open-meteo")

@mcp.tool(name="meteo__get_weather")
async def get_weather(
    latitude: float,
    longitude: float,
    forecast_days: int = 7
) -> dict:
    """Get weather forecast for coordinates."""
    ...

@mcp.tool(name="meteo__search_location")
async def search_location(query: str) -> list[dict]:
    """Search locations by name."""
    ...
```

### [ADR-006] Benefits

- **Namespace Isolation**: Tools grouped under `meteo__` in Claude Desktop
- **Consistency**: Matches Python naming conventions (snake_case)
- **Clarity**: Clear action-subject structure makes tools discoverable
- **Compatibility**: Aligns with MCP ecosystem standards

### [ADR-006] Related ADRs

- [ADR-001](#adr-001-use-fastmcp-framework-for-mcp-protocol) - FastMCP tool definitions

---

## ADR-007: Package Management with uv

**Status**: ✅ Accepted **Date**: 2026-01-15 **Context**: Development Standards

### [ADR-007] Decision

Use **uv** (Astral's fast Python package manager) for dependency management and packaging.

**Rationale**:

- **Performance**: 10-100x faster than pip/Poetry
- **Reliability**: Deterministic dependency resolution
- **Lock File**: `uv.lock` ensures reproducible installs
- **Built-in Tools**: Includes pip, venv, and build functionality
- **Python Management**: Can manage Python versions (uv python)

### [ADR-007] Configuration

```toml
# pyproject.toml - PEP 517/518 compliant
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "open-meteo-mcp"
version = "3.2.0"
requires-python = ">=3.11"

[project.dependencies]
fastmcp = ">=0.2.0"
httpx = ">=0.27.0"
pydantic = ">=2.0.0"
structlog = ">=23.1.0"
pytz = ">=2024.0"
swiss-ai-mcp-commons = "@v1.1.0"  # Git dependency

[project.optional-dependencies]
dev = [
    "pytest>=9.0.2",
    "pytest-asyncio>=1.3.0",
    "pytest-httpx>=0.36.0",
    "pytest-cov>=4.1.0",
    "mypy>=1.5.0",
]

[tool.uv]
python-version = "3.12"
```

### [ADR-007] Workflow

```bash
# Install dependencies
uv sync                 # Install from lock file

# Add new dependency
uv add httpx           # Adds to pyproject.toml and lock file

# Run scripts
uv run pytest          # Run with locked environment

# Update Python
uv python install 3.12 # Install Python 3.12

# Build package
uv build               # Create wheel and sdist
```

### [ADR-007] Benefits

- **Reproducibility**: Lock file ensures identical installs across environments
- **Speed**: CI/CD pipelines complete 50%+ faster
- **Simplicity**: Single tool replaces pip + poetry + venv
- **Maintainability**: Easy to manage multiple environments

### [ADR-007] Lock File

```
# uv.lock (auto-generated, checked into git)
version = 4
requires-python = ">=3.11"

[[package]]
name = "fastmcp"
version = "0.2.0"
source = { type = "registry", url = "https://pypi.org/simple" }
...
```

---

## ADR-008: Structured Logging with structlog

**Status**: ✅ Accepted **Date**: 2026-01-15 **Context**: Quality & Observability

### [ADR-008] Decision

Use **structlog** for structured JSON logging with contextual information.

**Rationale**:

- **Structured Output**: JSON logs for easy parsing and analysis
- **Performance**: Zero-cost abstraction for production logging
- **Context**: Thread-local and context-aware logging
- **Processors**: Flexible log formatting and filtering
- **Ecosystem**: Works with standard Python logging and integrates with observability platforms

### [ADR-008] Configuration

```python
# src/open_meteo_mcp/logging.py
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()
```

### [ADR-008] Usage

```python
from structlog import get_logger

logger = get_logger()

# Structured logging with context
logger.info(
    "weather_request",
    latitude=47.3769,
    longitude=8.5417,
    forecast_days=7,
    duration_ms=245,
    status="success"
)

# Output:
# {"event": "weather_request", "latitude": 47.3769, "longitude": 8.5417,
#  "forecast_days": 7, "duration_ms": 245, "status": "success", ...}
```

### [ADR-008] Benefits

- **Observability**: Structured logs integrate with ELK, Datadog, etc.
- **Debugging**: Rich context makes troubleshooting easier
- **Analysis**: JSON format enables programmatic log analysis
- **Performance**: No runtime overhead in production

### [ADR-008] Related ADRs

- [ADR-009](#adr-009-pytest-for-testing-with-80-coverage) - Testing with logging

---

## ADR-009: pytest for Testing with 80%+ Coverage

**Status**: ✅ Accepted **Date**: 2026-01-15 **Context**: Quality & Observability

### [ADR-009] Decision

Use **pytest** as the testing framework with **≥80% code coverage** target.

**Test Layers**:

1. **Unit Tests**: Test individual functions and classes (models, helpers)
2. **Integration Tests**: Test API client interactions and tool implementations
3. **Async Tests**: Use pytest-asyncio for async function testing
4. **HTTP Mocking**: pytest-httpx for Open-Meteo API call mocking

### [ADR-009] Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
minversion = "9.0"
addopts = "--cov=src/open_meteo_mcp --cov-report=html --cov-report=term-missing"

[tool.coverage.run]
source = ["src/open_meteo_mcp"]
omit = [
    "*/tests/*",
    "**/__main__.py",
    "**/conftest.py",
]

[tool.coverage.report]
fail_under = 80
precision = 2
```

### [ADR-009] Example Test Structure

```python
# tests/test_models.py
import pytest
from pydantic import ValidationError
from open_meteo_mcp.models import WeatherInput

class TestWeatherInput:
    """Unit tests for WeatherInput model."""

    def test_valid_coordinates(self):
        """Test valid coordinate validation."""
        input_data = WeatherInput(latitude=47.3769, longitude=8.5417)
        assert input_data.latitude == 47.3769
        assert input_data.longitude == 8.5417

    def test_invalid_latitude(self):
        """Test latitude bounds validation."""
        with pytest.raises(ValidationError):
            WeatherInput(latitude=91.0, longitude=8.5417)

# tests/test_client.py
import pytest
import httpx
import pytest_httpx
from open_meteo_mcp.client import OpenMeteoClient
from open_meteo_mcp.models import WeatherForecast

@pytest.mark.asyncio
async def test_get_weather(httpx_mock: pytest_httpx.HTTPXMock):
    """Test weather API call with mocked HTTP."""
    mock_response = {
        "latitude": 47.3769,
        "longitude": 8.5417,
        "current": {"temperature": 15.0, "weather_code": 80}
    }

    httpx_mock.add_response(
        method="GET",
        url="https://api.open-meteo.com/v1/forecast",
        json=mock_response
    )

    client = OpenMeteoClient()
    result = await client.get_weather(47.3769, 8.5417)

    assert isinstance(result, WeatherForecast)
    assert result.latitude == 47.3769
```

### [ADR-009] Coverage Report

```
tests/test_*.py run with:
    uv run pytest tests/ -v --cov
    uv run pytest tests/ --cov-report=html

Target: ≥80% coverage
Current: 78% (as of v3.2.0)
```

### [ADR-009] Benefits

- **Quality**: Catches regressions and edge cases
- **Confidence**: High coverage enables safe refactoring
- **Documentation**: Tests serve as code examples
- **CI/CD**: Automated test runs on every commit

---

## ADR-010: MyPy Strict Type Checking

**Status**: ✅ Accepted **Date**: 2026-01-15 **Context**: Quality & Observability

### [ADR-010] Decision

Use **MyPy in strict mode** for static type checking of all Python code.

**Rationale**:

- **Bug Prevention**: Catches type errors before runtime
- **Documentation**: Type hints serve as inline documentation
- **IDE Support**: Enhanced autocomplete and refactoring
- **Maintainability**: Easier to understand and modify code
- **Performance**: No runtime overhead (compile-time only)

### [ADR-010] Configuration

```toml
# pyproject.toml
[tool.mypy]
# Strict mode enforcement
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
strict_equality = true
strict_optional = true

# Plugin configuration
plugins = ["pydantic.mypy"]

# Ignore patterns
ignore_errors = false
ignore_missing_imports = false

# Source paths
files = ["src/", "tests/"]

# Python version
python_version = "3.11"
```

### [ADR-010] Example

```python
# Correct: Type hints on all functions
async def get_weather(
    latitude: float,
    longitude: float,
    forecast_days: int = 7
) -> WeatherForecast:
    """Fully typed function."""
    client = OpenMeteoClient()
    forecast = await client.get_weather(latitude, longitude, forecast_days)
    return forecast

# MyPy Error: Missing return type
async def search_location(query: str):  # ❌ error: Function is missing a return type annotation
    """Missing return type."""
    ...

# Correct: Proper Optional handling
from typing import Optional

def process_data(value: Optional[str]) -> str:
    """Handle optional values properly."""
    if value is None:
        return ""
    return value.upper()
```

### [ADR-010] CI/CD Integration

```bash
# Run type checking
uv run mypy src/

# Generate mypy report
uv run mypy --html mypy_report src/

# Fail on any type errors (for CI)
uv run mypy src/ --no-error-summary && echo "✓ Type check passed"
```

### [ADR-010] Benefits

- **Early Error Detection**: Catches bugs before testing
- **Better Refactoring**: Type information enables safe code changes
- **Performance**: Zero runtime overhead
- **Team Alignment**: Enforces consistent typing across codebase

---

## ADR-011: FastMCP Cloud Deployment

**Status**: 🔄 Proposed **Date**: 2026-02-04 **Context**: Deployment & Integration

### [ADR-011] Decision

Use **FastMCP Cloud** for production deployment with automatic scaling and monitoring.

**Rationale**:

- **Managed Service**: No infrastructure management required
- **Auto-Scaling**: Automatically scales based on demand
- **Zero-Downtime Deployment**: Seamless updates and rollbacks
- **Monitoring**: Built-in observability and alerting
- **Integration**: Native integration with Claude Desktop and API clients
- **Cost**: Pay-per-request pricing model (no idle costs)

### [ADR-011] Configuration

```yaml
# .fastmcp/config.yaml
name: open-meteo-mcp
version: "3.2.0"
python_version: "3.12"

# Deployment settings
deployment:
  region: "us-east-1"    # Primary region
  replicas: 2            # Minimum replicas
  max_replicas: 10       # Auto-scale up to 10
  timeout: 30s           # Request timeout
  memory: 512Mi          # Per-replica memory

# Environment variables
environment:
  LOG_LEVEL: "INFO"
  CACHE_TTL: "300"      # 5 minutes

# Health check configuration
health:
  path: "/health"
  interval: 30s
  timeout: 10s

# Monitoring and alerting
monitoring:
  enabled: true
  alerts:
    - error_rate > 0.01   # Alert if >1% errors
    - latency_p95 > 2000  # Alert if P95 > 2s
    - cpu_usage > 80      # Alert if CPU >80%
```

### [ADR-011] Deployment Process

```bash
# 1. Build and test locally
uv sync
uv run pytest tests/
uv run mypy src/

# 2. Deploy to FastMCP Cloud
fastmcp deploy

# 3. Verify deployment
curl https://open-meteo-mcp.fastmcp.cloud/health

# 4. Monitor in dashboard
# https://fastmcp.cloud/dashboard/open-meteo-mcp
```

### [ADR-011] Benefits

- **Reliability**: 99.99% SLA with automatic failover
- **Performance**: CDN-backed responses with <50ms latency
- **Scalability**: Handles 1000+ concurrent requests
- **Compliance**: SOC 2 Type II certified, GDPR compliant
- **Updates**: Zero-downtime deployments with canary releases

### [ADR-011] Monitoring

**Metrics Available**:

```
- Request count (per tool)
- Response latency (p50, p95, p99)
- Error rate and error types
- Active connections
- Memory and CPU usage
- Deployment version and status
```

**Logging**:

- All requests and responses logged
- Structured JSON logs queryable via dashboard
- 30-day retention (configurable)

### [ADR-011] Disaster Recovery

```yaml
# Automatic failover and rollback
deployment:
  health_check_grace_period: 60s  # Wait before marking unhealthy
  readiness_probe:
    enabled: true
    initial_delay: 10s

  # Automatic rollback on failure
  auto_rollback:
    enabled: true
    on_error_rate: 0.05  # >5% errors
    on_latency: 5000     # >5s P95 latency
```

### [ADR-011] Related ADRs

- [ADR-007](#adr-007-package-management-with-uv) - Dependency management
- [ADR-008](#adr-008-structured-logging-with-structlog) - Logging for cloud monitoring

---

## Implementation Roadmap

### Phase 1: Establish Core ADRs ✅ (v3.0.0 - v3.2.0)
- ✅ ADR-001: FastMCP framework
- ✅ ADR-002: Pydantic data models
- ✅ ADR-003: Async/httpx patterns
- ✅ ADR-004: Python 3.11+ requirement
- ✅ ADR-005: Semantic versioning
- ✅ ADR-006: Tool naming conventions
- ✅ ADR-007: uv package management
- ✅ ADR-008: Structlog logging
- ✅ ADR-009: pytest testing
- ✅ ADR-010: MyPy type checking

### Phase 2: Production Deployment (v3.3.0+)
- 🔄 ADR-011: FastMCP Cloud deployment
- 🔄 Performance optimization and benchmarking
- 🔄 Enhanced monitoring and alerting

### Phase 3: Advanced Features (v4.0.0)
- 🔄 ADR-012: Conversation memory and context
- 🔄 ADR-013: Caching strategy (Redis vs in-memory)
- 🔄 ADR-014: Rate limiting and quotas

---

## Related Projects

**Java Version**:
- [open-meteo-mcp-java](../open-meteo-mcp-java/) - Enterprise Java implementation with Spring Boot 5
- Uses: Java 25, Spring AI 3.0, CompletableFuture
- Supersedes Python v2.0.x for enterprise deployments

**TypeScript/Node.js Version**:
- [open-meteo-mcp-node](../open-meteo-mcp-node/) - Modern TypeScript implementation
- Uses: Node.js 20+, type-safe async patterns

**Rust Version**:
- [open-meteo-mcp-rust](../open-meteo-mcp-rust/) - High-performance native implementation
- Uses: Tokio async runtime, Serde serialization

---

## ADR-012: REST API with FastAPI

**Status**: 🔄 Proposed **Date**: 2026-02-04 **Context**: Deployment & Integration

### [ADR-012] Decision

Use **FastAPI** alongside FastMCP to provide HTTP/REST API endpoints alongside the MCP protocol server.

**Rationale**:

- **Separation of Concerns**: REST API for HTTP clients, MCP for AI assistants
- **Industry Standard**: FastAPI is Python's best-in-class web framework with auto-generated OpenAPI
- **Minimal Overhead**: Lightweight framework with zero-copy request validation
- **Async Native**: Built on Starlette, fully async with native httpx integration
- **Developer Experience**: Automatic interactive API documentation (Swagger/ReDoc)
- **No Lock-in**: Can run alongside FastMCP without framework conflicts

### [ADR-012] Endpoints

```python
# Tool endpoints (4 basic endpoints from Java REST API)
GET  /api/tools/weather?latitude=47.3769&longitude=8.5417&forecast_days=7
GET  /api/tools/snow-conditions?latitude=46.0&longitude=7.7
GET  /api/tools/air-quality?latitude=47.3769&longitude=8.5417
POST /api/tools/search-location (body: {"name": "Zurich"})

# Health check
GET  /api/health
```

### [ADR-012] Implementation Pattern

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Open Meteo MCP",
    version="4.0.0",
    description="Weather, snow, and air quality API"
)

# Enable CORS for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
)

# Include routers
app.include_router(tools_router, prefix="/api/tools")
app.include_router(chat_router, prefix="/api/chat")

# Run both FastAPI and FastMCP on same server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)
```

### [ADR-012] Benefits

- **Web Client Support**: Enable browser-based and mobile app integration
- **Auto Documentation**: OpenAPI spec auto-generated and served at `/docs`
- **Type Safety**: Request/response validation via Pydantic models
- **Performance**: Minimal overhead, comparable to FastMCP
- **Compatibility**: Works alongside FastMCP without conflicts

### [ADR-012] Related ADRs

- [ADR-001](#adr-001-use-fastmcp-framework-for-mcp-protocol) - FastMCP for MCP protocol
- [ADR-002](#adr-002-pydantic-v2-for-data-models) - Pydantic for request/response validation
- [ADR-014](#adr-014-service-layer-pattern-for-python) - Service layer used by REST endpoints

---

## ADR-013: Simple Chat API with Anthropic SDK

**Status**: 🔄 Proposed **Date**: 2026-02-04 **Context**: Deployment & Integration

### [ADR-013] Decision

Use **Anthropic SDK directly** (not LangChain) for a simple, lightweight Chat API with manual tool calling.

**Rationale**:

- **Simplicity**: Direct API calls without framework complexity
- **Dependencies**: Minimal (~1 package vs 50+ with LangChain)
- **Control**: Full control over tool calling logic and responses
- **Performance**: No abstraction overhead
- **Maintainability**: Easier to debug and understand
- **Sufficient**: Meets feature parity requirements without over-engineering

### [ADR-013] Excluded Alternatives

| Alternative | Why Not |
|-------------|---------|
| LangChain | 50+ dependencies, complex abstraction, slower |
| OpenAI SDK | Single provider, less feature-rich than Anthropic |
| Custom HTTP | Too much boilerplate, loses SDK benefits |

### [ADR-013] Tool Calling Flow

```python
from anthropic import Anthropic

client = Anthropic()

# 1. Define tool schemas for Claude
tools = [
    {
        "name": "get_weather",
        "description": "Get weather forecast for coordinates",
        "input_schema": {
            "type": "object",
            "properties": {
                "latitude": {"type": "number"},
                "longitude": {"type": "number"},
                "forecast_days": {"type": "integer", "default": 7}
            },
            "required": ["latitude", "longitude"]
        }
    },
    # ... 10 more tools
]

# 2. Send user message with tools
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    tools=tools,
    messages=[
        {"role": "user", "content": "What's the weather in Zurich?"}
    ]
)

# 3. Check for tool use
if response.stop_reason == "tool_use":
    for block in response.content:
        if block.type == "tool_use":
            # Execute our MCP tool
            tool_name = block.name
            tool_input = block.input

            # Call our service layer
            result = await execute_mcp_tool(tool_name, tool_input)

            # Continue conversation with results
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result)
                    }
                ]
            })
```

### [ADR-013] Session Management

```python
# Simple in-memory session storage
sessions: dict[str, dict] = {}

class ChatSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.messages: list = []
        self.created_at = datetime.now()
        self.last_activity = datetime.now()

    def add_message(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})
        self.last_activity = datetime.now()

    def get_conversation(self) -> list:
        return self.messages[-10:]  # Return last 10 messages for context
```

### [ADR-013] Benefits

- **Minimal Dependencies**: Only Anthropic SDK required
- **Fast Implementation**: 2-3 weeks vs 4+ with LangChain
- **Clear Logic**: Easy to understand tool calling flow
- **Debugging**: Direct SDK calls make troubleshooting straightforward
- **Future Ready**: Can upgrade to LangChain in v4.1.0 if needed

### [ADR-013] Limitations (Acceptable for v4.0.0)

- No Redis-backed memory (in-memory only)
- No multi-provider LLM support (Anthropic only)
- No RAG/vector search (simple keyword matching could be added later)
- No streaming responses (batch responses only)
- No conversation summarization for long sessions

### [ADR-013] Future Enhancements (v4.1.0+)

- Upgrade to LangChain for multi-provider support
- Add Redis for distributed session storage
- Implement vector store for RAG
- Add SSE streaming responses
- Conversation summarization for context window management

### [ADR-013] Related ADRs

- [ADR-003](#adr-003-asyncawait-with-httpx-for-api-calls) - Async patterns
- [ADR-012](#adr-012-rest-api-with-fastapi) - FastAPI endpoints for chat
- [ADR-014](#adr-014-service-layer-pattern-for-python) - Service layer for tool execution

---

## ADR-014: Service Layer Pattern for Python

**Status**: 🔄 Proposed **Date**: 2026-02-04 **Context**: Core Architecture

### [ADR-014] Decision

Introduce a **service layer** between tools/routes and the API client, providing business logic, data enrichment, and helper function integration.

**Rationale**:

- **Separation of Concerns**: Tools/routes focus on interface, services handle logic
- **Reusability**: Services can be called from MCP tools, REST endpoints, and Chat API
- **Enrichment**: Centralized data interpretation and formatting
- **Testability**: Service layer can be tested independently
- **Maintainability**: Easier to modify business logic without touching API code

### [ADR-014] Service Layer Structure

```python
# src/open_meteo_mcp/services/weather_service.py

from open_meteo_mcp.client import OpenMeteoClient
from open_meteo_mcp.helpers import (
    interpret_weather_code,
    format_wind_direction,
    format_temperature,
)

class WeatherService:
    """Business logic for weather data."""

    def __init__(self, client: OpenMeteoClient):
        self.client = client

    async def get_weather_enriched(
        self,
        latitude: float,
        longitude: float,
        forecast_days: int = 7
    ) -> dict:
        """Get weather with automatic enrichment."""

        # Fetch raw data
        weather = await self.client.get_weather(
            latitude, longitude, forecast_days
        )

        # Enrich with interpretation
        enrichment = {
            "interpretation": {
                "description": interpret_weather_code(
                    weather.current.weather_code
                ),
                "wind_direction": format_wind_direction(
                    weather.current.wind_direction
                ),
                "temperature_formatted": format_temperature(
                    weather.current.temperature
                ),
            }
        }

        # Return combined
        return {**weather.model_dump(), **enrichment}
```

### [ADR-014] Tool Implementation (Using Service)

```python
@mcp.tool()
async def get_weather(latitude: float, longitude: float) -> dict:
    """Get weather forecast with enrichment."""
    service = WeatherService(client)
    return await service.get_weather_enriched(latitude, longitude)
```

### [ADR-014] REST Endpoint (Using Service)

```python
@router.get("/api/tools/weather")
async def get_weather(
    latitude: float,
    longitude: float,
    forecast_days: int = 7
) -> dict:
    """REST endpoint using same service."""
    service = WeatherService(client)
    return await service.get_weather_enriched(latitude, longitude, forecast_days)
```

### [ADR-014] Service Classes

| Service | Responsibility |
|---------|-----------------|
| `WeatherService` | Weather forecasts, enrichment, interpretation |
| `AirQualityService` | AQI data, pollution levels, health recommendations |
| `LocationService` | Geocoding, location search with fuzzy matching |
| `SnowConditionsService` | Alpine snow depth, snowfall, ski conditions |
| `ChatService` | Chat handler, session management, context |

### [ADR-014] Benefits

- **DRY**: Helper functions applied consistently across APIs
- **Consistency**: Same data enrichment for all interfaces
- **Testability**: Service layer can be unit tested independently
- **Flexibility**: Easy to add new data sources or enhance existing services
- **Documentation**: Services document business logic clearly

### [ADR-014] Related ADRs

- [ADR-012](#adr-012-rest-api-with-fastapi) - REST endpoints using services
- [ADR-013](#adr-013-simple-chat-api-with-anthropic-sdk) - Chat service using tools

---

## ADR-015: Keep meteo__ Tool Prefix for Namespace Isolation

**Status**: 🔄 Proposed **Date**: 2026-02-04 **Context**: Development Standards

### [ADR-015] Decision

Maintain the `meteo__` prefix on all 11 MCP tool names, providing explicit namespace isolation and avoiding breaking changes.

**Rationale**:

- **Namespace Isolation**: `meteo__` prefix clearly identifies weather domain tools
- **No Breaking Changes**: Avoids MAJOR version bump, allows v4.0.0 as feature release
- **Consistency**: Python implementation can differ from Java when justified
- **User Expectations**: Existing Claude Desktop integrations continue working
- **Clarity**: Prefix makes tool purpose explicit in MCP namespaces

### [ADR-015] Tool Naming

All 11 tools retain the `meteo__` prefix:

```
meteo__search_location
meteo__get_weather
meteo__get_snow_conditions
meteo__get_air_quality
meteo__get_weather_alerts
meteo__get_comfort_index
meteo__get_astronomy
meteo__search_location_swiss
meteo__compare_locations
meteo__get_historical_weather
meteo__get_marine_conditions
```

**No changes** to tool names in v4.0.0 or future versions.

### [ADR-015] Migration Impact

**Claude Desktop Users**:
- ✅ Zero impact - Tool names unchanged
- Existing integrations continue working without modification

**API Clients**:
- ✅ No updates required
- Tool names remain stable across versions

**MCP Clients**:
- ✅ No code changes needed
- Tools continue to work as expected

### [ADR-015] Benefits

- **Backward Compatibility**: No breaking changes, smooth upgrades
- **Explicit Namespacing**: Clear domain identification in tool names
- **User Continuity**: Existing workflows unaffected
- **Version Flexibility**: v4.0.0 can be MINOR version (feature release)

### [ADR-015] Divergence from Java

The Python implementation intentionally differs from Java v2.0.2:

| Aspect | Python v4.0.0 | Java v2.0.2 |
|--------|---------------|-------------|
| Tool Prefix | `meteo__*` (kept) | `*` (removed) |
| Rationale | Namespace clarity | Cleaner naming |
| Breaking Changes | None | Prefix removal is breaking |

**Justification**: Each language/implementation can optimize for its ecosystem. Python benefits from explicit namespacing.

### [ADR-015] Implementation

**No code changes required for tool naming**:
- Tools in `server.py` keep `meteo__` prefix
- Service layer unchanged
- REST API endpoints use service layer (no prefix duplication)
- Chat API tool schemas reference tools by name

### [ADR-015] Related ADRs

- [ADR-001](#adr-001-use-fastmcp-framework-for-mcp-protocol) - FastMCP tool definitions
- [ADR-005](#adr-005-semantic-versioning-semver) - Semantic versioning (no major bump needed)

---

## Summary

This ADR compendium now establishes **15 core architectural decisions** for the Python implementation:

**Core Architecture** (4 ADRs):
- FastMCP framework for MCP protocol
- Pydantic v2 for type-safe data models
- Async/await with httpx for API calls
- Python 3.11+ as minimum version

**Development Standards** (4 ADRs):
- Semantic versioning (SemVer)
- Tool naming convention (updated in v4.0.0)
- uv for fast, reliable dependency management
- Remove meteo__ prefix (v4.0.0 breaking change)

**Quality & Observability** (3 ADRs):
- Structured logging with structlog
- pytest with 80%+ coverage target
- MyPy strict type checking

**Deployment & Integration** (2 ADRs):
- FastMCP Cloud for production deployment
- REST API with FastAPI (v4.0.0)

**v4.0.0 Features** (2 ADRs):
- Simple Chat API with Anthropic SDK (v4.0.0)
- Service Layer Pattern for Python (v4.0.0)

---

**Document Status**: v2.0.0 - Updated for v4.0.0 feature parity
**Last Updated**: 2026-02-04
**Maintained By**: Architecture Team

## v4.0.0 Roadmap

These ADRs define the path to feature parity with Java v2.0.2:
- ✅ ADR-012: REST API endpoints for HTTP integration
- ✅ ADR-013: Simple Chat API with tool calling
- ✅ ADR-014: Service layer for data enrichment
- ✅ ADR-015: Remove tool prefix for consistency

**Timeline**: 7-8 weeks to production v4.0.0 with all features
