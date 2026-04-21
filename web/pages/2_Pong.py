import streamlit as st
import time
from PIL import Image, ImageDraw

from utils.supabase_client import supabase
from utils.session import get_user

st.set_page_config(page_title="Pong IA", layout="wide")
st.title("🏓 Pong IA Autoplay (estable)")

user = get_user()

WIN_SCORE = 5

# ---------------- INIT STATE ----------------
if "ball" not in st.session_state:
    st.session_state.ball = [200, 100]
    st.session_state.vx = 3
    st.session_state.vy = 2
    st.session_state.player_y = 80
    st.session_state.ai_y = 80
    st.session_state.score_p = 0
    st.session_state.score_ai = 0
    st.session_state.game_over = False
    st.session_state.running = False

# 🔥 FIX SPEED ERROR
if "speed" not in st.session_state:
    st.session_state.speed = 0.05


# ---------------- CONTROLS ----------------
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("▶️ Start"):
        st.session_state.running = True

with col2:
    if st.button("⏸ Pause"):
        st.session_state.running = False

with col3:
    st.session_state.speed = st.slider(
        "Velocidad", 0.01, 0.2, st.session_state.speed
    )


# ---------------- RESET ----------------
if st.button("Reset"):
    st.session_state.ball = [200, 100]
    st.session_state.vx = 3
    st.session_state.vy = 2
    st.session_state.player_y = 80
    st.session_state.ai_y = 80
    st.session_state.score_p = 0
    st.session_state.score_ai = 0
    st.session_state.game_over = False
    st.session_state.running = False
    st.rerun()


# ---------------- STEP ----------------
def step():
    ball = st.session_state.ball
    vx = st.session_state.vx
    vy = st.session_state.vy

    ball[0] += vx
    ball[1] += vy

    if ball[1] <= 0 or ball[1] >= 190:
        vy *= -1

    # IA simple
    if ball[1] > st.session_state.ai_y:
        st.session_state.ai_y += 3
    else:
        st.session_state.ai_y -= 3

    st.session_state.ai_y = max(0, min(150, st.session_state.ai_y))

    # colisión IA
    if ball[0] >= 380 and abs(ball[1] - st.session_state.ai_y) < 50:
        vx *= -1

    # scoring
    if ball[0] < 0:
        st.session_state.score_ai += 1
        ball = [200, 100]

    if ball[0] > 400:
        st.session_state.score_p += 1
        ball = [200, 100]

    st.session_state.ball = ball
    st.session_state.vx = vx
    st.session_state.vy = vy


# ---------------- FIN ----------------
if st.session_state.score_p >= WIN_SCORE:
    st.success("🏆 Has ganado")
    st.session_state.game_over = True
    st.session_state.running = False

if st.session_state.score_ai >= WIN_SCORE:
    st.error("💀 Gana la IA")
    st.session_state.game_over = True
    st.session_state.running = False


# ---------------- DRAW ----------------
def draw():
    img = Image.new("RGB", (400, 200), (0, 0, 0))
    d = ImageDraw.Draw(img)

    x, y = st.session_state.ball

    d.ellipse([x, y, x+10, y+10], fill=(255, 255, 255))

    d.rectangle([10, st.session_state.player_y, 20, st.session_state.player_y + 50], fill=(0, 255, 0))
    d.rectangle([380, st.session_state.ai_y, 390, st.session_state.ai_y + 50], fill=(255, 0, 0))

    return img


placeholder = st.empty()

st.write(f"Jugador: {st.session_state.score_p} | IA: {st.session_state.score_ai}")

# ---------------- LOOP CONTROLADO ----------------
if st.session_state.running and not st.session_state.game_over:
    step()
    placeholder.image(draw(), width=400)
    time.sleep(st.session_state.speed)
    st.rerun()
else:
    placeholder.image(draw(), width=400)
