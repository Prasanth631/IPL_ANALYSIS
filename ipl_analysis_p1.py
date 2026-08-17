import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

try:
    import mysql.connector
except Exception:
    mysql = None


# -----------------------------
# STEP 0: Basic paths and config
# -----------------------------
BASE = Path(__file__).resolve().parent
MATCHES_PATH = BASE / "matches.csv"
DELIVERIES_PATH = BASE / "deliveries.csv"
PLAYERS_PATH = BASE / "players.csv"

DB_HOST = os.getenv("IPL_DB_HOST", "localhost")
DB_USER = os.getenv("IPL_DB_USER", "root")
DB_PASSWORD = os.getenv("IPL_DB_PASSWORD", "root")
DB_NAME = os.getenv("IPL_DB_NAME", "ipl_analysis_p1")


matches = pd.read_csv(MATCHES_PATH)
deliveries = pd.read_csv(DELIVERIES_PATH)
players = pd.read_csv(PLAYERS_PATH)


matches = matches.drop_duplicates(subset=["match_id"]).copy()
matches["match_id"] = pd.to_numeric(matches["match_id"], errors="coerce")
matches["season"] = pd.to_numeric(matches["season"], errors="coerce").fillna(0).astype(int)
matches["match_date"] = pd.to_datetime(matches["match_date"], errors="coerce")

for col in ["team1", "team2", "venue", "winner"]:
    matches[col] = matches[col].astype(str).str.strip().replace("nan", pd.NA)

# If winner is empty, treat it as No Result.
matches["winner"] = np.where(matches["winner"].isna(), "No Result", matches["winner"])
matches = matches.dropna(subset=["match_id", "team1", "team2"])
matches["match_id"] = matches["match_id"].astype(int)


deliveries = deliveries.drop_duplicates().copy()

for col in ["match_id", "inning", "over", "ball", "batsman_runs", "bowler_runs", "is_wicket"]:
    deliveries[col] = pd.to_numeric(deliveries[col], errors="coerce")

deliveries[["batsman_runs", "bowler_runs", "is_wicket"]] = deliveries[
    ["batsman_runs", "bowler_runs", "is_wicket"]
].fillna(0)

deliveries = deliveries.dropna(subset=["match_id", "inning", "over", "ball"])
deliveries = deliveries[deliveries["inning"].between(1, 2)]
deliveries = deliveries[deliveries["over"].between(1, 20)]
deliveries = deliveries[deliveries["ball"].between(1, 6)]

deliveries["match_id"] = deliveries["match_id"].astype(int)
deliveries["inning"] = deliveries["inning"].astype(int)
deliveries["over"] = deliveries["over"].astype(int)
deliveries["ball"] = deliveries["ball"].astype(int)
deliveries["is_wicket"] = deliveries["is_wicket"].astype(int)

deliveries["total_runs"] = deliveries["batsman_runs"] + deliveries["bowler_runs"]

# Keep only deliveries where match exists in matches table.
deliveries = deliveries[deliveries["match_id"].isin(set(matches["match_id"]))].copy()


players = players.drop_duplicates(subset=["player_id"]).copy()
players["player_id"] = pd.to_numeric(players["player_id"], errors="coerce")

for col in ["player_name", "team", "role"]:
    players[col] = players[col].astype(str).str.strip().replace("nan", pd.NA)

players["role"] = players["role"].fillna("Unknown")
players = players.dropna(subset=["player_id", "player_name", "team"])
players["player_id"] = players["player_id"].astype(int)


if mysql is None:
    raise ImportError("Please install mysql-connector-python first.")

temp_conn = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD)
temp_cur = temp_conn.cursor()
temp_cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
temp_cur.close()
temp_conn.close()

conn = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
cur = conn.cursor()

cur.execute(
    """
    CREATE TABLE IF NOT EXISTS matches (
        match_id INT PRIMARY KEY,
        season INT,
        team1 VARCHAR(50),
        team2 VARCHAR(50),
        venue VARCHAR(100),
        winner VARCHAR(50),
        match_date DATE
    )
    """
)

cur.execute(
    """
    CREATE TABLE IF NOT EXISTS deliveries (
        delivery_id INT AUTO_INCREMENT PRIMARY KEY,
        match_id INT,
        inning INT,
        over_no INT,
        ball_no INT,
        batsman_runs FLOAT,
        bowler_runs FLOAT,
        is_wicket INT,
        total_runs FLOAT,
        FOREIGN KEY (match_id) REFERENCES matches(match_id)
    )
    """
)

cur.execute(
    """
    CREATE TABLE IF NOT EXISTS players (
        player_id INT PRIMARY KEY,
        player_name VARCHAR(100),
        team VARCHAR(50),
        role VARCHAR(50)
    )
    """
)

