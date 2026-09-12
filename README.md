# 🤖 Gemini Code Interpreter Agent API

Microservice FastAPI propulsé par Google Gemini (`gemini-3.5-flash-lite`) avec exécution de code Python sandboxée (Code Interpreter).

## 🚀 Fonctionnalités
- Exécution de code Python native et sandboxée par Google Gemini.
- Calculs mathématiques, simulations, manipulation de données et algorithmes.
- Interface Web interactive directe intégrée sur `/`.
- Documentation OpenAPI / Swagger interactive sur `/docs`.
- Endpoint de santé sur `/health`.
- Endpoint d'interrogation sur `POST /api/v1/query`.

## ⚙️ Variables d'environnement
- `GEMINI_API_KEY` : Clé API Google AI Studio requise.
- `PORT` : Port d'écoute du serveur (par défaut `8000`).

## 📦 Déploiement sur Koyeb
1. Connectez votre dépôt GitHub à Koyeb.
2. Choisissez le mode de déploiement **Dockerfile**.
3. Définissez la variable d'environnement secrète `GEMINI_API_KEY`.
4. Le port par défaut est `8000`.
