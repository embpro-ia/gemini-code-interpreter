from typing import List, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from agents import run_analyst_agent

# Initialisation de l'application FastAPI
app = FastAPI(
    title="Gemini Code Interpreter Agent",
    description="Agent IA propulsé par Google Gemini (3.5 Flash Lite) avec exécution de code Python sandboxée.",
    version="1.0.0"
)

# --- MODÈLES DE REQUÊTE ET RÉPONSE (Pydantic) ---

class QueryRequest(BaseModel):
    prompt: str = Field(
        ...,
        description="La question ou le calcul Python à effectuer.",
        example="Calcule la factorielle de 25 et donne le nombre de zéros à la fin."
    )
    model: Optional[str] = Field(
        default="gemini-3.5-flash-lite",
        description="Le modèle Gemini à utiliser."
    )


class QueryResponse(BaseModel):
    status: str = Field(default="success")
    prompt: str
    response: str
    code_details: List[dict] = Field(default_factory=list)


class LegacyProcessRequest(BaseModel):
    instruction: str = Field(
        ...,
        description="Instruction ou requête utilisateur.",
        example="Génère les 10 premiers termes de la suite de Fibonacci."
    )


# --- ENDPOINTS ---

@app.get("/health", tags=["Health Check"])
@app.get("/api/health", tags=["Health Check"])
def health_check():
    """Vérification de l'état du service."""
    return {
        "status": "online",
        "service": "Gemini Code Interpreter Agent",
        "default_model": "gemini-3.5-flash-lite",
        "tools_enabled": ["code_execution"]
    }


@app.get("/", response_class=HTMLResponse, tags=["Web UI"])
@app.get("/api", response_class=HTMLResponse, include_in_schema=False)
@app.get("/api/index.py", response_class=HTMLResponse, include_in_schema=False)
def home_ui():
    """Interface web interactive pour tester directement l'agent dans le navigateur ou Hugging Face Spaces."""
    return """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Gemini Code Interpreter Agent</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
        <!-- Bibliothèques pour le rendu Markdown et Mathématiques -->
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
        <script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
        <style>
            body { max-width: 800px; margin: 0 auto; padding: 2rem 1rem; }
            .badge { display: inline-block; background: #0070f3; color: white; border-radius: 4px; padding: 0.2rem 0.5rem; font-size: 0.8rem; }
            pre { background: #1b1e2e; color: #a9b7c6; padding: 1rem; border-radius: 8px; overflow-x: auto; white-space: pre-wrap; }
            #loading { display: none; }
        </style>
    </head>
    <body>
        <header>
            <h1>🤖 Gemini Code Interpreter Agent (Version 2.0)</h1>
            <p>Propulsé par Google Gemini (<code>gemini-3.5-flash-lite</code>) & Code Execution sandboxée.</p>
            <p><a href="/docs" target="_blank">📖 Documentation Swagger API (/docs)</a></p>
        </header>
        <main>
            <label for="prompt"><b>Votre question ou calcul :</b></label>
            <textarea id="prompt" rows="3" placeholder="Ex: Calcule la factorielle de 20 et vérifie si le résultat est divisible par 17.">Génère les 10 premiers nombres premiers et calcule leur somme.</textarea>
            <button id="sendBtn" onclick="runAgent()">🚀 Exécuter l'Agent</button>
            <div id="loading"><article aria-busy="true">L'agent réfléchit et exécute le code Python...</article></div>
            
            <div id="resultSection" style="display: none; margin-top: 2rem;">
                <h3>Réponse de l'Agent :</h3>
                <article id="agentText"></article>
                <div id="codeSection" style="display: none;">
                    <h4>Détails d'exécution Python :</h4>
                    <pre id="codeOutput"></pre>
                </div>
            </div>
        </main>
        <script>
            async function runAgent() {
                const prompt = document.getElementById("prompt").value;
                if (!prompt.trim()) return;
                
                const sendBtn = document.getElementById("sendBtn");
                const loading = document.getElementById("loading");
                const resultSection = document.getElementById("resultSection");
                const agentText = document.getElementById("agentText");
                const codeSection = document.getElementById("codeSection");
                const codeOutput = document.getElementById("codeOutput");

                sendBtn.disabled = true;
                loading.style.display = "block";
                resultSection.style.display = "none";
                codeSection.style.display = "none";

                try {
                    const res = await fetch("/api/v1/query", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ prompt: prompt })
                    });
                    const data = await res.json();
                    
                    if (res.ok) {
                        agentText.innerHTML = marked.parse(data.response);
                        renderMathInElement(agentText, {
                            delimiters: [
                                {left: "$$", right: "$$", display: true},
                                {left: "\\[", right: "\\]", display: true},
                                {left: "$", right: "$", display: false},
                                {left: "\\(", right: "\\)", display: false}
                            ]
                        });
                        
                        if (data.code_details && data.code_details.length > 0) {
                            codeOutput.innerText = JSON.stringify(data.code_details, null, 2);
                            codeSection.style.display = "block";
                        }
                        resultSection.style.display = "block";
                    } else {
                        alert("Erreur: " + (data.detail || "Une erreur est survenue"));
                    }
                } catch (e) {
                    alert("Erreur réseau: " + e.message);
                } finally {
                    sendBtn.disabled = false;
                    loading.style.display = "none";
                }
            }
        </script>
    </body>
    </html>
    """


@app.post("/api/v1/query", response_model=QueryResponse, tags=["Analyst Agent"])
def process_query(payload: QueryRequest):
    """Exécute l'agent avec exécution de code Python sandboxée."""
    cleaned_prompt = payload.prompt.strip()
    if not cleaned_prompt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le champ 'prompt' ne peut pas être vide."
        )

    try:
        agent_output = run_analyst_agent(cleaned_prompt, model_name=payload.model)
        
        return QueryResponse(
            status="success",
            prompt=cleaned_prompt,
            response=agent_output.get("text", ""),
            code_details=agent_output.get("code_details", [])
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'exécution de l'agent : {str(e)}"
        )


@app.post("/api/v1/process", response_model=QueryResponse, tags=["Analyst Agent (Legacy)"])
def legacy_process_instruction(payload: LegacyProcessRequest):
    """Endpoint de compatibilité."""
    request_adapted = QueryRequest(prompt=payload.instruction)
    return process_query(request_adapted)
