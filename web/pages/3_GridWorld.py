import streamlit as st
import numpy as np
import random
import time
from PIL import Image, ImageDraw, ImageFont

from utils.supabase_client import supabase
from utils.session import get_user

st.set_page_config(page_title="GridWorld IA PRO FIX", layout="centered")
st.title("🤖 GridWorld IA PRO (FIXED)")

user = get_user()

# ---------------- FONT ----------------
try:
    FONT = ImageFont.truetype("arial.ttf", 24)
except:
    FONT = ImageFont.load_default()

GRID = 8
CELL = 70

# ---------------- STATE ----------------
if "Q_sarsa" not in st.session_state:
    st.session_state.Q_sarsa = {}

if "Q_ql" not in st.session_state:
    st.session_state.Q_ql = {}

if "results" not in st.session_state:
    st.session_state.results = {}

# =========================================================
# 🧱 MAPAS (NO MODIFICADOS)
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
    [" ","█"," "," "," ","█","█"," "],
    [" ","█"," ","█"," ","█","█"," "],
    [" ","█"," ","█"," ","█","█"," "],
    [" ","█"," ","█"," ","█","█"," "],
    [" ","█"," ","█"," ","█","█"," "],
    [" "," "," ","█"," "," "," ","G"]
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
# VISION 3x3
# =========================================================
def get_vision(agent, walls, traps, goal):
    ax, ay = agent
    v = []

    for dy in [-1,0,1]:
        for dx in [-1,0,1]:
            x = ax + dx
            y = ay + dy

            if x < 0 or x >= GRID or y < 0 or y >= GRID:
                v.append(-1)
            elif (x,y) == goal:
                v.append(3)
            elif (x,y) in walls:
                v.append(1)
            elif (x,y) in traps:
                v.append(2)
            else:
                v.append(0)

    return tuple(v)

# =========================================================
# STEP (CORREGIDO)
# =========================================================
def step(agent, action, goal, walls, traps):

    x, y = agent

    if action == 0: y -= 1
    elif action == 1: x += 1
    elif action == 2: y += 1
    elif action == 3: x -= 1

    # límites primero
    if x < 0 or x >= GRID or y < 0 or y >= GRID:
        return agent, -5, False

    new = (x, y)

    if new in walls:
        return agent, -10, False

    if new in traps:
        return new, -20, False

    if new == goal:
        return new, 100, True

    return new, -1, False

# =========================================================
# RL
# =========================================================
def state(v, gdir):
    return tuple(v) + tuple(gdir)

def choose(Q, s):
    if s not in Q:
        Q[s] = [0,0,0,0]

    if random.random() < 0.1:
        return random.randint(0,3)

    return int(np.argmax(Q[s]))

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
# TRAIN (ARREGLADO)
# =========================================================
def train(algo, difficulty, episodes):

    Q = st.session_state.Q_sarsa if algo == "SARSA" else st.session_state.Q_ql
    rewards = []

    for _ in range(episodes):

        start, goal, walls, traps = generate_map(difficulty)
        agent = start

        v = get_vision(agent, walls, traps, goal)
        gdir = (np.sign(goal[0]-agent[0]), np.sign(goal[1]-agent[1]))

        s = state(v, gdir)
        act = choose(Q, s)

        total = 0

        for _ in range(80):

            new_agent, r, done = step(agent, act, goal, walls, traps)

            v2 = get_vision(new_agent, walls, traps, goal)
            gdir2 = (np.sign(goal[0]-new_agent[0]), np.sign(goal[1]-new_agent[1]))

            ns = state(v2, gdir2)
            na = choose(Q, ns)

            update(Q, s, act, r, ns, na, algo)

            agent = new_agent
            s = ns
            act = na

            total += r

            if done:
                break

        rewards.append(total)

    return np.mean(rewards)

# =========================================================
# DRAW
# =========================================================
def draw(a, g, w, t):

    img = Image.new("RGB",(GRID*CELL,GRID*CELL),(25,25,25))
    d = ImageDraw.Draw(img)

    for x in range(GRID):
        for y in range(GRID):
            d.rectangle([x*CELL,y*CELL,x*CELL+CELL,y*CELL+CELL],outline=(80,80,80))

    for ob in w:
        d.rectangle([ob[0]*CELL,ob[1]*CELL,ob[0]*CELL+CELL,ob[1]*CELL+CELL],fill=(200,50,50))

    for tr in t:
        d.rectangle([tr[0]*CELL,tr[1]*CELL,tr[0]*CELL+CELL,tr[1]*CELL+CELL],fill=(255,140,0))

    d.ellipse([g[0]*CELL+20,g[1]*CELL+20,g[0]*CELL+CELL-20,g[1]*CELL+CELL-20],fill=(0,255,0))
    d.ellipse([a[0]*CELL+20,a[1]*CELL+20,a[0]*CELL+CELL-20,a[1]*CELL+CELL-20],fill=(50,150,255))

    return img

# =========================================================
# UI
# =========================================================
modo = st.selectbox("Modo", ["Entrenar", "Comparación visual", "Explicación"])

# =========================================================
# TRAIN
# =========================================================
if modo == "Entrenar":

    episodes = st.slider("Episodios", 1000, 20000, 5000, step=1000)

    if st.button("Entrenar IA"):

        results = {}

        for d in ["Fácil", "Media", "Difícil"]:

            s = train("SARSA", d, episodes)
            q = train("Q-Learning", d, episodes)

            results[d] = {"SARSA": s, "Q": q}

        st.session_state.results = results

        st.success("Entrenamiento completo")

# =========================================================
# COMPARACIÓN (ARREGLADA)
# =========================================================
if modo == "Comparación visual":

    difficulty = st.selectbox("Dificultad", ["Fácil","Media","Difícil"])

    if st.button("Simular"):

        start1, goal1, walls1, traps1 = generate_map(difficulty)
        start2, goal2, walls2, traps2 = generate_map(difficulty)

        a1 = start1
        a2 = start2

        col1,col2 = st.columns(2)
        p1 = col1.empty()
        p2 = col2.empty()

        Q1 = st.session_state.Q_sarsa
        Q2 = st.session_state.Q_ql

        for _ in range(80):

            v = get_vision(a1,walls1,traps1,goal1)
            gdir = (np.sign(goal1[0]-a1[0]), np.sign(goal1[1]-a1[1]))
            s = state(v,gdir)
            act = choose(Q1,s)
            a1,_,_ = step(a1,act,goal1,walls1,traps1)

            v = get_vision(a2,walls2,traps2,goal2)
            gdir = (np.sign(goal2[0]-a2[0]), np.sign(goal2[1]-a2[1]))
            s = state(v,gdir)
            act = choose(Q2,s)
            a2,_,_ = step(a2,act,goal2,walls2,traps2)

            p1.image(draw(a1,goal1,walls1,traps1))
            p2.image(draw(a2,goal2,walls2,traps2))

            time.sleep(0.4)

# =========================================================
# EXPLICACIÓN
# =========================================================
if modo == "Explicación":
    st.markdown("""
## SARSA vs Q-Learning

- SARSA: más conservador (aprende lo que realmente hace)
- Q-Learning: más agresivo (aprende el mejor futuro posible)

Las trampas fuerzan diferencias de estrategia.
""")
