import os
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Importer les outils Supabase qu'on a créés
from tools import (
    record_expense,
    record_income,
    add_life_action,
    add_journal_entry
)

load_dotenv()

# Initialisation du client Google GenAI
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_ID = "gemini-3.5-flash"

# =====================================================================
# 1. SOUS-AGENTS SPÉCIALISÉS
# =====================================================================

# A. Sous-Agent Finance
FINANCE_AGENT_INSTRUCTIONS = """
Tu es un sous-agent spécialisé dans la gestion financière personnelle.
- Ton rôle est d'analyser les entrées et sorties d'argent.
- Utilise l'outil 'record_expense' pour enregistrer chaque dépense (montant, description, catégorie).
- Utilise l'outil 'record_income' pour enregistrer chaque revenu (montant, description, catégorie).
- Sois précis sur l'extraction des montants numériques.
"""

# B. Sous-Agent Actions & Tâches
LIFE_ACTION_AGENT_INSTRUCTIONS = """
Tu es un sous-agent spécialisé dans la gestion des tâches et actions de vie.
- Ton rôle est d'identifier les engagements, devoirs, rappels ou rendez-vous à exécuter.
- Utilise l'outil 'add_life_action' pour enregistrer chaque action.
- Extrais l'échéance ou la date si elle est précisée.
"""

# C. Sous-Agent Journal de Vie
JOURNAL_AGENT_INSTRUCTIONS = """
Tu es un sous-agent spécialisé dans la tenue du journal de vie.
- Ton rôle est de consigner un résumé des événements, faits marquants, réflexions, réunions passées ou moments de la journée
bref tout ce qui est en rapport avec ma vie personnelle dont j'aurais besoin de me rappeler plus tard sans exception.
- Si je n'ai pas donné la date de l'événement alors tu mets la date d'aujourd'hui.
- Utilise l'outil 'add_journal_entry' pour enregistrer le résumé de l'événement.
"""

# Outils regroupés par sous-agent
FINANCE_TOOLS = [record_expense, record_income]
LIFE_ACTION_TOOLS = [add_life_action]
JOURNAL_TOOLS = [add_journal_entry]

# =====================================================================
# 2. ORCHESTRATEUR PRINCIPAL
# =====================================================================

ORCHESTRATOR_INSTRUCTIONS = """
Tu es un Assistant Personnel Intelligent Multi-Agents.
Ta mission est d'analyser l'instruction globale de l'utilisateur et d'exécuter TOUTES les actions nécessaires via tes outils disponibles.

Une seule phrase utilisateur peut contenir plusieurs intentions. Analyse-la méthodiquement :
1. S'il y a des aspects financiers (achats, dépenses, paies, revenus) -> Enregistre la dépense/revenu.
2. S'il y a des tâches/actions futures à accomplir -> Enregistre l'action à réaliser.
3. S'il y a des événements passés, anecdotes, réunions terminées ou notes de journée bref 
tout ce qui est en rapport avec ma vie personnelle dont j'aurais besoin de me rappeler plus tard sans exception
-> Enregistre l'événement dans le journal de vie.   
"""

ALL_TOOLS = FINANCE_TOOLS + LIFE_ACTION_TOOLS + JOURNAL_TOOLS

def run_assistant(instruction: str) -> str:
    """Exécute l'assistant sur une instruction utilisateur."""
    
    now = datetime.now()
    french_days = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    day_name = french_days[now.weekday()]
    current_date_str = now.strftime("%d/%m/%Y")
    
    date_context = f"""
INFORMATIONS TEMPORELLES ACTUELLES :
- Aujourd'hui nous sommes le : {day_name} {current_date_str}

RÈGLE IMPÉRATIVE POUR TOUS LES OUTILS ET DATES :
Lorsque l'utilisateur mentionne une expression temporelle relative ou non explicitée (ex: "ce soir", "ce lundi", "mardi prochain", "dans une semaine", "demain", "hier", etc.), tu DOIS OBLIGATOIREMENT calculer la date exacte correspondante et compléter l'expression par la date au format JJ/MM/AAAA entre parenthèses.
Exemples :
- "ce soir" -> "ce soir ({current_date_str})"
- Si aujourd'hui est {day_name} {current_date_str}, calcule la date exacte pour "demain", "mardi prochain", "dans 3 jours", etc., et écris-la au format (JJ/MM/AAAA).
Pour le journal de vie, si aucune date n'est précisée, complète avec la date d'aujourd'hui ({current_date_str}).
"""

    full_system_instruction = ORCHESTRATOR_INSTRUCTIONS + "\n" + date_context

    # Exécution de la requête avec appels d'outils automatiques (Function Calling)
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=instruction,
        config=types.GenerateContentConfig(
            system_instruction=full_system_instruction,
            tools=ALL_TOOLS,
            temperature=0.2, # Température basse pour une exécution rigoureuse des outils
        )
    )
    
    return response.text or "Action(s) exécutée(s) avec succès."