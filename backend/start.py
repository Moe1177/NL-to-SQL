#!/usr/bin/env python3
"""
Startup script for the Natural Language to SQL FastAPI backend.
"""

import os
import sys

import uvicorn

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

if __name__ == "__main__":
    # Run the FastAPI application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info",
    )
