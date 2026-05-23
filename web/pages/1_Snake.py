import streamlit as st
import random
import numpy as np
import time
import json
from PIL import Image, ImageDraw

from utils.supabase_client import supabase
from utils.session import get_user

# =====================================================
# 🧠 CONFIG GENERAL
# =====================================================

st.set_page_config(page_title="Snake IA", layout="wide")

st.title("🐍 Snake IA (Q-Learning)")

user = get_user()

# =====================================================
# 🌍 STATE GLOBAL
# =====================================================

if "Q" not in st.session_state:
    st.session_state.Q = {}

if "scores" not in st.session_state:
    st.session_state.scores = []

# =====================================================
# 🎮 MODE
# =====================================================

modo = st.selectbox("Modo", [
    "Entrenar IA",
    "Simulación IA",
    "Ver Q-Table",
    "Explicación"
])

# =====================================================
# 🧱 ENTORNO
# =====================================================

GRID = 18
dirs = ['UP', 'RIGHT', 'DOWN', 'LEFT']

def reset_env():
    snake = [(9, 9)]
    food = (random.randint(0, 17), random.randint(0, 17))
    direction = random.choice(dirs)
    return snake, food, direction

def check_collision(snake):
    head = snake[0]
    return (
        head[0] < 0 or head[0] >= GRID or
        head[1] < 0 or head[1] >= GRID or
        head in snake[1:]
    )

def move(snake, direction, action, food):

    idx = dirs.index(direction)

    if action == 0:
        direction = dirs[(idx - 1) % 4]
    elif action == 2:
        direction = dirs[(idx + 1) % 4]

    x, y = snake[0]

    if direction == 'UP':
        y -= 1
    elif direction == 'DOWN':
        y += 1
    elif direction == 'LEFT':
        x -= 1
    elif direction == 'RIGHT':
        x += 1

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
# 🧠 ESTADO / RL
# =====================================================

def get_state(snake, food, direction):

    head = snake[0]
    idx = dirs.index(direction)

    danger = []

    for act in [1, 0, 2]:
        tmp = snake.copy()
        tmp_dir = direction

        if act == 0:
            tmp_dir = dirs[(idx - 1) % 4]
        elif act == 2:
            tmp_dir = dirs[(idx + 1) % 4]

        x, y = tmp[0]

        if tmp_dir == 'UP':
            y -= 1
        elif tmp_dir == 'DOWN':
            y += 1
        elif tmp_dir == 'LEFT':
            x -= 1
        elif tmp_dir == 'RIGHT':
            x += 1

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

def choose_action(state):
    Q = st.session_state.Q

    if state not in Q:
        Q[state] = [0, 0, 0]

    if random.random() < 0.1:
        return random.randint(0, 2)

    return int(np.argmax(Q[state]))

def update_q(state, action, reward, next_state):

    Q = st.session_state.Q
    alpha = 0.1
    gamma = 0.9

    if state not in Q:
        Q[state] = [0, 0, 0]
    if next_state not in Q:
        Q[next_state] = [0, 0, 0]

    Q[state][action] += alpha * (
        reward + gamma * np.max(Q[next_state]) - Q[state][action]
    )

# =====================================================
# 🎨 DRAW
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
# 🏋️ ENTRENAMIENTO
# =====================================================

if modo == "Entrenar IA":

    episodes = st.slider("Episodios", 1000, 30000, 5000, step=1000)

    if st.button("Entrenar"):

        st.session_state.Q = {}
        st.session_state.scores = []

        progress = st.progress(0)
        log = st.empty()

        for ep in range(episodes):

            snake, food, direction = reset_env()
            state = get_state(snake, food, direction)

            score = 0
            done = False

            for _ in range(200):

                action = choose_action(state)

                snake, direction, food, reward, done = move(
                    snake, direction, action, food
                )

                next_state = get_state(snake, food, direction)

                update_q(state, action, reward, next_state)

                state = next_state

                if reward == 20:
                    score += 1

                if done:
                    break

            st.session_state.scores.append(score)

            if ep % 200 == 0:
                log.text(f"Episodio {ep}/{episodes}")

            progress.progress((ep + 1) / episodes)

        st.success("Entrenamiento completado")

        # 💾 SUPABASE
        if user:
            supabase.table("snake_stats").insert({
                "user_id": user.id,
                "display_name": user.user_metadata.get("display_name"),
                "max_score": max(st.session_state.scores),
                "last_score": st.session_state.scores[-1],
                "episodes": episodes,
                "algorithm": "Q-Learning"
            }).execute()

# =====================================================
# 📊 GRÁFICA
# =====================================================

if modo == "Entrenar IA" and st.session_state.scores:

    import matplotlib.pyplot as plt

    scores = st.session_state.scores
    media = [np.mean(scores[max(0, i-50):i+1]) for i in range(len(scores))]

    fig, ax = plt.subplots()
    ax.plot(scores, alpha=0.3)
    ax.plot(media)

    st.pyplot(fig)

# =====================================================
# 🔵 SIMULACIÓN
# =====================================================

if modo == "Simulación IA":

    if not st.session_state.Q:
        st.warning("⚠️ Primero entrena la IA")
    else:

        snake, food, direction = reset_env()
        placeholder = st.empty()

        score = 0
        done = False

        for _ in range(300):

            state = get_state(snake, food, direction)
            action = choose_action(state)

            snake, direction, food, reward, done = move(
                snake, direction, action, food
            )

            if reward == 20:
                score += 1

            placeholder.image(draw(snake, food), width=360)
            time.sleep(0.08)

            if done:
                break

        st.success(f"💀 Game Over | Score: {score}")

# =====================================================
# 📥 Q-TABLE
# =====================================================

if modo == "Ver Q-Table":

    Q = st.session_state.Q

    st.write(f"Estados aprendidos: {len(Q)}")

    st.json(dict(list(Q.items())[:20]))

    st.download_button(
        "⬇️ Descargar Q-Table",
        data=json.dumps(Q),
        file_name="snake_qtable.json"
    )

# =====================================================
# 📄 EXPLICACIÓN
# =====================================================

if modo == "Explicación":

    st.markdown("""
## 🧠 Snake IA

Este juego utiliza Q-Learning.

La IA aprende mediante:
- recompensa por comer comida
- penalización por morir
- exploración de estados

Sin entrenamiento, la IA no tiene conocimiento previo.

La Q-table representa la “memoria” del agente.
""")
