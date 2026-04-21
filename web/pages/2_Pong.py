import streamlit as st
import time
from PIL import Image, ImageDraw

st.set_page_config(page_title="Pong IA", layout="wide")
st.title("🏓 Pong FIX estable")

WIN = 5

# ---------------- INIT ----------------
if "ball" not in st.session_state:
    st.session_state.ball = [200, 100]
    st.session_state.vx = 4
    st.session_state.vy = 3
    st.session_state.player = 80
    st.session_state.ai = 80
    st.session_state.s1 = 0
    st.session_state.s2 = 0
    st.session_state.running = False


# ---------------- CONTROLS ----------------
col1, col2 = st.columns(2)

with col1:
    if st.button("▶️ Start"):
        st.session_state.running = True

with col2:
    if st.button("⏸ Stop"):
        st.session_state.running = False


# ---------------- PLAYER MOVE ----------------
col3, col4 = st.columns(2)

with col3:
    if st.button("⬆️"):
        st.session_state.player -= 15

with col4:
    if st.button("⬇️"):
        st.session_state.player += 15

st.session_state.player = max(0, min(150, st.session_state.player))


# ---------------- STEP ----------------
def step():
    x, y = st.session_state.ball
    vx, vy = st.session_state.vx, st.session_state.vy

    x += vx
    y += vy

    if y <= 0 or y >= 190:
        vy *= -1

    # IA
    if y > st.session_state.ai:
        st.session_state.ai += 3
    else:
        st.session_state.ai -= 3

    st.session_state.ai = max(0, min(150, st.session_state.ai))

    # player collision FIX
    if x <= 20 and st.session_state.player <= y <= st.session_state.player + 50:
        vx *= -1
        x = 20

    # ai collision FIX
    if x >= 380 and st.session_state.ai <= y <= st.session_state.ai + 50:
        vx *= -1
        x = 380

    # score
    if x < 0:
        st.session_state.s2 += 1
        x, y = 200, 100

    if x > 400:
        st.session_state.s1 += 1
        x, y = 200, 100

    st.session_state.ball = [x, y]
    st.session_state.vx = vx
    st.session_state.vy = vy


# ---------------- DRAW (SIEMPRE PRIMERO) ----------------
def draw():
    img = Image.new("RGB", (400, 200), (0, 0, 0))
    d = ImageDraw.Draw(img)

    x, y = st.session_state.ball

    d.ellipse([x, y, x+10, y+10], fill=(255, 255, 255))

    d.rectangle([10, st.session_state.player, 20, st.session_state.player+50], fill=(0, 255, 0))
    d.rectangle([380, st.session_state.ai, 390, st.session_state.ai+50], fill=(255, 0, 0))

    return img


placeholder = st.empty()

placeholder.image(draw(), width=400)
st.write(f"{st.session_state.s1} - {st.session_state.s2}")

# ---------------- LOOP ----------------
if st.session_state.running:
    time.sleep(0.03)
    step()
    st.rerun()
