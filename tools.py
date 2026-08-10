import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Client Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# --- 1. OUTILS FINANCIERS ---

def record_expense(amount: float, description: str, category: str = "Général") -> str:
    """Enregistre une nouvelle dépense dans la table 'expenses'. La description doit préciser la date exacte (ex: JJ/MM/AAAA) si mentionnée."""
    data = {"amount": amount, "description": description, "category": category}
    supabase.table("expenses").insert(data).execute()
    return f"Dépense enregistrée : {amount}$ pour '{description}'."


def record_income(amount: float, description: str, category: str = "Général") -> str:
    """Enregistre un nouveau revenu dans la table 'incomes'. La description doit préciser la date exacte (ex: JJ/MM/AAAA) si mentionnée."""
    data = {"amount": amount, "description": description, "category": category}
    supabase.table("incomes").insert(data).execute()
    return f"Revenu enregistré : {amount}$ provenant de '{description}'."


# --- 2. OUTILS ACTIONS DE VIE ---

def add_life_action(action: str, domain: str = "Général", due_date: str = None) -> str:
    """Enregistre une action ou tâche personnelle dans la table 'life_actions'. L'intitulé 'action' ou 'due_date' doit inclure la date exacte au format JJ/MM/AAAA si mentionnée."""
    data = {"action": action, "domain": domain, "status": "pending"}
    if due_date:
        data["due_date"] = due_date

    supabase.table("life_actions").insert(data).execute()
    return f"Action ajoutée : '{action}'" + (f" (Échéance: {due_date})" if due_date else "")


# --- 3. OUTIL JOURNAL DE VIE ---

def add_journal_entry(event_summary: str, domain: str = "Général", details: str = None) -> str:
    """Enregistre un fait marquant, une note ou un événement dans la table 'journal_entries'. L'événement 'event_summary' doit préciser la date exacte au format JJ/MM/AAAA."""
    data = {"event_summary": event_summary, "domain": domain}
    if details:
        data["details"] = details

    supabase.table("journal_entries").insert(data).execute()
    return f"Événement consigné au journal : '{event_summary}'."