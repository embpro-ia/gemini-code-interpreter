import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ GEMINI_API_KEY introuvable dans le fichier .env")
    exit(1)

client = genai.Client(api_key=api_key)
model = "gemini-3.5-flash-lite"

print(f"🔬 Diagnostic des quotas avec le modèle '{model}' :\n")

# Étape 1 : Appel standard sans aucun outil
print("1️⃣ Test : Génération simple de texte (aucun outil)...")
try:
    res = client.models.generate_content(
        model=model,
        contents="Réponds simplement 'OK'."
    )
    print(f"   ✅ SUCCÈS : Réponse reçue -> {res.text.strip()}")
except Exception as e:
    print(f"   ❌ ÉCHEC : {e}")

# Étape 2 : Appel avec Code Execution uniquement
print("\n2️⃣ Test : Code Execution uniquement...")
try:
    res = client.models.generate_content(
        model=model,
        contents="Calcule 25 * 40 avec Python.",
        config=types.GenerateContentConfig(
            tools=[types.Tool(code_execution=types.ToolCodeExecution())]
        )
    )
    print(f"   ✅ SUCCÈS : Réponse reçue -> {res.text.strip()[:80]}...")
except Exception as e:
    print(f"   ❌ ÉCHEC : {e}")

# Étape 3 : Appel avec Google Search uniquement
print("\n3️⃣ Test : Google Search Grounding uniquement...")
try:
    res = client.models.generate_content(
        model=model,
        contents="Quel est le cours de l'action Apple aujourd'hui ?",
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())]
        )
    )
    print(f"   ✅ SUCCÈS : Réponse reçue -> {res.text.strip()[:80]}...")
except Exception as e:
    print(f"   ❌ ÉCHEC : {e}")

print("\n--- Fin du diagnostic ---")
