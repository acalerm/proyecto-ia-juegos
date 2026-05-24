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
    ["S"," ","T","T"," "," "," "," "],
    [" ","█","█","█","█","█","█"," "],
    [" ","█"," "," "," ","█","█"," "],
    [" ","█"," ","█"," ","█","█","T"],
    [" ","█"," ","█"," ","█","█","T"],
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

    # fuera del mapa
    if x < 0 or x >= GRID or y < 0 or y >= GRID:
        return agent, -10, False

    new = (x, y)

    # pared
    if new in walls:
        return agent, -15, False

    # trampa
    if new in traps:
        return new, -100, False

    # meta
    if new == goal:
        return new, 200, True

    # =====================================================
    # REWARD SHAPING
    # =====================================================
    old_dist = abs(agent[0] - goal[0]) + abs(agent[1] - goal[1])
    new_dist = abs(new[0] - goal[0]) + abs(new[1] - goal[1])

    reward = -1

    # alejarse de la meta
    if new_dist > old_dist:
        reward -= 4

    # acercarse
    if new_dist < old_dist:
        reward += 2

    return new, reward, False

# =========================================================
# ESTADO
# =========================================================
def state(agent, vision, gdir):

    return (
        tuple(agent)
        + tuple(vision)
        + tuple(gdir)
    )

# =========================================================
# CHOOSE ACTION
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

        Q[s][a] += alpha * (
            r + gamma * Q[ns][na] - Q[s][a]
        )

    else:

        Q[s][a] += alpha * (
            r + gamma * np.max(Q[ns]) - Q[s][a]
        )

# =========================================================
# TRAIN
# =========================================================
def train(
    algo,
    difficulty,
    episodes,
    progress,
    current_step,
    total_steps
):

    Q = (
        st.session_state.Q_sarsa
        if algo == "SARSA"
        else st.session_state.Q_ql
    )

    rewards = []

    for ep in range(episodes):

        start, goal, walls, traps = generate_map(difficulty)

        agent = start

        st.session_state.visited.clear()

        vision = get_vision(agent, walls, traps, goal)

        gdir = (
            np.sign(goal[0] - agent[0]),
            np.sign(goal[1] - agent[1])
        )

        s = state(agent, vision, gdir)

        epsilon = max(
            0.01,
            0.25 * (1 - ep / episodes)
        )

        act = choose(Q, s, epsilon)

        total_reward = 0

        for _ in range(100):

            new_agent, reward, done = step(
                agent,
                act,
                goal,
                walls,
                traps
            )

            # =============================================
            # PENALIZAR LOOPS
            # =============================================
            if new_agent in st.session_state.visited:
                reward -= 25

            st.session_state.visited.add(new_agent)

            # =============================================
            # NUEVO ESTADO
            # =============================================
            vision2 = get_vision(
                new_agent,
                walls,
                traps,
                goal
            )

            gdir2 = (
                np.sign(goal[0] - new_agent[0]),
                np.sign(goal[1] - new_agent[1])
            )

            ns = state(new_agent, vision2, gdir2)

            na = choose(Q, ns, epsilon)

            # =============================================
            # UPDATE
            # =============================================
            update(
                Q,
                s,
                act,
                reward,
                ns,
                na,
                algo
            )

            agent = new_agent
            s = ns
            act = na

            total_reward += reward

            if done:
                break

        rewards.append(total_reward)

        # =============================================
        # BARRA GLOBAL
        # =============================================
        global_progress = (
            current_step + ep + 1
        ) / total_steps

        progress.progress(global_progress)

    return np.mean(rewards)

