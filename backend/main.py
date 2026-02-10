from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import tasks
from routes import auth
from routes import chat
from config import settings
from sqlmodel import SQLModel
from db import engine
from models import Task, User  # Import models to register them with SQLModel


# Create database tables on startup
def create_db_and_tables():
    SQLModel.metadata.create_all(bind=engine)


# Create FastAPI app with API versioning
app = FastAPI(
    title="Todo Backend API",
    version="1.0.0",
    description="Secure Todo API with user management and task tracking"
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "Authorization"],  # Include Authorization header for JWT
)


# Include the auth, tasks, and chat routers
app.include_router(auth.router, prefix="/api")
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1/chat")


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


def setup_mcp_server():
    """Set up FastMCP server integration with proper multiprocessing handling"""
    try:
        # Check if we're in a subprocess by checking environment variables
        import os
        import sys

        # Skip MCP setup in worker processes to avoid multiprocessing issues
        if os.environ.get("WORKER_ID") or os.environ.get("UVICORN_WORKER_PROCESS"):
            return

        # Additional check: if this is being imported by uvicorn worker, skip
        if hasattr(sys, '_called_from_test') or 'worker' in os.path.basename(sys.argv[0] or ''):
            return

        import fastmcp
        from tools.mcp_tools import mcp

        # Mount the MCP tools server into the FastAPI app
        mcp_app = mcp.http_app(path="/mcp")

        # Mount MCP routes at /mcp path
        app.mount("/mcp", mcp_app)

        print("FastMCP server mounted at /mcp")
    except ImportError:
        print("FastMCP not available, running without MCP server")
    except Exception as e:
        print(f"Error initializing FastMCP: {e}")


# Setup MCP server only when running directly (not in worker processes)
if __name__ == "__main__":
    setup_mcp_server()

    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["."]
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["."]
    )