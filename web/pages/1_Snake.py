import streamlit as st
import random
import time
from PIL import Image, ImageDraw

st.set_page_config(page_title="Snake IA", layout="wide")
st.title("🐍 Snake estable FIX")

dirs = ["UP", "RIGHT", "DOWN", "LEFT"]

# ---------------- INIT ----------------
if "snake" not in st.session_state:
    st.session_state.snake = [(9, 9)]
    st.session_state.food = (5, 5)
    st.session_state.running = False
    st.session_state.score = 0
    st.session_state.direction = "RIGHT"


# ---------------- CONTROLS ----------------
col1, col2 = st.columns(2)

with col1:
    if st.button("▶️ Start"):
        st.session_state.running = True

with col2:
    if st.button("⏸ Stop"):
        st.session_state.running = False


# ---------------- MOVE ----------------
def step():
    snake = st.session_state.snake
    x, y = snake[0]

    if st.session_state.direction == "UP":
        y -= 1
    elif st.session_state.direction == "DOWN":
        y += 1
    elif st.session_state.direction == "LEFT":
        x -= 1
    elif st.session_state.direction == "RIGHT":
        x += 1

    new_head = (x, y)
    snake.insert(0, new_head)

    if new_head == st.session_state.food:
        st.session_state.score += 1
        st.session_state.food = (random.randint(0, 17), random.randint(0, 17))
    else:
        snake.pop()

    # colisión
    if x < 0 or x > 17 or y < 0 or y > 17 or new_head in snake[1:]:
        st.session_state.running = False


# ---------------- DRAW ----------------
def draw():
    img = Image.new("RGB", (360, 360), (0, 0, 0))
    d = ImageDraw.Draw(img)

    for s in st.session_state.snake:
        d.rectangle([s[0]*20, s[1]*20, s[0]*20+20, s[1]*20+20], fill=(0, 255, 0))

    f = st.session_state.food
    d.rectangle([f[0]*20, f[1]*20, f[0]*20+20, f[1]*20+20], fill=(255, 0, 0))

    return img


# ---------------- RENDER SIEMPRE PRIMERO ----------------
placeholder = st.empty()

placeholder.image(draw(), width=360)
st.write(f"Score: {st.session_state.score}")

# ---------------- LOOP CONTROLADO ----------------
if st.session_state.running:
    time.sleep(0.08)
    step()
    st.rerun()