# =========================================================
# DRAW
# =========================================================
def draw(agent, goal, walls, traps):

    img = Image.new(
        "RGB",
        (GRID * CELL, GRID * CELL),
        (25,25,25)
    )

    d = ImageDraw.Draw(img)

    # grid
    for x in range(GRID):
        for y in range(GRID):

            d.rectangle(
                [
                    x * CELL,
                    y * CELL,
                    x * CELL + CELL,
                    y * CELL + CELL
                ],
                outline=(80,80,80)
            )

    # paredes
    for ob in walls:

        d.rectangle(
            [
                ob[0] * CELL,
                ob[1] * CELL,
                ob[0] * CELL + CELL,
                ob[1] * CELL + CELL
            ],
            fill=(200,50,50)
        )

    # trampas
    for tr in traps:

        d.rectangle(
            [
                tr[0] * CELL,
                tr[1] * CELL,
                tr[0] * CELL + CELL,
                tr[1] * CELL + CELL
            ],
            fill=(255,140,0)
        )

    # meta
    d.ellipse(
        [
            goal[0] * CELL + 20,
            goal[1] * CELL + 20,
            goal[0] * CELL + CELL - 20,
            goal[1] * CELL + CELL - 20
        ],
        fill=(0,255,0)
    )

    # agente
    d.ellipse(
        [
            agent[0] * CELL + 20,
            agent[1] * CELL + 20,
            agent[0] * CELL + CELL - 20,
            agent[1] * CELL + CELL - 20
        ],
        fill=(50,150,255)
    )

    return img

# =========================================================
# UI
# =========================================================
modo = st.selectbox(
    "Modo",
    [
        "Entrenar",
        "Comparación visual",
        "Explicación"
    ]
)

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

        # RESET Q TABLES
        st.session_state.Q_sarsa = {}
        st.session_state.Q_ql = {}

        progress = st.progress(0)

        results = {}

        difficulties = [
            "Fácil",
            "Media",
            "Difícil"
        ]

        algos = [
            "SARSA",
            "Q-Learning"
        ]

        total_steps = (
            len(difficulties)
            * len(algos)
            * episodes
        )

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

        st.success("✅ Entrenamiento completo")

# =========================================================
# COMPARACIÓN VISUAL
# =========================================================
if modo == "Comparación visual":

    difficulty = st.selectbox(
        "Dificultad",
        ["Fácil", "Media", "Difícil"]
    )

    if st.button("Simular"):

        start1, goal1, walls1, traps1 = generate_map(difficulty)
        start2, goal2, walls2, traps2 = generate_map(difficulty)

        a1 = start1
        a2 = start2

        col1, col2 = st.columns(2)

        col1.markdown("## 🟦 SARSA")
        col2.markdown("## 🟧 Q-Learning")

        p1 = col1.empty()
        p2 = col2.empty()

        Q1 = st.session_state.Q_sarsa
        Q2 = st.session_state.Q_ql

        done1 = False
        done2 = False

        for _ in range(100):

            # =========================================
            # SARSA
            # =========================================
            if not done1:

                v1 = get_vision(
                    a1,
                    walls1,
                    traps1,
                    goal1
                )

                gdir1 = (
                    np.sign(goal1[0] - a1[0]),
                    np.sign(goal1[1] - a1[1])
                )

                s1 = state(a1, v1, gdir1)

                act1 = choose(Q1, s1, 0)

                a1, _, done1 = step(
                    a1,
                    act1,
                    goal1,
                    walls1,
                    traps1
                )

            # =========================================
            # Q-LEARNING
            # =========================================
            if not done2:

                v2 = get_vision(
                    a2,
                    walls2,
                    traps2,
                    goal2
                )

                gdir2 = (
                    np.sign(goal2[0] - a2[0]),
                    np.sign(goal2[1] - a2[1])
                )

                s2 = state(a2, v2, gdir2)

                act2 = choose(Q2, s2, 0)

                a2, _, done2 = step(
                    a2,
                    act2,
                    goal2,
                    walls2,
                    traps2
                )

            p1.image(draw(a1, goal1, walls1, traps1))
            p2.image(draw(a2, goal2, walls2, traps2))

            time.sleep(0.25)

            if done1 and done2:
                break

# =========================================================
# EXPLICACIÓN
# =========================================================
if modo == "Explicación":

    st.markdown("""
## 🤖 SARSA vs Q-Learning

### 🟦 SARSA
- Aprende según las acciones reales que toma
- Más conservador
- Evita más riesgos

### 🟧 Q-Learning
- Aprende el mejor futuro posible
- Más agresivo
- Busca rutas óptimas aunque tengan riesgo

## 🔥 Mejoras implementadas
- Reward shaping
- Penalización de loops
- Estado con posición real
- Barra de progreso global
- IA más estable
""")
