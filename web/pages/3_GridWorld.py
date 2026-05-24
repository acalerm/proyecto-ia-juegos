import streamlit as st
import numpy as np
import random
import time
from PIL import Image, ImageDraw, ImageFont

from utils.supabase_client import supabase
from utils.session import get_user

st.set_page_config(page_title="GridWorld IA", layout="centered")

st.title("🤖 GridWorld IA")

# =========================================================
# 👤 USER
# =========================================================
user = get_user()

# =========================================================
# FONT
# =========================================================
try:
    FONT = ImageFont.truetype("arial.ttf", 24)
except:
    FONT = ImageFont.load_default()

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

if "trained" not in st.session_state:
    st.session_state.trained = False

# =========================================================
# 🧱 MAPAS
# =========================================================
def generate_map(difficulty):

    agent = (0, 0)
    goal = (7, 7)

    # =====================================================
    # FÁCIL
    # =====================================================
    if difficulty == "Fácil":

        walls = [
            (3,3),
            (3,4),
            (4,3)
        ]

    # =====================================================
    # MEDIA
    # =====================================================
    elif difficulty == "Media":

        # Dos caminos:
        # - uno corto y estrecho
        # - otro largo y seguro

        walls = [

            # bloque central
            (2,2),(2,3),(2,4),
            (3,4),
            (4,4),
            (5,4),

            # pasillo estrecho
            (4,1),
            (4,2),

            # pared lateral
            (6,2),(6,3)
        ]

    # =====================================================
    # DIFÍCIL
    # =====================================================
    else:

        # mapa diseñado para:
        # SARSA -> ruta segura
        # Q-Learning -> atajo peligroso

        walls = [

            # muro vertical izquierdo
            (1,1),(1,2),(1,3),(1,4),

            # muro horizontal superior
            (2,4),(3,4),(4,4),

            # muro central
            (4,1),(4,2),

            # cierre parcial
            (5,2),(6,2),

            # zona inferior
            (2,6),(3,6),(4,6),

            # laberinto
            (6,4),(6,5)
        ]

    return agent, goal, walls

# =========================================================
# 🧠 VISIÓN
# =========================================================
def get_vision(agent, walls, goal):

    ax, ay = agent
    v = []

    for dy in [-1,0,1]:
        for dx in [-1,0,1]:

            x = ax + dx
            y = ay + dy

            if x < 0 or x >= GRID or y < 0 or y >= GRID:
                v.append(-1)

            elif (x,y) == goal:
                v.append(2)

            elif (x,y) in walls:
                v.append(1)

            else:
                v.append(0)

    return tuple(v)

# =========================================================
# STEP
# =========================================================
def step(agent, action, goal, walls):

    x,y = agent

    if action == 0:
        y -= 1

    elif action == 1:
        x += 1

    elif action == 2:
        y += 1

    elif action == 3:
        x -= 1

    new = (x,y)

    # pared exterior
    if x < 0 or x >= GRID or y < 0 or y >= GRID:
        return agent, -15, False

    # paredes
    if new in walls:
        return agent, -20, False

    # meta
    if new == goal:
        return new, 100, True

    # recompensa por acercarse
    d1 = abs(agent[0]-goal[0]) + abs(agent[1]-goal[1])
    d2 = abs(new[0]-goal[0]) + abs(new[1]-goal[1])

    reward = -1

    if d2 < d1:
        reward += 3

    return new, reward, False

# =========================================================
# RL
# =========================================================
def state(v,gdir):
    return v + gdir

def choose(Q,s):

    if s not in Q:
        Q[s] = [0,0,0,0]

    epsilon = 0.1

    if random.random() < epsilon:
        return random.randint(0,3)

    return int(np.argmax(Q[s]))

def update(Q,s,a,r,ns,na,algo):

    alpha = 0.1
    gamma = 0.9

    if s not in Q:
        Q[s] = [0,0,0,0]

    if ns not in Q:
        Q[ns] = [0,0,0,0]

    # =====================================================
    # SARSA
    # =====================================================
    if algo == "SARSA":

        Q[s][a] += alpha * (
            r + gamma * Q[ns][na] - Q[s][a]
        )

    # =====================================================
    # Q-LEARNING
    # =====================================================
    else:

        Q[s][a] += alpha * (
            r + gamma * np.max(Q[ns]) - Q[s][a]
        )

# =========================================================
# TRAIN
# =========================================================
def train(algo, difficulty, episodes):

    Q = (
        st.session_state.Q_sarsa
        if algo == "SARSA"
        else st.session_state.Q_ql
    )

    for _ in range(episodes):

        a,g,w = generate_map(difficulty)

        v = get_vision(a,w,g)

        gdir = (
            np.sign(g[0]-a[0]),
            np.sign(g[1]-a[1])
        )

        s = state(v,gdir)

        act = choose(Q,s)

        done = False

        for _ in range(80):

            na,r,done = step(a,act,g,w)

            v2 = get_vision(na,w,g)

            gdir2 = (
                np.sign(g[0]-na[0]),
                np.sign(g[1]-na[1])
            )

            ns = state(v2,gdir2)

            nxt = choose(Q,ns)

            update(Q,s,act,r,ns,nxt,algo)

            a = na
            s = ns
            act = nxt

            if done:
                break

