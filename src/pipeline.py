import requests

# URLs des différents fichiers StatsBomb / Hudl
url_lineup = "https://raw.githubusercontent.com/hudl/open-data/master/data/lineups/15946.json"
url_match = "https://raw.githubusercontent.com/hudl/open-data/master/data/matches/11/1.json"
url_event = "https://raw.githubusercontent.com/hudl/open-data/master/data/events/15946.json"

# Téléchargement des données
data_lineup = requests.get(url_lineup).json()
data_match = requests.get(url_match).json()
data_event = requests.get(url_event).json()

# 1. CHARGE TEMPORELLE (LINEUPS)
joueurs_utiles = []
for team in data_lineup:
    team_name = team['team_name']
    for player in team['lineup']:
        if player['positions']:  # Joueurs ayant foulé la pelouse
            joueurs_utiles.append({
                "team": team_name,
                "player_id": player['player_id'],
                "player_name": player['player_name'],
                "positions": player['positions']
            })

# 2. PERFORMANCE TECHNIQUE (EVENTS : Passes, Duels, etc.)
# On initialise un dictionnaire pour compter les actions par joueur
performances_joueurs = {}

for event in data_event:
    # On récupère l'ID du joueur s'il est présent dans l'événement
    player_info = event.get('player')
    if player_info:
        p_id = player_info['id']
        p_name = player_info['name']
        
        if p_id not in performances_joueurs:
            performances_joueurs[p_id] = {
                "name": p_name,
                "passes": 0,
                "duels": 0,
                "pressures": 0
            }
        
        # Comptage des types d'actions techniques pertinents pour l'intensité
        event_type = event.get('type', {}).get('name')
        if event_type == 'Pass':
            performances_joueurs[p_id]['passes'] += 1
        elif event_type == 'Duel':
            performances_joueurs[p_id]['duels'] += 1
        elif event_type == 'Pressure':
            performances_joueurs[p_id]['pressures'] += 1

# Affichage croisé pour l'analyse
print("=== ANALYSE COMBINÉE : CHARGE & PERFORMANCE TECHNIQUE ===")
for j in joueurs_utiles:
    p_id = j['player_id']
    perf = performances_joueurs.get(p_id, {"passes": 0, "duels": 0, "pressures": 0})
    
    print(f"[{j['team']}] {j['player_name']} :")
    print(f"  -> Séquences de jeu : {len(j['positions'])}")
    print(f"  -> Intensité technique -> Passes : {perf['passes']} | Duels : {perf['duels']} | Pressions : {perf['pressures']}\n")