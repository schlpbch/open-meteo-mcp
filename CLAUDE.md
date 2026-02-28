# CLAUDE.md - Project Guidelines

## Project Overview

**open-meteo-mcp** is a Model Context Protocol (MCP) server providing weather, snow conditions, air quality, and location services via the Open-Meteo API. This Python implementation extends the base functionality with a REST API and integrated chat interface.

- **Version**: 3.3.0
- **Python**: 3.13+
- **Framework**: FastMCP 3.0+ with FastAPI (optional REST API)
- **Status**: Production-ready with strict type safety
- **Scope**: Weather, snow, air quality, location services
- **Additional Features**: REST API, chat handler with Claude integration

### Relationship to Reference Implementation

This is **the primary/extended Python implementation** of the Open Meteo MCP server:

| Aspect | Reference (TypeScript) | Python Extended |
|--------|---------|---------|
| **Language** | TypeScript/Node.js | Python 3.13+ |
| **Core Tools** | 11 | 11 (identical) |
| **Reference Resources** | 4 | 4 (identical) |
| **REST API** | ✗ | ✓ (NEW) |
| **Chat Interface** | ✗ | ✓ Claude integration |
| **Service Layer** | ✓ | ✓ Enriched |
| **Async Support** | ✓ | ✓ |
| **Type Safety** | ✓ strict | ✓ strict |

**Key Difference**: This version adds optional REST API endpoints and a chat handler for Claude AI integration, making it suitable for both MCP and web/chat applications.

## Development Standards

### Code Quality (Production-Grade)

#### Type Safety
- **Requirement**: 0 mypy errors across entire codebase
- **Strictness**: STRICT mode (`disallow_untyped_defs = true`)
- **Tool**: `uv run mypy src/`
- **Pre-commit**: Mypy checks run but are non-blocking

#### Code Formatting
- **Status**: Post-MVP phase (ruff configuration pending)
- **Tool**: Ruff (listed in dependencies, configuration commented)
- **Future**: Will enforce 88 char line-length with ruff formatter
- **Current**: Codebase follows Python conventions; ruff enforcement is pending

#### Linting
- **Tool**: Ruff (listed in dependencies but not yet enforced)
- **Command**: `uv run ruff check src/ tests/` (when enabled)
- **Status**: Configuration pending post-MVP

### Pre-commit Hooks (Recommended)

```bash
# Recommended pre-commit setup (not yet enforced)
.git/hooks/pre-commit
├── Ruff linting check (pending)
├── Ruff formatting check (pending)
└── Mypy type checking (non-blocking)
```

**Setup**:
```bash
# Manual checks available now
uv run mypy src/
uv run ruff check src/ tests/
```

## Testing

### Test Execution
```bash
# Run all tests with coverage
uv run pytest tests/ -v --cov=open_meteo_mcp --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_server.py -v

# Run REST API tests
uv run pytest tests/test_rest_api.py -v

# Run chat handler tests
uv run pytest tests/test_chat_handler.py -v
```

### Coverage Requirements
- **Minimum**: 85% across codebase
- **Target**: 90%+
- **Current**: ~90%
- **Tracked**: All test files in tests/ directory

### Test Organization
```
tests/
├── test_server.py              # FastMCP server registration and tools
├── test_client.py              # OpenMeteoClient HTTP client
├── test_models.py              # Pydantic model validation
├── test_helpers.py             # Utility function tests
├── test_services.py            # Service layer tests
├── test_geocoding.py           # Location search functionality
├── test_air_quality.py         # Air quality data enrichment
├── test_meteo_improvements.py  # Weather feature tests
├── test_integration.py         # End-to-end workflows
├── test_rest_api.py            # FastAPI REST endpoints (NEW)
└── test_chat_handler.py        # Claude chat integration (NEW)
```

## Architecture

### Core Components

**MCP Server Layer** (`server.py`)
```
FastMCP initialization
├── Tool registration (11 tools)
├── Resource registration (4 resources)
├── Prompt registration (3 prompts)
└── Service layer dependency injection
```

**Service Layer** (business logic with enrichment patterns)
```
services/
├── base.py                     # BaseService with common patterns
├── weather_service.py          # Weather forecast enrichment
├── air_quality_service.py      # Air quality data enrichment
└── location_service.py         # Location/geocoding enrichment
```

**HTTP Client** (`client.py`)
```
OpenMeteoClient
├── Async HTTP client (httpx)
├── Error handling decorator pattern
├── API call orchestration
└── Response validation (Pydantic)
```

**REST API Layer** (`api/` - NEW)
```
FastAPI application
├── api/main.py              # FastAPI app configuration
└── api/routers/
    ├── tools.py             # MCP tools as HTTP endpoints
    └── chat.py              # Chat handler routes
```

**Chat Interface** (`chat/` - NEW)
```
Chat handler for Claude integration
├── handler.py               # Claude chat orchestration
├── tools.py                 # Tool definitions for chat
└── sessions/                # Chat session management
```

### Data Models (`models.py`)
- Pydantic models for all API responses
- Type-safe data validation
- Automatic JSON serialization

### Helpers (`helpers.py`)
- Weather code interpretation
- Temperature unit conversion
- Alert threshold definitions
- Utility functions

## Version Management

### Version Files
Update in these files for releases:
1. `pyproject.toml`: `version = "X.Y.Z"`
2. `src/open_meteo_mcp/__init__.py`: `__version__ = "X.Y.Z"`
3. `src/open_meteo_mcp/api/main.py`: `version="X.Y.Z"` (3 occurrences)
4. `src/open_meteo_mcp/client.py`: User-Agent header (optional)

### Release Process
1. Update version in all 4 files
2. Commit with message: `Release vX.Y.Z: <description>`
3. Create git tag: `git tag -a vX.Y.Z -m "<release notes>"`
4. Push commit and tag: `git push origin main && git push origin vX.Y.Z`
5. Create GitHub release: `gh release create vX.Y.Z --notes "..."`

## Dependency Management

### Core Dependencies
- **fastmcp**: MCP server framework (3.0+)
- **httpx**: Async HTTP client for Open-Meteo API
- **pydantic**: Data validation (2.0+)
- **structlog**: Structured logging
- **pytz**: Timezone handling

### Optional Dependencies
- **fastapi**: REST API framework (optional)
- **uvicorn**: ASGI server (optional, for REST API)
- **anthropic**: Claude AI client (optional, for chat features)
- **prometheus-client**: Metrics (optional)
- **slowapi**: Rate limiting (optional)

### Dev Dependencies
- **pytest**: Testing framework
- **pytest-asyncio**: Async test support
- **pytest-httpx**: HTTP mocking
- **pytest-cov**: Coverage reporting
- **mypy**: Type checking
- **ruff**: Linting/formatting (pending full configuration)

### Package Manager
- **uv**: Fast Python package manager (required)
- **Command**: `uv sync` - installs dependencies from `pyproject.toml`

## Common Tasks

### Add a New Weather Tool

1. Define async function with `@mcp.tool()` decorator in `server.py`
2. Add type hints for all parameters
3. Create service method for business logic (e.g., `weather_service.py`)
4. Implement error handling with try/except
5. Add docstring with examples
6. Write tests in `test_server.py`
7. If applicable, add REST API route in `api/routers/tools.py`

### Fix Type Errors

```bash
# Find all type errors
uv run mypy src/ --show-error-codes

# Check specific file
uv run mypy src/open_meteo_mcp/server.py

# Fix errors by adding type annotations
def get_weather(...) -> dict[str, Any]:
    ...
```

### Add REST API Endpoint

1. Create route in `api/routers/tools.py` or `api/routers/chat.py`
2. Use FastAPI `@app.get()` or `@app.post()` decorator
3. Add request/response Pydantic models
4. Delegate to MCP tools via `service` layer
5. Write tests in `tests/test_rest_api.py`

### Integrate New Tool with Chat

1. Define tool in `chat/tools.py` with Claude API schema
2. Register tool with Claude client in `chat/handler.py`
3. Implement tool execution in handler
4. Write tests in `tests/test_chat_handler.py`

## Testing Patterns

### Unit Tests
- Test individual service methods
- Test data validation (Pydantic models)
- Test utility functions
- Mock HTTP calls

### Integration Tests
- Test complete tool workflows
- Test service layer caching
- Test error handling
- Real API calls (optional)

