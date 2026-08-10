from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from agents import run_assistant

# Initialisation de l'application FastAPI
app = FastAPI(
    title="Personal Assistant Microservice",
    description="Microservice FastAPI pour l'assistant personnel multi-agents (Finance, Actions, Journal)",
    version="1.0.0"
)

# --- MODÈLES DE REQUÊTE ET RÉPONSE (Pydantic) ---

class ProcessRequest(BaseModel):
    instruction: str = Field(
        ...,
        description="L'instruction ou la note vocale/texte de l'utilisateur.",
        example="Aujourd'hui j'ai eu une réunion IA. J'ai dépensé 15$ pour le déjeuner et je dois appeler mon père demain."
    )

class ProcessResponse(BaseModel):
    status: str = Field(default="success")
    instruction: str
    result: str

# --- ENDPOINTS ---

@app.get("/", tags=["Health Check"])
def health_check():
    """Endpoint de santé pour vérifier que le microservice fonctionne."""
    return {"status": "online", "service": "Personal Assistant Agent Microservice"}


@app.post("/api/v1/process", response_model=ProcessResponse, tags=["Assistant Agent"])
def process_instruction(payload: ProcessRequest):
    """
    Endpoint principal : Analyse l'instruction utilisateur,
    déclenche les sous-agents appropriés et enregistre les données dans Supabase.
    """
    if not payload.instruction.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="L'instruction ne peut pas être vide."
        )
    
    try:
        # Exécution de l'orchestrateur d'agents
        assistant_result = run_assistant(payload.instruction)
        
        return ProcessResponse(
            status="success",
            instruction=payload.instruction,
            result=assistant_result
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du traitement de l'agent : {str(e)}"
        )