import os
import sys
from starlette.requests import Request
from starlette.responses import HTMLResponse

# Permet à Python de trouver main.py et agents.py situés à la racine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, home_ui


@app.middleware("http")
async def vercel_routing_middleware(request: Request, call_next):
    # Vercel transmet le vrai chemin demandé par le client dans l'en-tête HTTP x-matched-path
    matched_path = request.headers.get("x-matched-path")
    if matched_path:
        request.scope["path"] = matched_path.split("?")[0]
    return await call_next(request)


# Route de secours directe si Vercel appelle directement /api/index.py
@app.get("/api/index.py", response_class=HTMLResponse, include_in_schema=False)
def fallback_index():
    return home_ui()
