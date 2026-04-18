from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers import upload, generate, export, knowledge_base
from src.core.logger import get_logger

logger = get_logger("api.main")


app = FastAPI(
    title="Exam Generator API",
    version="0.1.0",
    description="API for automatically generating exam questions from course materials.",
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(upload.router, prefix="/api/v1/upload", tags=["Files"])
app.include_router(generate.router, prefix="/api/v1/generate", tags=["Generation"])
app.include_router(export.router, prefix="/api/v1/export", tags=["Export"])
app.include_router(knowledge_base.router, prefix="/api/v1/kb", tags=["Knowledge Base"])


@app.get("/health", tags=["System"])
async def health_check():
    logger.info("Health check endpoint called")
    """
    Check the health of the API and its dependencies.
    """
    return {
        "status": "ok",
        "components": {
            # Placeholder for future checks (e.g., Ollama connectivity)
            "ollama": "unknown"
        },
    }


@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the Exam Generator API"}
