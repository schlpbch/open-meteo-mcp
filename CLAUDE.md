# CLAUDE.md - Project Guidelines

## Project Overview

**open-meteo-mcp** is a Model Context Protocol (MCP) server providing weather, snow conditions, air quality, and location services via the Open-Meteo API.

- **Version**: 3.3.0
- **Python**: 3.11+
- **Framework**: FastMCP
- **Status**: Production-ready with full type safety and automated quality checks

## Development Standards

### Code Quality (Phase 7 Complete)

#### Type Safety
- **Requirement**: 0 mypy errors across entire codebase
- **Tool**: `mypy src/`
- **Config**: Strict mode (`disallow_untyped_defs`, `disallow_incomplete_defs`)
- **Pre-commit**: Mypy checks run but are non-blocking (warns on issues)

#### Code Formatting
- **Tool**: Black (v24+)
- **Command**: `uv run black src/ tests/`
- **Pre-commit**: Blocking check - prevents commits with formatting issues
- **Coverage**: 100% of codebase

#### Linting
- **Tool**: Ruff
- **Command**: `uv run ruff check src/ tests/`
- **Pre-commit**: Blocking check - prevents commits with linting violations
- **Coverage**: 100% of codebase

### Pre-commit Hooks

All commits automatically run three quality checks:

```bash
.git/hooks/pre-commit
├── Black formatting check (blocking)
├── Ruff linting check (blocking)
└── Mypy type checking (non-blocking, warns on issues)
```

**Install hooks**:
```bash
# Hooks are auto-installed; manually verify with:
cat .git/hooks/pre-commit
```

**Bypass hooks** (only in emergencies):
```bash
git commit --no-verify  # Not recommended - only for critical fixes
```

## Testing

### Test Execution
```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage report
uv run pytest --cov=src --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_client.py -v
```

### Coverage Requirements
- **Minimum**: 85% across codebase
- **Target**: 90% (current: 90%)
- **Files to maintain**:
  - `client.py`: 98%
  - `models.py`: 99%
  - `server.py`: 90%
  - `services/`: 70%+

### Test Organization
```
tests/
├── test_client.py       # OpenMeteoClient tests
├── test_models.py       # Pydantic model tests
├── test_server.py       # FastMCP server tests
├── test_helpers.py      # Utility function tests
├── test_services.py     # Service layer tests
├── test_rest_api.py     # REST API tests
└── test_chat_handler.py # Chat handler tests
```

## Architecture

### Core Components

**`src/open_meteo_mcp/`**
- `server.py`: FastMCP server with tools, resources, prompts
- `client.py`: Async HTTP client for Open-Meteo API
- `models.py`: Pydantic data models for type safety
- `helpers.py`: Utility functions (weather interpretation, calculations)
- `services/`: Service layer for business logic
  - `base.py`: Base service class with common enrichment patterns
  - `weather_service.py`: Weather data enrichment
  - `air_quality_service.py`: Air quality data enrichment
  - `location_service.py`: Location data enrichment

### MCP Structure
- **Tools**: 11 tools for weather, snow, air quality, locations
- **Resources**: 4 resources with reference data (weather codes, parameters, AQI, locations)
- **Prompts**: 3 prompts for ski trips, outdoor activities, travel planning

## Version Management

### Version Files
Update in these files for releases:
1. `pyproject.toml`: `version = "X.Y.Z"`
2. `src/open_meteo_mcp/__init__.py`: `__version__ = "X.Y.Z"`
3. `src/open_meteo_mcp/api/main.py`: `version="X.Y.Z"` (3 occurrences)
4. `src/open_meteo_mcp/client.py`: User-Agent header

### Release Process
1. Update version in all 4 files
2. Commit with message: `Release vX.Y.Z: <description>`
3. Create git tag: `git tag -a vX.Y.Z -m "<release notes>"`
4. Push commit and tag: `git push origin main && git push origin vX.Y.Z`
5. Create GitHub release: `gh release create vX.Y.Z --notes "..."`

## Dependency Management

### Dependencies
- **fastmcp**: MCP server framework
- **fastapi**: REST API (optional)
- **uvicorn**: ASGI server (optional)
- **httpx**: Async HTTP client
- **pydantic**: Data validation
- **structlog**: Structured logging
- **pytz**: Timezone handling

### Dev Dependencies
- **pytest**: Testing framework
- **pytest-asyncio**: Async test support
- **pytest-httpx**: HTTP mocking
- **pytest-cov**: Coverage reporting
- **black**: Code formatting
- **ruff**: Linting
- **mypy**: Type checking

### Package Manager
- **uv**: Fast Python package manager (required)
- **Command**: `uv sync` - installs dependencies from `pyproject.toml`

## Common Tasks

### Add a New Tool
1. Define async function with `@mcp.tool()` decorator in `server.py`
2. Add type hints for all parameters
3. Implement error handling with try/except
4. Add docstring with examples
5. Write tests in `test_server.py`
6. Verify coverage remains 90%+

### Fix Type Errors
1. Run `uv run mypy src/` to find errors
2. Add type annotations or use `cast()` for unavoidable `Any` returns
3. Verify with `uv run mypy src/` (must show no errors)
4. Pre-commit hook will enforce on next commit

### Update Documentation
1. Update docstrings in code
2. Update README.md for user-facing changes
3. Keep CLAUDE.md synchronized with processes
4. Run tests to verify examples are accurate

## Troubleshooting

### Pre-commit Hook Fails
```bash
# Check formatting
uv run black src/ tests/ --check

# Auto-fix formatting
uv run black src/ tests/

# Check linting
uv run ruff check src/ tests/

# Fix linting issues
uv run ruff check src/ tests/ --fix

# Check types
uv run mypy src/
```

### Tests Fail
```bash
# Run with verbose output
uv run pytest tests/ -vv

# Run specific test
uv run pytest tests/test_file.py::test_function -vv

# Show print statements
uv run pytest tests/ -s
```

### Type Checking Issues
```bash
# Check all files
uv run mypy src/

# Check specific file
uv run mypy src/open_meteo_mcp/client.py

# Ignore specific error (as last resort)
# Add: # type: ignore[error-code]
```

## Best Practices

### Code Style
- Use type hints on all function signatures
- Keep functions focused and testable
- Use descriptive variable names
- Add docstrings to public functions
- Follow PEP 8 conventions (enforced by black)

### Error Handling
- Use specific exception types
- Log errors with structlog
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
- Maintain version history in CHANGELOG (if exists)

## Resources

- **FastMCP Docs**: https://github.com/modelcontextprotocol/python-sdk
- **Open-Meteo API**: https://open-meteo.com/en/docs
- **Python MCP Spec**: https://spec.modelcontextprotocol.io/
- **Pydantic Docs**: https://docs.pydantic.dev/
- **Black Formatter**: https://black.readthedocs.io/

## Contact & Support

For questions or issues:
1. Check existing issues on GitHub
2. Review CLAUDE.md and project structure
3. Run tests to verify environment
4. Create detailed GitHub issue with:
   - Python version
   - Steps to reproduce
   - Expected vs actual behavior
   - Relevant logs/errors

---

**Last Updated**: Phase 7 Complete (v3.3.0)
**Maintained By**: Development Team
**Status**: Production Ready
