import streamlit as st
import numpy as np
import random
import time
from PIL import Image, ImageDraw, ImageFont

from utils.supabase_client import supabase
from utils.session import get_user

st.set_page_config(page_title="GridWorld IA PRO", layout="centered")
st.title("🤖 GridWorld IA PRO (FINAL)")

user = get_user()

# =========================================================
# FONT
# =========================================================
try:
    FONT = ImageFont.truetype("arial.ttf", 24)
except:
    FONT = ImageFont.load_default()

GRID = 8
CELL = 70

# =========================================================
# SAVE (BBDD)
# =========================================================
def save_game(user, difficulty, episodes):
    if not user:
        return

    display_name = None

    if hasattr(user, "user_metadata") and user.user_metadata:
        display_name = user.user_metadata.get("display_name")

    if not display_name:
        display_name = getattr(user, "email", "guest")

    supabase.table("gridworld_stats").insert({
        "user_id": user.id,
        "display_name": display_name,
        "difficulty": difficulty,
        "episodes": episodes
    }).execute()

# =========================================================
# SESSION STATE
# =========================================================
if "Q_sarsa" not in st.session_state:
    st.session_state.Q_sarsa = {}

if "Q_ql" not in st.session_state:
    st.session_state.Q_ql = {}

if "results" not in st.session_state:
    st.session_state.results = {}

if "visited" not in st.session_state:
    st.session_state.visited = set()

# =========================================================
# MAPAS
# =========================================================
def parse_grid(grid):

    walls = []
    traps = []
    start = None
    goal = None

    for y in range(GRID):
        for x in range(GRID):

            cell = grid[y][x]

            if cell == "S":
                start = (x, y)

            elif cell == "G":
                goal = (x, y)

            elif cell == "█":
                walls.append((x, y))

            elif cell == "T":
                traps.append((x, y))

    return start, goal, walls, traps


grid_medium = [
    ["S"," "," ","█"," "," "," ","█"],
    [" "," "," ","T"," ","█"," ","█"],
    [" ","█","█","█"," ","█"," ","█"],
    [" "," "," ","█"," ","█"," "," "],
    [" ","█","█","█"," ","█"," "," "],
    [" "," ","█","█"," "," "," "," "],
    [" "," "," ","█","█","█","█"," "],
    ["█"," "," "," "," "," "," ","G"]
]

grid_easy = [
    ["S"," "," ","█"," "," ","█","█"],
    [" "," "," ","█"," "," "," ","█"],
    ["█"," ","█","█","█","█"," ","█"],
    [" "," "," "," "," ","█"," ","█"],
    [" ","█","█","█"," "," "," "," "],
    [" "," "," ","█"," ","█","█"," "],
    [" "," "," ","█"," ","█","█"," "],
    [" "," "," ","█"," ","█","█","G"]
]

grid_hard = [
    ["S"," ","T"," "," "," "," "," "],
    [" ","█","█","█","█","█","█"," "],
    [" ","█"," "," "," "," "," "," "],
    [" ","█"," ","█","█","█","█"," "],
    [" ","█"," ","█","█"," ","█"," "],
    [" ","█"," "," "," "," ","█"," "],
    [" ","█","█","█","█"," ","█"," "],
    [" "," "," "," "," "," ","█","G"]
]

# =========================================================
# MAP SELECTOR
# =========================================================
def generate_map(difficulty):

    if difficulty == "Fácil":
        return parse_grid(grid_easy)

    if difficulty == "Media":
        return parse_grid(grid_medium)

    return parse_grid(grid_hard)

# =========================================================
# (TODO LO DEMÁS SIN CAMBIOS)
# =========================================================
# ... (NO TOCADO para no romper el juego)

# =========================================================
# ENTRENAMIENTO
# =========================================================
if modo == "Entrenar":

    episodes = st.slider(
        "Episodios",
        1000,
        20000,
        5000,
        step=1000
    )

    if st.button("Entrenar IA"):

        st.session_state.Q_sarsa = {}
        st.session_state.Q_ql = {}

        progress = st.progress(0)

        results = {}

        difficulties = ["Fácil", "Media", "Difícil"]
        algos = ["SARSA", "Q-Learning"]

        total_steps = len(difficulties) * len(algos) * episodes
        current_step = 0

        for difficulty in difficulties:

            sarsa_result = train(
                "SARSA",
                difficulty,
                episodes,
                progress,
                current_step,
                total_steps
            )

            current_step += episodes

            q_result = train(
                "Q-Learning",
                difficulty,
                episodes,
                progress,
                current_step,
                total_steps
            )

            current_step += episodes

            results[difficulty] = {
                "SARSA": sarsa_result,
                "Q": q_result
            }

        progress.progress(1.0)
        st.session_state.results = results

        # ✅ GUARDADO EN BBDD (UNA SOLA VEZ)
        save_game(
            user=user,
            difficulty="Multi (SARSA + Q)",
            episodes=episodes
        )

        st.success("✅ Entrenamiento completo")
