import streamlit as st
import numpy as np
import random
import time
from PIL import Image, ImageDraw

from utils.session import get_user

st.set_page_config(page_title="GridWorld IA PRO", layout="centered")
st.title("🤖 GridWorld IA PRO (Mapas personalizados)")

user = get_user()

# =========================================================
# CONSTANTES
# =========================================================
GRID = 8
CELL = 70

# =========================================================
# MAPAS (SEGÚN TU EXCEL)
# =========================================================

def generate_map(difficulty):

    start = (0, 0)
    goal = (7, 7)

    # =====================================================
    # 🟡 1. MEDIO (primero en tu orden)
    # =====================================================
    if difficulty == "Media":

        walls = {
            (0,3),(1,3),(2,3),
            (2,1),(3,1),(4,1),
            (4,2),(5,2),(6,2),
            (6,4),(5,4)
        }

        traps = {
            (3,2),   # trampa que hace el camino corto arriesgado
            (5,3)
        }

    # =====================================================
    # 🟢 2. FÁCIL (camino único sin trampas)
    # =====================================================
    elif difficulty == "Fácil":

        walls = {
            (1,1),(1,2),(1,3),
            (2,3),(3,3),
            (4,4),(5,4),
            (5,5),(6,5)
        }

        traps = set()

    # =====================================================
    # 🔴 3. DIFÍCIL (dos rutas: derecha corta con trampa)
    # =====================================================
    else:

        walls = {
            (1,0),(2,0),
            (2,1),(2,2),
            (3,2),(4,2),
            (4,3),(4,4),
            (5,5),(6,5)
        }

        traps = {
            (6,1),  # camino corto peligroso (derecha)
            (6,2),
            (6,3)
        }

    return start, goal, walls, traps

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

    if action == 0: y -= 1
    elif action == 1: x += 1
    elif action == 2: y += 1
    elif action == 3: x -= 1

    new = (x, y)

    if x < 0 or x >= GRID or y < 0 or y >= GRID:
        return agent, -5, False

    if new in walls:
        return agent, -10, False

    if new in traps:
        return new, -30, False

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

    Q = {}

    rewards = []

    for _ in range(episodes):

        a, g, w, t = generate_map(difficulty)

        v = get_vision(a,w,t,g)
        gdir = (np.sign(g[0]-a[0]), np.sign(g[1]-a[1]))

        s = state(v, gdir)
        act = choose(Q, s)

        total = 0
        done = False

        for _ in range(80):

            na, r, done = step(a, act, g, w, t)

            v2 = get_vision(na,w,t,g)
            gdir2 = (np.sign(g[0]-na[0]), np.sign(g[1]-na[1]))

            ns = state(v2, gdir2)
            nxt = choose(Q, ns)

            update(Q, s, act, r, ns, nxt, algo)

            a = na
            s = ns
            act = nxt

            total += r

            if done:
                break

        rewards.append(total)

    return np.mean(rewards)

# =========================================================
# DRAW
# =========================================================
def draw(a, g, w, t):

    img = Image.new("RGB", (GRID*CELL, GRID*CELL), (25,25,25))
    d = ImageDraw.Draw(img)

    for x in range(GRID):
        for y in range(GRID):
            d.rectangle([x*CELL,y*CELL,x*CELL+CELL,y*CELL+CELL], outline=(80,80,80))

    for ob in w:
        d.rectangle([ob[0]*CELL,ob[1]*CELL,ob[0]*CELL+CELL,ob[1]*CELL+CELL], fill=(200,50,50))

    for tr in t:
        d.rectangle([tr[0]*CELL,tr[1]*CELL,tr[0]*CELL+CELL,tr[1]*CELL+CELL], fill=(255,140,0))

    d.ellipse([g[0]*CELL+15,g[1]*CELL+15,g[0]*CELL+CELL-15,g[1]*CELL+CELL-15], fill=(0,255,0))
    d.ellipse([a[0]*CELL+15,a[1]*CELL+15,a[0]*CELL+CELL-15,a[1]*CELL+CELL-15], fill=(50,150,255))

    return img

# =========================================================
# UI
# =========================================================
modo = st.selectbox("Modo", ["Entrenar", "Comparación visual", "Explicación"])

if modo == "Entrenar":

    episodes = st.slider("Episodios", 1000, 20000, 5000, step=1000)

    if st.button("Entrenar IA"):

        st.write("Entrenando SARSA vs Q-Learning...")

        for d in ["Fácil","Media","Difícil"]:
            s = train("SARSA", d, episodes)
            q = train("Q-Learning", d, episodes)

            st.write(f"{d} → SARSA: {s:.2f} | Q: {q:.2f}")

        st.success("Entrenamiento completado")

elif modo == "Comparación visual":

    difficulty = st.selectbox("Dificultad", ["Fácil","Media","Difícil"])

    if st.button("Simular"):

        a1,g1,w1,t1 = generate_map(difficulty)
        a2,g2,w2,t2 = generate_map(difficulty)

        col1, col2 = st.columns(2)
        p1 = col1.empty()
        p2 = col2.empty()

        for _ in range(80):

            v = get_vision(a1,w1,t1,g1)
            gdir = (np.sign(g1[0]-a1[0]), np.sign(g1[1]-a1[1]))
            a1,_,_ = step(a1,0,g1,w1,t1)

            v = get_vision(a2,w2,t2,g2)
            gdir = (np.sign(g2[0]-a2[0]), np.sign(g2[1]-a2[1]))
            a2,_,_ = step(a2,1,g2,w2,t2)

            p1.image(draw(a1,g1,w1,t1))
            p2.image(draw(a2,g2,w2,t2))

            time.sleep(0.3)

else:
    st.write("""
### 📘 Explicación

- **SARSA**: evita trampas → más seguro
- **Q-Learning**: busca el camino óptimo → más arriesgado

Los mapas están diseñados para forzar decisiones distintas en cada dificultad.
""")
