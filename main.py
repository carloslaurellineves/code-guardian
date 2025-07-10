"""
Main FastAPI application entry point.
"""

from fastapi import FastAPI
import uvicorn
from api.app import create_app

# Create FastAPI application
app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
