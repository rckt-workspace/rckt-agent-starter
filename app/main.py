from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.core.config import settings
from app.api import health, chat

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Simple agent starter for educational purposes",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
app.include_router(health.router)
app.include_router(chat.router)

# Static files and frontend SPA
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if (frontend_dist / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")


@app.get("/")
async def root(request: Request):
    # If a browser requests HTML and frontend is built, serve the SPA
    if "text/html" in request.headers.get("accept", "") and (frontend_dist / "index.html").exists():
        return FileResponse(str(frontend_dist / "index.html"))

    return {
        "message": f"Welcome to {settings.app_name}",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/{path:path}")
async def serve_spa_or_static(path: str, request: Request):
    # Do not intercept API or documentation routes
    if path.startswith(("api", "health", "docs", "openapi.json", "redoc")):
        raise HTTPException(status_code=404, detail="Not Found")

    target_file = frontend_dist / path
    if target_file.is_file():
        return FileResponse(str(target_file))

    # SPA client-side routing fallback for HTML requests
    if (frontend_dist / "index.html").exists() and "text/html" in request.headers.get("accept", ""):
        return FileResponse(str(frontend_dist / "index.html"))

    raise HTTPException(status_code=404, detail="Not Found")
