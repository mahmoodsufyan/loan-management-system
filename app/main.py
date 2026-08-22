import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from app.api.v1.api import api_router
from app.db.session import init_db

# Initialize database schema on startup
init_db()

app = FastAPI(
    title="Loan & Amortization Engine API",
    description="""
## Enterprise Financial & Amortization Core Engine
Provides high-precision loan amortization schedules, early settlement rebate calculations, multi-stage credit approval state machines, and dynamic PDF contract exports.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", tags=["Dashboard"], response_class=HTMLResponse)
def serve_root():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Loan & Amortization Engine API is Running</h1><p><a href='/docs'>Swagger API Docs</a></p>")

@app.get("/dashboard", tags=["Dashboard"], response_class=HTMLResponse)
def serve_dashboard():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Dashboard HTML not found</h1>", status_code=404)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "Loan & Amortization Engine API",
        "version": "1.0.0",
        "docs": "/docs",
        "dashboard": "/dashboard"
    }

