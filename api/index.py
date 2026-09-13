import os
import sys

# Permet à Python de trouver main.py et agents.py situés à la racine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app as fastapi_app


# Wrapper ASGI exécuté AVANT que FastAPI ne résolve la route
class VercelPathMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            # Vercel fournit le vrai chemin d'origine demandé par le client
            matched_path = headers.get(b"x-matched-path", b"").decode("utf-8")
            if matched_path:
                scope["path"] = matched_path.split("?")[0]
            elif scope.get("path") in ["/api", "/api/", "/api/index.py", "/api/index"]:
                scope["path"] = "/"
        await self.app(scope, receive, send)


app = VercelPathMiddleware(fastapi_app)
