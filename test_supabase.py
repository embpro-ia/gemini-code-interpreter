import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print("🔌 Test de connexion globales aux 4 tables Supabase...")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Test de lecture sur les 4 tables
    tables = ["expenses", "incomes", "life_actions", "journal_entries"]
    for table in tables:
        res = supabase.table(table).select("*").limit(1).execute()
        print(f"✅ Table '{table}' accessible.")

    print("\n🎉 Tout est 100% fonctionnel sur Supabase !")

except Exception as e:
    print(f"❌ Échec de la connexion : {e}")