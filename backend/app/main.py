import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, chat, admin
from app.config import settings

# Create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CampusMind - College RAG Chatbot API",
    description="AI-powered College Information Assistant grounded strictly in college documents.",
    version="1.0.0"
)

# Global error handler to ensure all errors return proper JSON
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"}
    )

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(admin.router)

@app.get("/")
def root():
    return {
        "message": "Welcome to CampusMind API",
        "status": "online",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
