"""Gateway application entrypoint.

Create the FastAPI application and register API routes here during implementation.
This module is a scaffold; it does not start an HTTP server.
"""

from fastapi import FastAPI


def create_app() -> FastAPI:
    application = FastAPI(title="StayPilot")

    @application.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        return {
            "status": "ok",
            "service": "staypilot-gateway",
        }

    return application


app = create_app()
