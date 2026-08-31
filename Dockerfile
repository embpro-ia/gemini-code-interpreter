# Image de base Python 3.11 légère
FROM python:3.11-slim

# Forcer l'affichage direct des logs et désactiver les .pyc
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Répertoire de travail
WORKDIR /app

# Copier et installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code source
COPY . .

# Exposer le port
EXPOSE 8080

# Démarrer FastAPI avec Uvicorn sur le port dynamique fourni par Cloud Run ($PORT)
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
