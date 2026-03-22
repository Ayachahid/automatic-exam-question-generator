from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers import upload, generate

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


@app.get("/health", tags=["System"])
async def health_check():
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
    return {"message": "Welcome to the Exam Generator API"}
