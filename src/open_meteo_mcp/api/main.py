"""FastAPI application for Open Meteo MCP REST API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .routers import tools


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title="Open Meteo MCP API",
        description="REST API for weather, snow conditions, air quality, and location search",
        version="3.3.1",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(tools.router, prefix="/api/tools", tags=["tools"])

    # Import chat router here to avoid circular imports
    from .routers import chat

    app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

    # Health check endpoint
    @app.get("/api/health")
    async def health_check() -> JSONResponse:
        """Health check endpoint.

        Returns:
            Health status with timestamp
        """
        from datetime import datetime

        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "version": "3.3.1",
                "timestamp": datetime.now().isoformat(),
            },
        )

    # Root endpoint
    @app.get("/")
    async def root() -> JSONResponse:
        """Root endpoint with API information.

        Returns:
            API information and documentation links
        """
        return JSONResponse(
            status_code=200,
            content={
                "message": "Open Meteo MCP REST API",
                "version": "3.3.1",
                "docs": "/api/docs",
                "openapi": "/api/openapi.json",
                "health": "/api/health",
                "endpoints": {
                    "weather": "GET /api/tools/weather",
                    "snow-conditions": "GET /api/tools/snow-conditions",
                    "air-quality": "GET /api/tools/air-quality",
                    "search-location": "POST /api/tools/search-location",
                },
            },
        )

    return app


if __name__ == "__main__":
    import uvicorn

    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8888)
