import streamlit as st
import time
from PIL import Image, ImageDraw

from utils.session import get_user
from utils.supabase_client import supabase

st.set_page_config(page_title="Pong IA", layout="wide")
st.title("🏓 Pong IA vs Humano")

user = get_user()

WIN_SCORE = 5

# ---------------- INIT STATE ----------------
if "ball" not in st.session_state:
    st.session_state.ball = [200, 100]
    st.session_state.vx = 4
    st.session_state.vy = 3

if "player_y" not in st.session_state:
    st.session_state.player_y = 80

if "ai_y" not in st.session_state:
    st.session_state.ai_y = 80

if "score_p" not in st.session_state:
    st.session_state.score_p = 0

if "score_ai" not in st.session_state:
    st.session_state.score_ai = 0

if "running" not in st.session_state:
    st.session_state.running = False

# ---------------- START ----------------
if st.button("▶ Start / Pause"):
    st.session_state.running = not st.session_state.running

# ---------------- CONTROLES ----------------
col1, col2 = st.columns(2)

with col1:
    if st.button("⬆️"):
        st.session_state.player_y -= 15

with col2:
    if st.button("⬇️"):
        st.session_state.player_y += 15

st.session_state.player_y = max(0, min(150, st.session_state.player_y))

# ---------------- RESET ----------------
if st.button("🔄 Reset"):
    for k in ["ball", "vx", "vy", "score_p", "score_ai"]:
        st.session_state.pop(k, None)
    st.session_state.running = False
    st.rerun()

# ---------------- GAME LOOP ----------------
if st.session_state.running:

    ball = st.session_state.ball
    vx = st.session_state.vx
    vy = st.session_state.vy

    # mover pelota SIEMPRE
    ball[0] += vx
    ball[1] += vy

    # rebotes arriba/abajo
    if ball[1] <= 0 or ball[1] >= 190:
        vy *= -1

    # IA simple
    if ball[1] > st.session_state.ai_y:
        st.session_state.ai_y += 3
    else:
        st.session_state.ai_y -= 3

    st.session_state.ai_y = max(0, min(150, st.session_state.ai_y))

    # colisión jugador
    if ball[0] <= 20:
        if abs(ball[1] - st.session_state.player_y) < 50:
            vx *= -1

    # colisión IA
    if ball[0] >= 380:
        if abs(ball[1] - st.session_state.ai_y) < 50:
            vx *= -1

    # puntos
    if ball[0] < 0:
        st.session_state.score_ai += 1
        ball = [200, 100]

    if ball[0] > 400:
        st.session_state.score_p += 1
        ball = [200, 100]

    st.session_state.ball = ball
    st.session_state.vx = vx
    st.session_state.vy = vy

    time.sleep(0.02)
    st.rerun()

# ---------------- DRAW ----------------
def draw():
    img = Image.new("RGB", (400, 200), (0, 0, 0))
    d = ImageDraw.Draw(img)

    x, y = st.session_state.ball

    d.ellipse([x, y, x+10, y+10], fill=(255, 255, 255))

    d.rectangle([10, st.session_state.player_y, 20, st.session_state.player_y+50], fill=(0,255,0))
    d.rectangle([380, st.session_state.ai_y, 390, st.session_state.ai_y+50], fill=(255,0,0))

    return img

st.write(f"Jugador: {st.session_state.score_p} | IA: {st.session_state.score_ai}")
st.image(draw())
