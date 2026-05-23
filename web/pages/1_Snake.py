import streamlit as st
import random
import numpy as np
import time
import json
from PIL import Image, ImageDraw

from utils.session import get_user

# =====================================================
# CONFIG
# =====================================================

st.set_page_config(page_title="Snake IA", layout="wide")
st.title("🐍 Snake IA (SARSA - Replay estable)")

user = get_user()

# =====================================================
# STATE
# =====================================================

if "Q" not in st.session_state:
    st.session_state.Q = {}

if "scores" not in st.session_state:
    st.session_state.scores = []

# =====================================================
# MODE
# =====================================================

modo = st.selectbox("Modo", [
    "Entrenar IA",
    "Simulación IA",
    "Ver Q-Table",
    "Explicación"
])

# =====================================================
# ENV
# =====================================================

GRID = 18
dirs = ['UP', 'RIGHT', 'DOWN', 'LEFT']

def reset_env():
    return [(9, 9)], (random.randint(0, 17), random.randint(0, 17)), random.choice(dirs)

def check_collision(snake):
    h = snake[0]
    return (
        h in snake[1:] or
        h[0] < 0 or h[0] >= GRID or
        h[1] < 0 or h[1] >= GRID
    )

def move(snake, direction, action, food):

    idx = dirs.index(direction)

    if action == 0:
        direction = dirs[(idx - 1) % 4]
    elif action == 2:
        direction = dirs[(idx + 1) % 4]

    x, y = snake[0]

    if direction == "UP": y -= 1
    if direction == "DOWN": y += 1
    if direction == "LEFT": x -= 1
    if direction == "RIGHT": x += 1

    new_head = (x, y)
    snake.insert(0, new_head)

    reward = -0.1
    done = check_collision(snake)

    if new_head == food:
        reward = 20
        food = (random.randint(0, 17), random.randint(0, 17))
    else:
        snake.pop()

    return snake, direction, food, reward, done

# =====================================================
# STATE + SARSA
# =====================================================

def get_state(snake, food, direction):

    head = snake[0]
    idx = dirs.index(direction)

    danger = []

    for act in [1, 0, 2]:
        tmp = snake.copy()
        d = direction

        if act == 0:
            d = dirs[(idx - 1) % 4]
        elif act == 2:
            d = dirs[(idx + 1) % 4]

        x, y = tmp[0]

        if d == "UP": y -= 1
        if d == "DOWN": y += 1
        if d == "LEFT": x -= 1
        if d == "RIGHT": x += 1

        tmp.insert(0, (x, y))
        if (x, y) != food:
            tmp.pop()

        danger.append(int(check_collision(tmp)))

    food_dir = [
        int(food[1] < head[1]),
        int(food[1] > head[1]),
        int(food[0] < head[0]),
        int(food[0] > head[0])
    ]

    return tuple(danger + food_dir + [idx])

def choose(state):
    Q = st.session_state.Q

    if state not in Q:
        Q[state] = [0, 0, 0]

    if random.random() < 0.1:
        return random.randint(0, 2)

    return int(np.argmax(Q[state]))

def update(s, a, r, ns, na):
    Q = st.session_state.Q
    alpha = 0.1
    gamma = 0.9

    if s not in Q:
        Q[s] = [0, 0, 0]
    if ns not in Q:
        Q[ns] = [0, 0, 0]

    Q[s][a] += alpha * (r + gamma * Q[ns][na] - Q[s][a])

# =====================================================
# DRAW
# =====================================================

def draw(snake, food):

    img = Image.new("RGB", (360, 360), (0, 0, 0))
    d = ImageDraw.Draw(img)

    for s in snake:
        d.rectangle(
            [s[0]*20, s[1]*20, s[0]*20+20, s[1]*20+20],
            fill=(0, 255, 0)
        )

    fx, fy = food
    d.rectangle(
        [fx*20, fy*20, fx*20+20, fy*20+20],
        fill=(255, 0, 0)
    )

    return img

# =====================================================
# TRAINING (FIX PROGRESO)
# =====================================================

if modo == "Entrenar IA":

    episodes = st.slider("Episodios", 1000, 20000, 5000, 1000)

    if st.button("Entrenar"):

        st.session_state.Q = {}
        st.session_state.scores = []

        status = st.empty()

        for ep in range(episodes):

            snake, food, direction = reset_env()

            s = get_state(snake, food, direction)
            a = choose(s)

            score = 0

            for _ in range(200):

                snake, direction, food, r, done = move(
                    snake, direction, a, food
                )

                ns = get_state(snake, food, direction)
                na = choose(ns)

                update(s, a, r, ns, na)

                s, a = ns, na

                if r == 20:
                    score += 1

                if done:
                    break

            st.session_state.scores.append(score)

            if ep % 200 == 0:
                status.text(f"Entrenando... {ep}/{episodes}")

        status.success("✅ Entrenamiento completado")

# =====================================================
# SIMULACIÓN (REPLAY ESTABLE)
# =====================================================

if modo == "Simulación IA":

    if st.button("▶ Iniciar simulación"):

        snake, food, direction = reset_env()
        Q = st.session_state.Q

        frames = []
        score = 0

        # ===============================
        # 1. SIMULACIÓN (SIN UI)
        # ===============================

        for _ in range(200):

            state = get_state(snake, food, direction)

            if state not in Q:
                action = random.randint(0, 2)
            else:
                action = int(np.argmax(Q[state]))

            snake, direction, food, r, done = move(
                snake, direction, action, food
            )

            if r == 20:
                score += 1

            frames.append((snake.copy(), food))

            if done:
                break

        # ===============================
        # 2. REPLAY VISUAL
        # ===============================

        placeholder = st.empty()

        for s_frame, f_frame in frames:

            placeholder.image(draw(s_frame, f_frame), width=360)

            time.sleep(1.0)  # 🔥 lento para ver bien (debug)

        st.success(f"💀 Score: {score}")

# =====================================================
# Q-TABLE
# =====================================================

if modo == "Ver Q-Table":

    Q = st.session_state.Q

    st.write(f"Estados: {len(Q)}")

    st.json({str(k): v for k, v in list(Q.items())[:20]})

# =====================================================
# EXPLICACIÓN
# =====================================================

if modo == "Explicación":

    st.markdown("""
## 🧠 Snake IA (SARSA)

- Entrenamiento offline (sin render)
- Simulación con replay de frames
- Evita problemas de Streamlit en tiempo real
- Aprendizaje mediante Q-table (SARSA)
""")
