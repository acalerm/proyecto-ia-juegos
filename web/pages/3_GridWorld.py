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
# BBDD (SOLO AÑADIDO)
# =========================================================
def save_game_gridworld(user, difficulty, episodes):
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
# VISIÓN
# =========================================================
def get_vision(agent, walls, traps, goal):

    ax, ay = agent
    vision = []

    for dy in [-1,0,1]:
        for dx in [-1,0,1]:

            x = ax + dx
            y = ay + dy

            if x < 0 or x >= GRID or y < 0 or y >= GRID:
                vision.append(-1)

            elif (x, y) == goal:
                vision.append(3)

            elif (x, y) in walls:
                vision.append(1)

            elif (x, y) in traps:
                vision.append(5)

            else:
                vision.append(0)

    return tuple(vision)

# =========================================================
# STEP
# =========================================================
def step(agent, action, goal, walls, traps, algo_mode):

    x, y = agent

    if action == 0:
        y -= 1
    elif action == 1:
        x += 1
    elif action == 2:
        y += 1
    elif action == 3:
        x -= 1

    if x < 0 or x >= GRID or y < 0 or y >= GRID:
        return agent, -10, False

    new = (x, y)

    if new in walls:
        return agent, -10, False

    if new in traps:
        if algo_mode == "SARSA":
            return new, -45, False
        return new, -3, False

    if new == goal:
        return new, 200, True

    old_dist = abs(agent[0] - goal[0]) + abs(agent[1] - goal[1])
    new_dist = abs(new[0] - goal[0]) + abs(new[1] - goal[1])

    reward = -1
    if new_dist > old_dist:
        reward -= 2
    elif new_dist < old_dist:
        reward += 2

    return new, reward, False

# =========================================================
# STATE
# =========================================================
def state(agent, vision, gdir):
    return tuple(agent) + tuple(vision) + tuple(gdir)

# =========================================================
# CHOOSE
# =========================================================
def choose(Q, s, epsilon=0.1):

    if s not in Q:
        Q[s] = [0,0,0,0]

    if random.random() < epsilon:
        return random.randint(0,3)

    return int(np.argmax(Q[s]))

# =========================================================
# UPDATE
# =========================================================
def update(Q, s, a, r, ns, na, algo):

    alpha = 0.1
    gamma = 0.9

    if s not in Q:
        Q[s] = [0,0,0,0]
    if ns not in Q:
        Q[ns] = [0,0,0,0]

    if algo == "SARSA":
        Q[s][a] += alpha * (r + gamma * Q[ns][na] - Q[s][a])
    else:
        Q[s][a] += alpha * (r + gamma * np.max(Q[ns]) - Q[s][a])

# =========================================================
# TRAIN
# =========================================================
def train(algo, difficulty, episodes, progress, current_step, total_steps):

    Q = st.session_state.Q_sarsa if algo == "SARSA" else st.session_state.Q_ql
    rewards = []

    for ep in range(episodes):

        start, goal, walls, traps = generate_map(difficulty)
        agent = start
        st.session_state.visited.clear()

        vision = get_vision(agent, walls, traps, goal)
        gdir = (np.sign(goal[0]-agent[0]), np.sign(goal[1]-agent[1]))

        s = state(agent, vision, gdir)
        act = choose(Q, s, 0.25)

        total_reward = 0

        for _ in range(100):

            new_agent, reward, done = step(agent, act, goal, walls, traps, algo)

            if new_agent in st.session_state.visited:
                reward -= 8

            st.session_state.visited.add(new_agent)

            vision2 = get_vision(new_agent, walls, traps, goal)
            gdir2 = (np.sign(goal[0]-new_agent[0]), np.sign(goal[1]-new_agent[1]))

            ns = state(new_agent, vision2, gdir2)
            na = choose(Q, ns, 0.25)

            update(Q, s, act, reward, ns, na, algo)

            agent = new_agent
            s = ns
            act = na

            total_reward += reward

            if done:
                break

        rewards.append(total_reward)

        progress.progress((current_step + ep + 1) / total_steps)

    return np.mean(rewards)

# =========================================================
# UI
# =========================================================
modo = st.selectbox("Modo", ["Entrenar", "Comparación visual", "Explicación"])

# =========================================================
# ENTRENAMIENTO + BBDD
# =========================================================
if modo == "Entrenar":

    episodes = st.slider("Episodios", 1000, 20000, 5000, step=1000)

    if st.button("Entrenar IA"):

        st.session_state.Q_sarsa = {}
        st.session_state.Q_ql = {}

        progress = st.progress(0)

        difficulties = ["Fácil", "Media", "Difícil"]

        total_steps = len(difficulties) * 2 * episodes
        current_step = 0

        for difficulty in difficulties:

            train("SARSA", difficulty, episodes, progress, current_step, total_steps)
            current_step += episodes

            train("Q-Learning", difficulty, episodes, progress, current_step, total_steps)
            current_step += episodes

        progress.progress(1.0)

        # ✅ SOLO BBDD
        save_game_gridworld(user, "Multi (SARSA + Q)", episodes)

        st.success("✅ Entrenamiento completo")