# Clean table data before inserting new rows.
cur.execute("SET FOREIGN_KEY_CHECKS=0")
cur.execute("TRUNCATE TABLE deliveries")
cur.execute("TRUNCATE TABLE matches")
cur.execute("TRUNCATE TABLE players")
cur.execute("SET FOREIGN_KEY_CHECKS=1")


match_rows = [
    (
        int(r.match_id),
        int(r.season),
        str(r.team1),
        str(r.team2),
        str(r.venue) if pd.notna(r.venue) else None,
        str(r.winner),
        r.match_date.date() if pd.notna(r.match_date) else None,
    )
    for r in matches.itertuples(index=False)
]

delivery_rows = [
    (
        int(r.match_id),
        int(r.inning),
        int(r.over),
        int(r.ball),
        float(r.batsman_runs),
        float(r.bowler_runs),
        int(r.is_wicket),
        float(r.total_runs),
    )
    for r in deliveries.itertuples(index=False)
]

player_rows = [
    (int(r.player_id), str(r.player_name), str(r.team), str(r.role)) for r in players.itertuples(index=False)
]

cur.executemany(
    "INSERT INTO matches (match_id, season, team1, team2, venue, winner, match_date) VALUES (%s,%s,%s,%s,%s,%s,%s)",
    match_rows,
)
cur.executemany(
    "INSERT INTO deliveries (match_id, inning, over_no, ball_no, batsman_runs, bowler_runs, is_wicket, total_runs) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
    delivery_rows,
)
cur.executemany(
    "INSERT INTO players (player_id, player_name, team, role) VALUES (%s,%s,%s,%s)",
    player_rows,
)
conn.commit()


cur.execute(
    "SELECT winner AS team, COUNT(*) AS wins FROM matches WHERE winner <> 'No Result' GROUP BY winner ORDER BY wins DESC"
)
wins_df = pd.DataFrame(cur.fetchall(), columns=["team", "wins"])

cur.execute("SELECT match_id, SUM(total_runs) AS total_runs FROM deliveries GROUP BY match_id")
runs_per_match_df = pd.DataFrame(cur.fetchall(), columns=["match_id", "total_runs"])

cur.execute("SELECT match_id, SUM(is_wicket) AS wickets FROM deliveries GROUP BY match_id")
wickets_per_match_df = pd.DataFrame(cur.fetchall(), columns=["match_id", "wickets"])

cur.execute("SELECT COUNT(*) FROM matches WHERE winner = 'No Result'")
no_result_matches = int(cur.fetchone()[0])

average_runs_per_match = float(runs_per_match_df["total_runs"].mean())
high_scoring_df = runs_per_match_df[runs_per_match_df["total_runs"] >= 180].copy()
if high_scoring_df.empty:
    high_scoring_df = runs_per_match_df.sort_values("total_runs", ascending=False).head(10)

cur.close()
conn.close()


fig, axes = plt.subplots(3, 2, figsize=(15, 12))
fig.suptitle("IPL Analysis Dashboard", fontsize=15, fontweight="bold")

axes[0, 0].bar(wins_df["team"], wins_df["wins"], color="teal")
axes[0, 0].set_title("Team Wins Across Seasons")
axes[0, 0].tick_params(axis="x", rotation=45)

axes[0, 1].hist(runs_per_match_df["total_runs"], bins=12, color="orange", edgecolor="black")
axes[0, 1].set_title("Runs Distribution Per Match")

axes[1, 0].plot(wickets_per_match_df["match_id"], wickets_per_match_df["wickets"], marker="o")
axes[1, 0].set_title("Wickets Per Match")

axes[1, 1].bar(high_scoring_df["match_id"].astype(str), high_scoring_df["total_runs"], color="crimson")
axes[1, 1].set_title("High-Scoring Matches")
axes[1, 1].tick_params(axis="x", rotation=45)

axes[2, 0].bar(["Average Runs"], [average_runs_per_match], color="steelblue")
axes[2, 0].set_title("Average Runs Per Match")

axes[2, 1].bar(["No Result"], [no_result_matches], color="gray")
axes[2, 1].set_title("Matches With No Result")

plt.tight_layout(rect=[0, 0, 1, 0.96])
dashboard_path = BASE / "ipl_dashboard.png"
plt.savefig(dashboard_path, dpi=150)
plt.show()


print("\nFinal Summary")
top_team = wins_df.iloc[0]["team"] if not wins_df.empty else "N/A"
print("Top winning team:", top_team)
print("Average runs per match:", round(average_runs_per_match, 2))
print("No Result matches:", no_result_matches)
print("Dashboard saved at:", dashboard_path)
