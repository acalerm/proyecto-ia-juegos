import streamlit as st
import random
import time
from PIL import Image, ImageDraw

from utils.session import get_user

st.set_page_config(page_title="Snake IA", layout="wide")
st.title("🐍 Snake IA")

user = get_user()

# ---------------- INIT ----------------
if "snake" not in st.session_state:
    st.session_state.snake = [(9, 9)]

if "food" not in st.session_state:
    st.session_state.food = (5, 5)

if "direction" not in st.session_state:
    st.session_state.direction = "RIGHT"

if "running" not in st.session_state:
    st.session_state.running = False

# ---------------- CONTROLS ----------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("⬆️"):
        st.session_state.direction = "UP"

with col2:
    if st.button("⬇️"):
        st.session_state.direction = "DOWN"

with col3:
    if st.button("⬅️"):
        st.session_state.direction = "LEFT"

with col4:
    if st.button("➡️"):
        st.session_state.direction = "RIGHT"

if st.button("▶ Start / Pause"):
    st.session_state.running = not st.session_state.running

if st.button("🔄 Reset"):
    st.session_state.snake = [(9, 9)]
    st.session_state.food = (5, 5)
    st.session_state.direction = "RIGHT"
    st.session_state.running = False
    st.rerun()

# ---------------- MOVE ----------------
def step():
    head = st.session_state.snake[0]
    x, y = head

    if st.session_state.direction == "UP":
        y -= 1
    if st.session_state.direction == "DOWN":
        y += 1
    if st.session_state.direction == "LEFT":
        x -= 1
    if st.session_state.direction == "RIGHT":
        x += 1

    new_head = (x, y)

    # colisión
    if x < 0 or x > 17 or y < 0 or y > 17 or new_head in st.session_state.snake:
        st.session_state.running = False
        return

    st.session_state.snake.insert(0, new_head)

    # comida
    if new_head == st.session_state.food:
        st.session_state.food = (random.randint(0,17), random.randint(0,17))
    else:
        st.session_state.snake.pop()

# ---------------- RUN ----------------
if st.session_state.running:
    step()
    time.sleep(0.15)
    st.rerun()

# ---------------- DRAW ----------------
def draw():
    img = Image.new("RGB", (360, 360), (0,0,0))
    d = ImageDraw.Draw(img)

    for s in st.session_state.snake:
        d.rectangle([s[0]*20, s[1]*20, s[0]*20+20, s[1]*20+20], fill=(0,255,0))

    fx, fy = st.session_state.food
    d.rectangle([fx*20, fy*20, fx*20+20, fy*20+20], fill=(255,0,0))

    return img

st.image(draw())
