import streamlit as st
from PIL import Image, ImageDraw

st.title("🏓 Pong estable")

# ---------------- STATE ----------------
if "ball" not in st.session_state:
    st.session_state.ball = [200, 100]
    st.session_state.vx = 4
    st.session_state.vy = 3

if "player_y" not in st.session_state:
    st.session_state.player_y = 80

if "ai_y" not in st.session_state:
    st.session_state.ai_y = 80

if "running" not in st.session_state:
    st.session_state.running = False

# ---------------- CONTROLS ----------------
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("⬆️"):
        st.session_state.player_y -= 15

with col2:
    if st.button("⬇️"):
        st.session_state.player_y += 15

with col3:
    if st.button("▶ Play / Pause"):
        st.session_state.running = not st.session_state.running

st.session_state.player_y = max(0, min(150, st.session_state.player_y))

# ---------------- STEP ----------------
def step():
    ball = st.session_state.ball
    vx = st.session_state.vx
    vy = st.session_state.vy

    # movimiento pelota SIEMPRE
    ball[0] += vx
    ball[1] += vy

    # rebotes
    if ball[1] <= 0 or ball[1] >= 190:
        st.session_state.vy *= -1

    # IA
    if ball[1] > st.session_state.ai_y:
        st.session_state.ai_y += 3
    else:
        st.session_state.ai_y -= 3

    st.session_state.ai_y = max(0, min(150, st.session_state.ai_y))

    # colisiones
    if ball[0] <= 20 and abs(ball[1] - st.session_state.player_y) < 50:
        st.session_state.vx *= -1

    if ball[0] >= 380 and abs(ball[1] - st.session_state.ai_y) < 50:
        st.session_state.vx *= -1

    # reset ball
    if ball[0] < 0 or ball[0] > 400:
        ball[0], ball[1] = 200, 100

    st.session_state.ball = ball

# ---------------- AUTO LOOP CONTROLADO ----------------
if st.session_state.running:
    step()
    st.rerun()

# ---------------- DRAW ----------------
def draw():
    img = Image.new("RGB", (400, 200), (0, 0, 0))
    d = ImageDraw.Draw(img)

    x, y = st.session_state.ball

    d.ellipse([x, y, x+10, y+10], fill=(255,255,255))

    d.rectangle([10, st.session_state.player_y, 20, st.session_state.player_y+50], fill=(0,255,0))
    d.rectangle([380, st.session_state.ai_y, 390, st.session_state.ai_y+50], fill=(255,0,0))

    return img

st.image(draw())
