from agents import run_assistant

print("🤖 Test de l'assistant multi-intentions...\n")

# Instruction contenant 3 intentions simultanées (Finance + Tâche + Journal)
test_prompt = (   
    """Merci pour le travail effectué et bonne nuit a demain matin"""    
)

print(f"📥 Instruction envoyée :\n\"{test_prompt}\"\n")
print("⏳ Traitement par l'assistant et enregistrement dans Supabase...\n")

resultat = run_assistant(test_prompt)

print("--------------------------------------------------")
print("📤 Réponse de l'Assistant :")
print("--------------------------------------------------")
print(resultat)