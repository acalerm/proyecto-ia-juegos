import streamlit as st
import numpy as np
import random
import time
from PIL import Image, ImageDraw

from utils.supabase_client import supabase
from utils.session import get_user

st.set_page_config(page_title="Snake IA", layout="wide")
st.title("🐍 Snake IA Autoplay (estable)")

user = get_user()

# ---------------- CONFIG ----------------
dirs = ['UP', 'RIGHT', 'DOWN', 'LEFT']
placeholder = st.empty()

# ---------------- STATE ----------------
if "Q" not in st.session_state:
    st.session_state.Q = {}

if "snake_running" not in st.session_state:
    st.session_state.snake_running = False
    st.session_state.running = False
    st.session_state.snake = None
    st.session_state.food = None
    st.session_state.direction = None
    st.session_state.score = 0


# ---------------- UI ----------------
col1, col2 = st.columns(2)

with col1:
    if st.button("▶️ Start IA"):
        st.session_state.snake_running = True
        st.session_state.running = True
        st.session_state.snake = [(9, 9)]
        st.session_state.food = (random.randint(0, 17), random.randint(0, 17))
        st.session_state.direction = random.choice(dirs)
        st.session_state.score = 0

with col2:
    if st.button("⏸ Pause"):
        st.session_state.running = False


# ---------------- STEP ----------------
def step():
    state = get_state(st.session_state.snake, st.session_state.food, st.session_state.direction)
    action = choose_action(state)

    snake, direction, food, reward, done = move(
        st.session_state.snake,
        st.session_state.direction,
        action,
        st.session_state.food
    )

    st.session_state.snake = snake
    st.session_state.direction = direction
    st.session_state.food = food

    if reward == 20:
        st.session_state.score += 1

    if done:
        st.session_state.running = False
        st.session_state.snake_running = False
        st.success(f"Game Over - Score: {st.session_state.score}")


# ---------------- DRAW ----------------
def draw(snake, food):
    img = Image.new("RGB", (360, 360), (0, 0, 0))
    d = ImageDraw.Draw(img)

    for s in snake:
        d.rectangle([s[0]*20, s[1]*20, s[0]*20+20, s[1]*20+20], fill=(0, 255, 0))

    d.rectangle([food[0]*20, food[1]*20, food[0]*20+20, food[1]*20+20], fill=(255, 0, 0))

    return img


st.write(f"Score: {st.session_state.score}")

# ---------------- LOOP CONTROLADO ----------------
if st.session_state.running and st.session_state.snake_running:

    step()

    placeholder.image(
        draw(st.session_state.snake, st.session_state.food),
        width=360
    )

    time.sleep(0.05)
    st.rerun()

else:
    if st.session_state.snake:
        placeholder.image(draw(st.session_state.snake, st.session_state.food), width=360)