# =========================================================
# DRAW
# =========================================================
def draw(agent,goal,walls):

    img = Image.new(
        "RGB",
        (GRID*CELL, GRID*CELL),
        (25,25,25)
    )

    d = ImageDraw.Draw(img)

    # grid
    for x in range(GRID):
        for y in range(GRID):

            d.rectangle(
                [
                    x*CELL,
                    y*CELL,
                    x*CELL+CELL,
                    y*CELL+CELL
                ],
                outline=(80,80,80)
            )

    # walls
    for ob in walls:

        d.rectangle(
            [
                ob[0]*CELL,
                ob[1]*CELL,
                ob[0]*CELL+CELL,
                ob[1]*CELL+CELL
            ],
            fill=(200,50,50)
        )

    # goal
    d.ellipse(
        [
            goal[0]*CELL+20,
            goal[1]*CELL+20,
            goal[0]*CELL+CELL-20,
            goal[1]*CELL+CELL-20
        ],
        fill=(0,255,0)
    )

    # player
    d.ellipse(
        [
            agent[0]*CELL+20,
            agent[1]*CELL+20,
            agent[0]*CELL+CELL-20,
            agent[1]*CELL+CELL-20
        ],
        fill=(50,150,255)
    )

    return img

# =========================================================
# UI
# =========================================================
modo = st.selectbox("Modo", [
    "Entrenar",
    "Comparación visual",
    "Explicación"
])

# =========================================================
# ENTRENAR
# =========================================================
if modo == "Entrenar":

    difficulty = st.selectbox(
        "Dificultad",
        ["Fácil","Media","Difícil"]
    )

    episodes = st.slider(
        "Episodios",
        1000,
        20000,
        5000,
        step=1000
    )

    if st.button("Entrenar IA"):

        progress = st.progress(0)

        train("SARSA", difficulty, episodes)
        progress.progress(50)

        train("Q-Learning", difficulty, episodes)
        progress.progress(100)

        st.session_state.trained = True

        # =================================================
        # GUARDAR
        # =================================================
        if user:

            supabase.table("gridworld_stats").insert({
                "user_id": user.id,
                "display_name": user.user_metadata.get("display_name"),
                "algorithm": "SARSA",
                "difficulty": difficulty,
                "episodes": episodes,
                "avg_reward": 0
            }).execute()

            supabase.table("gridworld_stats").insert({
                "user_id": user.id,
                "display_name": user.user_metadata.get("display_name"),
                "algorithm": "Q-Learning",
                "difficulty": difficulty,
                "episodes": episodes,
                "avg_reward": 0
            }).execute()

        st.success("✅ Entrenamiento completado")

# =========================================================
# COMPARACIÓN
# =========================================================
if modo == "Comparación visual":

    difficulty = st.selectbox(
        "Dificultad",
        ["Fácil","Media","Difícil"]
    )

    speed = st.slider(
        "Velocidad simulación",
        0.05,
        1.0,
        0.3
    )

    if st.button("Simular batalla"):

        a1,g1,w1 = generate_map(difficulty)
        a2,g2,w2 = generate_map(difficulty)

        Q1 = st.session_state.Q_sarsa
        Q2 = st.session_state.Q_ql

        col1,col2 = st.columns(2)

        with col1:
            st.subheader("🟢 SARSA")

        with col2:
            st.subheader("🔴 Q-Learning")

        p1 = col1.empty()
        p2 = col2.empty()

        done1 = False
        done2 = False

        for _ in range(80):

            # =================================================
            # SARSA
            # =================================================
            if not done1:

                v = get_vision(a1,w1,g1)

                gdir = (
                    np.sign(g1[0]-a1[0]),
                    np.sign(g1[1]-a1[1])
                )

                s = state(v,gdir)

                act = choose(Q1,s)

                a1,_,done1 = step(a1,act,g1,w1)

            # =================================================
            # QL
            # =================================================
            if not done2:

                v = get_vision(a2,w2,g2)

                gdir = (
                    np.sign(g2[0]-a2[0]),
                    np.sign(g2[1]-a2[1])
                )

                s = state(v,gdir)

                act = choose(Q2,s)

                a2,_,done2 = step(a2,act,g2,w2)

            p1.image(draw(a1,g1,w1), width=350)
            p2.image(draw(a2,g2,w2), width=350)

            time.sleep(speed)

# =========================================================
# EXPLICACIÓN
# =========================================================
if modo == "Explicación":

    st.markdown("## 📄 Explicación")

    st.write("""
GridWorld permite comparar dos algoritmos de aprendizaje por refuerzo:

### 🟢 SARSA
- Más conservador
- Aprende usando la acción que realmente ejecuta
- Tiende a evitar rutas peligrosas
- Prioriza estabilidad y seguridad

### 🔴 Q-Learning
- Más agresivo
- Aprende la mejor acción posible teóricamente
- Busca rutas más rápidas y eficientes
- Puede asumir más riesgos

### 🎯 Objetivo
La IA debe encontrar el camino hasta la meta evitando paredes y optimizando sus decisiones.

### 👀 Visión local 3x3
La IA no conoce el mapa completo.
Solo puede observar las casillas cercanas a su posición actual.

Esto obliga al agente a aprender mediante experiencia y exploración.
""")