### API Tests
- Test REST endpoints
- Test request validation
- Test response serialization
- Test error responses

### Chat Tests
- Test Claude integration
- Test tool execution within chat context
- Test session management
- Test message formatting

## Troubleshooting

### Type Checking Fails

```bash
# Find all type errors
uv run mypy src/ --show-error-codes

# Check specific file
uv run mypy src/open_meteo_mcp/server.py

# Show detailed error information
uv run mypy src/ --pretty
```

### Tests Fail After Code Changes

```bash
# Run tests with verbose output
uv run pytest tests/ -vv

# Run specific failing test
uv run pytest tests/test_file.py::test_name -vv

# Show print statements during test
uv run pytest tests/ -s

# Run with coverage to find untested paths
uv run pytest tests/ --cov=open_meteo_mcp --cov-report=html
```

### REST API Not Starting

```bash
# Check FastAPI configuration
cd /home/schlpbch/code/open-meteo-mcp-py
uv run python -m open_meteo_mcp.api.main

# Test REST API directly
curl http://localhost:8000/health
```

### Chat Handler Not Responding

```bash
# Check Claude API credentials
export ANTHROPIC_API_KEY="your-key"

# Test chat handler
uv run python -c "
from open_meteo_mcp.chat.handler import ChatHandler
handler = ChatHandler()
print('Handler initialized')
"
```

## Best Practices

### Code Style
- Use type hints on all function signatures (enforced by mypy --strict)
- Keep functions focused and testable
- Use descriptive variable names
- Add docstrings to public functions
- Follow PEP 8 conventions

### Error Handling
- Use specific exception types
- Log errors with structlog for debugging
- Raise errors at system boundaries (API calls)
- Don't suppress errors silently
- Return sensible defaults for non-critical operations

### Testing
- Write tests before/with code (TDD preferred)
- Mock external API calls
- Test both happy path and error cases
- Keep test names descriptive
- Maintain test independence

### Documentation
- Keep README up to date
- Document breaking changes
- Include examples in docstrings
- Maintain version history
- Document architectural decisions

### Performance
- Cache frequently accessed data
- Use connection pooling for HTTP (handled by httpx)
- Profile code for bottlenecks
- Monitor metrics in production

## Extended Features: REST API

### FastAPI Integration
The server can optionally run as a REST API for web/chat applications:

```bash
# Start REST API server
uv run python -m uvicorn open_meteo_mcp.api.main:app --host 0.0.0.0 --port 8000
```

### Available REST Endpoints
- `GET /health` - Health check
- `GET /tools` - List available MCP tools
- `POST /tools/{tool_name}` - Execute MCP tool
- `POST /chat` - Chat with Claude using MCP tools (if Anthropic key set)

See `api/routers/` for full endpoint definitions.

## Extended Features: Chat Integration

### Claude Integration
The server can integrate with Claude AI to orchestrate tools within conversations:

```python
from open_meteo_mcp.chat.handler import ChatHandler

handler = ChatHandler()
response = await handler.chat(
    user_message="What's the weather in Zurich?",
    session_id="session-123"
)
```

### Session Management
Chat sessions are tracked in `chat/sessions/` with persistent state:
- User message history
- Tool execution results
- Claude conversation context

## Resources

- **FastMCP Docs**: https://github.com/modelcontextprotocol/python-sdk
- **Open-Meteo API**: https://open-meteo.com/en/docs
- **Python MCP Spec**: https://spec.modelcontextprotocol.io/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Pydantic Docs**: https://docs.pydantic.dev/
- **Anthropic SDK**: https://github.com/anthropics/anthropic-sdk-python

## Contact & Support

For questions or issues:
1. Check existing issues on GitHub
2. Review CLAUDE.md and project structure
3. Run tests to verify environment: `uv run pytest tests/ -v`
4. Create detailed GitHub issue with:
   - Python version and environment
   - Steps to reproduce
   - Expected vs actual behavior
   - Relevant logs/errors
   - Data sample if weather-related

---

**Last Updated**: v3.3.0
**Maintained By**: Development Team
**Status**: Production Ready - Extended with REST API & Chat
**Python Minimum**: 3.13
**FastMCP**: 3.0+
