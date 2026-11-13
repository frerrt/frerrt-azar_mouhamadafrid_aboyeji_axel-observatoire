import pandas as pd
import requests

# 1. Chargement du calendrier des matchs (Liga, compétition 11, saison 1)
url_match = (
    "https://raw.githubusercontent.com/hudl/open-data/master/data/matches/11/1.json"
)
matches_data = requests.get(url_match).json()
df_matches = pd.json_normalize(matches_data)

# Pour un premier test, on prend le premier match de la liste
match_id = matches_data[0]["match_id"]
print(f"Traitement du match ID : {match_id}")

# 2. Chargement des Lineups (Temps de jeu / postes) et Events (Passes / Duels)
url_lineup = f"https://raw.githubusercontent.com/hudl/open-data/master/data/lineups/{match_id}.json"
url_event = f"https://raw.githubusercontent.com/hudl/open-data/master/data/events/{match_id}.json"

lineups_data = requests.get(url_lineup).json()
events_data = requests.get(url_event).json()

# 3. Structuration des joueurs actifs et de leur poste
joueurs_list = []
for team in lineups_data:
  team_name = team["team_name"]
  for player in team["lineup"]:
    if player["positions"]:  # Joueurs ayant joué
      poste_principal = player["positions"][0].get("position", "Inconnu")
      joueurs_list.append({
          "match_id": match_id,
          "team": team_name,
          "player_id": player["player_id"],
          "player_name": player["player_name"],
          "position": poste_principal,
          "nb_sequences": len(player["positions"]),
      })

df_joueurs = pd.DataFrame(joueurs_list)

# 4. Structuration fine des performances techniques depuis les events
events_list = []
for event in events_data:
  player_info = event.get("player")
  if player_info:
    event_type = event.get("type", {}).get("name")
    
    # On isole les passes réussies (pas d'attribut 'outcome' ou 'outcome' absent/différent d'échec)
    is_successful_pass = 0
    if event_type == "Pass":
      pass_info = event.get("pass", {})
      # Si la passe n'a pas de sous-clé 'outcome', elle est réussie
      if "outcome" not in pass_info:
        is_successful_pass = 1

    events_list.append({
        "player_id": player_info["id"],
        "event_type": event_type,
        "successful_pass": is_successful_pass,
    })

df_events = pd.DataFrame(events_list)

# Agrégation des actions par joueur
df_actions = (
    df_events.groupby("player_id")["event_type"]
    .value_counts()
    .unstack(fill_value=0)
    .reset_index()
)

# Agrégation spécifique des passes réussies
df_passes_reussies = (
    df_events.groupby("player_id")["successful_pass"]
    .sum()
    .reset_index()
    .rename(columns={"successful_pass": "Passes_Reussies"})
)

# 5. Fusion finale (Match + Joueurs + Actions techniques + Passes réussies)
df_final = pd.merge(df_joueurs, df_actions, on="player_id", how="left")
df_final = pd.merge(df_final, df_passes_reussies, on="player_id", how="left").fillna(0)

# Affichage propre des colonnes clés
print("\n--- Extrait du Dataset Final (Postes & Performance Technique) ---")
cols_to_print = ["team", "player_name", "position", "nb_sequences", "Pass", "Passes_Reussies", "Duel"]
# On vérifie que les colonnes existent avant de les afficher
cols_available = [c for c in cols_to_print if c in df_final.columns]

print(df_final[cols_available].head(10))