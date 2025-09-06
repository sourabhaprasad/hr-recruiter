
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import jd, resume, dashboard, ai_assistant, candidate
from core.db import create_tables
from core.models import *  # Import all models to ensure they're registered

app = FastAPI(title="Talent Matcher API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
create_tables()

# Include routers
app.include_router(jd.router, prefix="/jd", tags=["Job Descriptions"])
app.include_router(resume.router, prefix="/resume", tags=["Resumes"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(ai_assistant.router)
app.include_router(candidate.router, prefix="/candidate", tags=["Candidates"])

@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "Talent Matcher API is running",
        "version": "1.0.0"
    }

@app.get("/health")
def detailed_health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "services": ["jd", "resume", "dashboard", "matching", "email"]
    }
