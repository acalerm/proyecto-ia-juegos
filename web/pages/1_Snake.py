import streamlit as st
import numpy as np
import random
import time
from PIL import Image, ImageDraw

from utils.supabase_client import supabase
from utils.session import get_user

st.set_page_config(page_title="Snake IA", layout="wide")

st.title("🐍 Snake IA (SARSA vs Q-Learning)")

# 🔐 usuario
user = get_user()

st.write("Puedes usar la IA sin iniciar sesión 👤")

# ---------------- CONFIG ----------------
GRID_SIZE = 20
GRID_WIDTH = 18
GRID_HEIGHT = 18

BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

dirs = ['UP', 'RIGHT', 'DOWN', 'LEFT']

# ---------------- UI ----------------
modo = st.selectbox("Modo", [
    "Entrenar IA",
    "Ver aprendizaje",
    "Ver IA jugar"
])

algoritmo = st.selectbox("Algoritmo", ["SARSA", "Q-Learning"])

episodios = st.slider("Episodios", 100, 100000, 5000, step=100)
velocidad = st.slider("Velocidad", 0.01, 0.2, 0.05)

placeholder = st.empty()

# ---------------- STATE ----------------
if "Q" not in st.session_state:
    st.session_state.Q = {}

if "scores" not in st.session_state:
    st.session_state.scores = []

# ---------------- FUNCIONES ----------------
def reset_env():
    snake = [(9, 9)]
    food = (random.randint(0, 17), random.randint(0, 17))
    direction = random.choice(dirs)
    return snake, food, direction

def check_collision(snake):
    head = snake[0]
    return (
        head[0] < 0 or head[0] >= 18 or
        head[1] < 0 or head[1] >= 18 or
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

def get_state(snake, food, direction):
    head = snake[0]
    idx = dirs.index(direction)

    danger = [0, 0, 0]

    for i, act in enumerate([1, 0, 2]):
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

        danger[i] = int(check_collision(tmp))

    food_dir = [
        int(food[1] < head[1]),
        int(food[1] > head[1]),
        int(food[0] < head[0]),
        int(food[0] > head[0])
    ]

    return tuple(danger + food_dir + [idx])

def choose_action(state):
    Q = st.session_state.Q
    epsilon = 0.1

    if state not in Q:
        Q[state] = [0, 0, 0]

    if random.random() < epsilon:
        return random.choice([0, 1, 2])

    return int(np.argmax(Q[state]))

def update_q(state, action, reward, next_state, next_action):
    Q = st.session_state.Q
    alpha = 0.1
    gamma = 0.9

    if state not in Q:
        Q[state] = [0, 0, 0]
    if next_state not in Q:
        Q[next_state] = [0, 0, 0]

    if algoritmo == "SARSA":
        Q[state][action] += alpha * (reward + gamma * Q[next_state][next_action] - Q[state][action])
    else:
        Q[state][action] += alpha * (reward + gamma * np.max(Q[next_state]) - Q[state][action])

def draw(snake, food):
    img = Image.new("RGB", (360, 360), BLACK)
    d = ImageDraw.Draw(img)

    for s in snake:
        d.rectangle([s[0]*20, s[1]*20, s[0]*20+20, s[1]*20+20], fill=GREEN)

    d.rectangle([food[0]*20, food[1]*20, food[0]*20+20, food[1]*20+20], fill=RED)

    return img

# ---------------- DEMO ARREGLADA ----------------
if modo == "Ver IA jugar" and st.button("Jugar"):

    snake, food, direction = reset_env()
    done = False
    score = 0

    placeholder = st.empty()

    for _ in range(1000):  # 🔥 FIX STREAMLIT

        if done:
            break

        state = get_state(snake, food, direction)
        action = choose_action(state)

        snake, direction, food, reward, done = move(snake, direction, action, food)

        if reward == 20:
            score += 1

        placeholder.image(draw(snake, food), width=360)
        time.sleep(velocidad)

    st.success(f"💀 Game Over - Score: {score}")
