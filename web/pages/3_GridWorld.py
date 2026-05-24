import streamlit as st
import numpy as np
import random
import time
from PIL import Image, ImageDraw, ImageFont

from utils.supabase_client import supabase
from utils.session import get_user

st.set_page_config(page_title="GridWorld IA", layout="centered")

st.title("🤖 GridWorld IA")

user = get_user()

# =========================================================
# CONSTANTES
# =========================================================
GRID = 8
CELL = 70

# =========================================================
# STATE
# =========================================================
if "Q_sarsa" not in st.session_state:
    st.session_state.Q_sarsa = {}

if "Q_ql" not in st.session_state:
    st.session_state.Q_ql = {}

if "results" not in st.session_state:
    st.session_state.results = {}

# =========================================================
# MAPAS (NUEVO SISTEMA GRID)
# =========================================================
def generate_map(difficulty):

    if difficulty == "Fácil":

        grid = [
            ["S", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", "█", "█", "█", " ", " "],
            [" ", " ", " ", " ", " ", "█", " ", " "],
            [" ", " ", " ", " ", " ", "█", " ", " "],
            [" ", "█", "█", "█", " ", " ", " ", " "],
            [" ", " ", " ", "█", " ", " ", " ", " "],
            [" ", " ", " ", "█", " ", "█", "█", "█"],
            [" ", " ", " ", " ", " ", " ", " ", "G"]
        ]

    elif difficulty == "Media":

        grid = [
            ["S", " ", " ", "█", " ", " ", " ", " "],
            [" ", "█", " ", "█", " ", "█", "█", " "],
            [" ", "█", " ", " ", " ", "█", " ", " "],
            [" ", "█", "█", "█", " ", "█", "T", " "],
            [" ", " ", " ", "█", " ", "█", "█", "█"],
            ["█", "█", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", "█", "█", "█", "█", " "],
            [" ", "█", " ", " ", " ", " ", " ", "G"]
        ]

    else:

        grid = [
            ["S", " ", "█", " ", " ", " ", "█", " "],
            [" ", " ", "█", " ", "█", " ", "█", " "],
            ["█", " ", "█", " ", "█", " ", " ", " "],
            ["█", " ", " ", " ", "█", "█", "█", "█"],
            ["█", "█", "█", "T", " ", "T", " ", " "],
            [" ", " ", "█", "█", " ", "█", "█", " "],
            [" ", " ", " ", " ", " ", "█", " ", " "],
            ["█", "█", "█", "█", "█", "█", " ", "G"]
        ]

    agent = None
    goal = None
    walls = []
    traps = []

    for y in range(GRID):
        for x in range(GRID):

            cell = grid[y][x]

            if cell == "S":
                agent = (x, y)

            elif cell == "G":
                goal = (x, y)

            elif cell == "█":
                walls.append((x, y))

            elif cell == "T":
                traps.append((x, y))

    return agent, goal, walls, traps

# =========================================================
# VISIÓN
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
# STEP
# =========================================================
def step(agent, action, goal, walls, traps):

    x, y = agent

    if action == 0:
        y -= 1
    elif action == 1:
        x += 1
    elif action == 2:
        y += 1
    elif action == 3:
        x -= 1

    new = (x, y)

    if x < 0 or x >= GRID or y < 0 or y >= GRID:
        return agent, -10, False

    if new in walls:
        return agent, -15, False

    if new in traps:
        return new, -20, False

    if new == goal:
        return new, 100, True

    return new, -1, False

# =========================================================
# RL
# =========================================================
def state(v, gdir):
    return v + gdir

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
# TRAIN
# =========================================================
def train(algo, difficulty, episodes):

    Q = st.session_state.Q_sarsa if algo == "SARSA" else st.session_state.Q_ql

    for _ in range(episodes):

        a, g, w, t = generate_map(difficulty)

        v = get_vision(a, w, t, g)

        gdir = (np.sign(g[0]-a[0]), np.sign(g[1]-a[1]))

        s = state(v, gdir)

        act = choose(Q, s)

        done = False

        for _ in range(120):

            na, r, done = step(a, act, g, w, t)

            v2 = get_vision(na, w, t, g)

            gdir2 = (np.sign(g[0]-na[0]), np.sign(g[1]-na[1]))

            ns = state(v2, gdir2)

            nxt = choose(Q, ns)

            update(Q, s, act, r, ns, nxt, algo)

            a = na
            s = ns
            act = nxt

            if done:
                break

# =========================================================
# DRAW
# =========================================================
def draw(a, g, w, t):

    img = Image.new("RGB", (GRID*CELL, GRID*CELL), (25,25,25))
    d = ImageDraw.Draw(img)

    for x in range(GRID):
        for y in range(GRID):
            d.rectangle([x*CELL, y*CELL, x*CELL+CELL, y*CELL+CELL], outline=(80,80,80))

    for ob in w:
        d.rectangle([ob[0]*CELL, ob[1]*CELL, ob[0]*CELL+CELL, ob[1]*CELL+CELL], fill=(200,50,50))

    for tr in t:
        d.rectangle([tr[0]*CELL+15, tr[1]*CELL+15, tr[0]*CELL+CELL-15, tr[1]*CELL+CELL-15], fill=(255,140,0))

    d.ellipse([g[0]*CELL+20, g[1]*CELL+20, g[0]*CELL+CELL-20, g[1]*CELL+CELL-20], fill=(0,255,0))
    d.ellipse([a[0]*CELL+20, a[1]*CELL+20, a[0]*CELL+CELL-20, a[1]*CELL+CELL-20], fill=(50,150,255))

    return img

# =========================================================
# UI
# =========================================================
modo = st.selectbox("Modo", ["Entrenar", "Comparación visual", "Explicación"])

if modo == "Entrenar":

    episodes = st.slider("Episodios", 1000, 20000, 5000, step=1000)

    if st.button("Entrenar IA"):

        for d in ["Fácil", "Media", "Difícil"]:
            train("SARSA", d, episodes)
            train("Q-Learning", d, episodes)

        st.success("Entrenamiento completado")

elif modo == "Comparación visual":

    difficulty = st.selectbox("Dificultad", ["Fácil", "Media", "Difícil"])

    if st.button("Simular batalla"):

        a1,g1,w1,t1 = generate_map(difficulty)
        a2,g2,w2,t2 = generate_map(difficulty)

        Q1 = st.session_state.Q_sarsa
        Q2 = st.session_state.Q_ql

        col1, col2 = st.columns(2)

        p1 = col1.empty()
        p2 = col2.empty()

        done1 = False
        done2 = False

        for _ in range(120):

            if not done1:
                v = get_vision(a1,w1,t1,g1)
                gdir = (np.sign(g1[0]-a1[0]), np.sign(g1[1]-a1[1]))
                s = state(v,gdir)
                act = choose(Q1,s)
                a1,_,done1 = step(a1,act,g1,w1,t1)

            if not done2:
                v = get_vision(a2,w2,t2,g2)
                gdir = (np.sign(g2[0]-a2[0]), np.sign(g2[1]-a2[1]))
                s = state(v,gdir)
                act = choose(Q2,s)
                a2,_,done2 = step(a2,act,g2,w2,t2)

            p1.image(draw(a1,g1,w1,t1))
            p2.image(draw(a2,g2,w2,t2))

            time.sleep(0.3)

else:

    st.markdown("""
    ## 📘 Explicación

    - SARSA: más conservador
    - Q-Learning: más agresivo
    - Los mapas están diseñados para forzar decisiones distintas
    """)
