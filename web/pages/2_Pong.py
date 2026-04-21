import streamlit as st
import time
from PIL import Image, ImageDraw

from utils.session import get_user

st.set_page_config(page_title="Pong IA", layout="wide")
st.title("🏓 Pong estable")

user = get_user()

WIN_SCORE = 5

# ---------------- STATE ----------------
if "ball" not in st.session_state:
    st.session_state.ball = [200, 100]
    st.session_state.vx = 4
    st.session_state.vy = 3
    st.session_state.player_y = 80
    st.session_state.ai_y = 80
    st.session_state.score_p = 0
    st.session_state.score_ai = 0
    st.session_state.running = False


# ---------------- CONTROLS ----------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("▶️ Start"):
        st.session_state.running = True

with col2:
    if st.button("⏸ Stop"):
        st.session_state.running = False

with col3:
    if st.button("⬆️"):
        st.session_state.player_y -= 15

with col4:
    if st.button("⬇️"):
        st.session_state.player_y += 15

st.session_state.player_y = max(0, min(150, st.session_state.player_y))


# ---------------- STEP ----------------
def step():
    ball = st.session_state.ball
    vx = st.session_state.vx
    vy = st.session_state.vy

    x, y = ball

    x += vx
    y += vy

    # rebote arriba/abajo
    if y <= 0 or y >= 190:
        vy *= -1

    # IA simple
    if y > st.session_state.ai_y:
        st.session_state.ai_y += 3
    else:
        st.session_state.ai_y -= 3

    st.session_state.ai_y = max(0, min(150, st.session_state.ai_y))

    # 🟢 COLISIÓN JUGADOR (FIX REAL)
    if x <= 20:
        if st.session_state.player_y <= y <= st.session_state.player_y + 50:
            vx *= -1
            x = 20  # evita atravesar

    # 🔴 COLISIÓN IA
    if x >= 380:
        if st.session_state.ai_y <= y <= st.session_state.ai_y + 50:
            vx *= -1
            x = 380

    # puntos
    if x < 0:
        st.session_state.score_ai += 1
        x, y = 200, 100

    if x > 400:
        st.session_state.score_p += 1
        x, y = 200, 100

    st.session_state.ball = [x, y]
    st.session_state.vx = vx
    st.session_state.vy = vy


# ---------------- DRAW ----------------
def draw():
    img = Image.new("RGB", (400, 200), (0, 0, 0))
    d = ImageDraw.Draw(img)

    x, y = st.session_state.ball

    d.ellipse([x, y, x+10, y+10], fill=(255, 255, 255))

    d.rectangle([10, st.session_state.player_y, 20, st.session_state.player_y+50], fill=(0, 255, 0))
    d.rectangle([380, st.session_state.ai_y, 390, st.session_state.ai_y+50], fill=(255, 0, 0))

    return img


placeholder = st.empty()

st.write(f"Jugador {st.session_state.score_p} - IA {st.session_state.score_ai}")

if st.session_state.running:
    step()
    placeholder.image(draw(), width=400)
    time.sleep(0.03)
    st.rerun()
else:
    placeholder.image(draw(), width=400)
