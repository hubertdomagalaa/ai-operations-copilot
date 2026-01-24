"""
FastAPI Application Entry Point
===============================

This module creates and configures the FastAPI application instance.
It serves as the main entry point for the backend API.

WHY THIS FILE EXISTS:
- Centralizes app configuration (CORS, middleware, exception handlers)
- Registers all routers from the api package
- Provides a clean entry point for uvicorn or other ASGI servers

USAGE:
    uvicorn backend.api.main:app --reload
"""

from fastapi import FastAPI

# TODO: Import routers when implemented
# from backend.api.routes import tickets, agents, health

app = FastAPI(
    title="AI Operations Copilot API",
    description="Internal API for AI-assisted support ticket processing",
    version="0.1.0",
)


# TODO: Configure CORS middleware for internal access
# TODO: Add exception handlers for consistent error responses
# TODO: Add request logging middleware


@app.get("/")
async def root():
    """
    Root endpoint — returns basic API information.
    
    This is a simple health check / info endpoint.
    """
    return {
        "service": "AI Operations Copilot",
        "version": "0.1.0",
        "status": "skeleton",
    }


# TODO: Include routers
# app.include_router(tickets.router, prefix="/tickets", tags=["tickets"])
# app.include_router(agents.router, prefix="/agents", tags=["agents"])
# app.include_router(health.router, prefix="/health", tags=["health"])
