from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from starlette.requests import Request
import os
import logging

# Import routers
from api.routers import chat, upload, admin, health
from database.connections.db_manager import initialize_databases, close_databases

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_middleware(app: FastAPI):
    """Set up CORS and other middleware"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

def setup_routes(app: FastAPI):
    """Set up API routes"""
    app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
    app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
    app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
    app.include_router(health.router, prefix="/api/health", tags=["health"])

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title="Agno AI Backend",
        description="AI-powered chat service with video search capabilities",
        version="1.0.0"
    )

    # Database lifecycle management
    @app.on_event("startup")
    async def on_startup():
        """Initialize databases on startup"""
        try:
            await initialize_databases()
            logger.info("Application started successfully")
        except Exception as e:
            logger.error(f"Failed to initialize databases: {e}")
            raise

    @app.on_event("shutdown")
    async def on_shutdown():
        """Close database connections on shutdown"""
        try:
            await close_databases()
            logger.info("Application shutdown successfully")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

    # Set up middleware and routes
    setup_middleware(app)
    setup_routes(app)

    # Static files serving
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    if os.path.exists(static_dir):
        app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

    @app.exception_handler(404)
    async def custom_404_handler(request: Request, exc):
        """Custom 404 handler for SPA routing"""
        if request.url.path.startswith("/api/"):
            return JSONResponse(status_code=404, content={"detail": "API endpoint not found"})
        
        # For non-API routes, serve index.html for SPA routing
        index_path = os.path.join(static_dir, 'index.html')
        if os.path.exists(index_path):
            return FileResponse(index_path)
        
        return JSONResponse(status_code=404, content={"detail": "Page not found"})

    @app.get("/")
    async def root():
        """Root endpoint"""
        return {"message": "Agno AI Backend API", "status": "running"}

    return app

# Create the app instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )