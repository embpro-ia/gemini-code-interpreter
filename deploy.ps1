# Script d'aide pour déployer Google Search & Code Interpreter Agent sur Google Cloud Run
# 
# Instructions d'utilisation :
# 1. Ouvrez votre terminal PowerShell.
# 2. Assurez-vous d'être connecté à GCP : gcloud auth login
# 3. Choisissez votre projet : gcloud config set project VOTRE_PROJECT_ID
# 4. Exécutez ce script : .\deploy.ps1

$PROJECT_NAME = "google-search-interpreter-agent"
$REGION = "europe-west1"

Write-Host "🚀 Déploiement de $PROJECT_NAME sur Cloud Run ($REGION)..." -ForegroundColor Green

gcloud run deploy $PROJECT_NAME `
  --source . `
  --region $REGION `
  --allow-unauthenticated `
  --set-env-vars "GEMINI_API_KEY=$env:GEMINI_API_KEY"

Write-Host "✅ Déploiement terminé !" -ForegroundColor Green
