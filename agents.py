import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

SYSTEM_INSTRUCTION = """
Tu es un assistant expert en analyse de données et en calculs de haute précision avec Code Interpreter.
- Utilise l'exécution de code Python (Code Execution) pour effectuer des calculs précis, manipuler des données numériques ou simuler des algorithmes.
- Explique clairement ta démarche, montre les étapes importantes et reste rigoureux et factuel.
"""

def get_client() -> genai.Client:
    """Initialise le client Google GenAI avec la clé API."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY est manquante. Définissez-la dans vos variables d'environnement ou fichier .env.")
    return genai.Client(api_key=api_key)


def run_analyst_agent(prompt: str, model_name: str = "gemini-3.5-flash-lite") -> dict:
    """
    Exécute l'agent d'analyse avec l'outil natif de Code Execution Python de Gemini.
    Retourne la réponse textuelle et les détails d'exécution de code.
    """
    client = get_client()

    # Outil de Code Execution Python natif (inclus sans surcoût/quota search)
    tools = [
        types.Tool(code_execution=types.ToolCodeExecution())
    ]

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        tools=tools,
    )

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=config,
    )

    # Extraction des détails de code exécuté
    code_details = []
    if response.candidates and response.candidates[0].content:
        parts = getattr(response.candidates[0].content, "parts", []) or []
        for part in parts:
            exec_code = getattr(part, "executable_code", None)
            if exec_code:
                code_details.append({
                    "type": "input_code",
                    "language": getattr(exec_code, "language", "PYTHON"),
                    "code": getattr(exec_code, "code", "")
                })
            exec_result = getattr(part, "code_execution_result", None)
            if exec_result:
                code_details.append({
                    "type": "execution_result",
                    "outcome": getattr(exec_result, "outcome", ""),
                    "output": getattr(exec_result, "output", "")
                })

    return {
        "text": response.text or "",
        "code_details": code_details
    }


# Alias de compatibilité
run_assistant = run_analyst_agent


if __name__ == "__main__":
    test_prompt = "Génère les 10 premiers nombres premiers, calcule leur somme et leur moyenne en utilisant Python."
    print(f"--- Prompt utilisateur ---\n{test_prompt}\n")
    
    result = run_analyst_agent(test_prompt)
    print("--- Réponse de l'Agent ---")
    print(result["text"])
    
    if result["code_details"]:
        print("\n--- Exécution de code Python sandboxée ---")
        for c in result["code_details"]:
            print(c)
