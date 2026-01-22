# Changelog

All notable changes to open-meteo-mcp will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.2.0] - 2026-01-22

### Changed
- **Updated swiss-ai-mcp-commons to v1.1.0** with HTTP content negotiation support
- Enhanced JSON serialization capabilities with automatic compression
- Added framework integration helpers for FastAPI, Flask, and Starlette
- Improved bandwidth efficiency with smart gzip compression (60-80% reduction)

### Performance
- Content negotiation enables automatic response compression when beneficial
- Configurable compression thresholds (default: 1024 bytes)
- Backward compatible with existing API consumers

## [3.1.0] - 2026-01-22

### Added
- Production release with comprehensive weather and snow condition queries
- MCP tools for weather forecasts, ski resort conditions, and location search
- MCP resources for documentation and API schemas
- Full test coverage with 129 passing tests
- Structured logging and error handling
- HTTP/SSE transport support

### Features
- Current weather and 7-day forecasts
- Hourly weather data with detailed parameters
- Ski resort snow conditions and webcams
- Location search and reverse geocoding
- Multi-location support worldwide

[3.2.0]: https://github.com/schlpbch/open-meteo-mcp/compare/v3.1.0...v3.2.0
[3.1.0]: https://github.com/schlpbch/open-meteo-mcp/releases/tag/v3.1.0
