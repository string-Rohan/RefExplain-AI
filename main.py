"""
RefExplain AI - Root ASGI Entry Point
Exposes the FastAPI 'app' from backend/main.py for Render and root-level deployments.
"""
import os
import sys

# Ensure the backend directory is on sys.path so modules like rules, ai_engine are discoverable
backend_dir = os.path.join(os.path.dirname(__file__), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from backend.main import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)

