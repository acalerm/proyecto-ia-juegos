import streamlit as st
from PIL import Image, ImageDraw
import time

from utils.supabase_client import supabase
from utils.session import get_user

st.set_page_config(page_title="Pong IA", layout="wide")
st.title("🏓 Pong")

user = get_user()

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


# ---------------- GUARDAR ----------------
def guardar(resultado):
    if user:
        supabase.table("pong_stats").insert({
            "user_id": user.id,
            "display_name": user.user_metadata.get("display_name"),
            "result": resultado,
            "score_player": st.session_state.s1,
            "score_ai": st.session_state.s2
        }).execute()


# ---------------- CONTROLS ----------------
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    if st.button("▶️ Start"):
        st.session_state.running = True

with col2:
    if st.button("⏸ Stop"):
        st.session_state.running = False

with col3:
    if st.button("⬆️"):
        st.session_state.player -= 15

with col4:
    if st.button("⬇️"):
        st.session_state.player += 15

with col5:
    if st.button("🔄 Reset"):
        guardar("LOSE")

        st.session_state.ball = [200, 100]
        st.session_state.vx = 4
        st.session_state.vy = 3
        st.session_state.player = 80
        st.session_state.ai = 80
        st.session_state.s1 = 0
        st.session_state.s2 = 0
        st.session_state.running = False

with col6:
    if st.button("🎮 Simulación"):
        st.session_state.running = False
        st.session_state.simulate = True


st.session_state.player = max(0, min(150, st.session_state.player))


# ---------------- STEP ----------------
def step():
    x, y = st.session_state.ball
    vx = st.session_state.vx
    vy = st.session_state.vy

    x += vx
    y += vy

    if y <= 0 or y >= 190:
        vy *= -1

    # IA simple
    if y > st.session_state.ai:
        st.session_state.ai += 3
    else:
        st.session_state.ai -= 3

    st.session_state.ai = max(0, min(150, st.session_state.ai))

    # player collision
    if x <= 20 and st.session_state.player <= y <= st.session_state.player + 50:
        vx *= -1
        x = 20

    # ai collision
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


# ---------------- DRAW ----------------
def draw():
    img = Image.new("RGB", (400, 200), (0, 0, 0))
    d = ImageDraw.Draw(img)

    x, y = st.session_state.ball

    d.ellipse([x, y, x+10, y+10], fill=(255, 255, 255))

    d.rectangle([10, st.session_state.player, 20, st.session_state.player+50], fill=(0, 255, 0))
    d.rectangle([380, st.session_state.ai, 390, st.session_state.ai+50], fill=(255, 0, 0))

    return img


# ---------------- UI ----------------
st.write(f"{st.session_state.s1} - {st.session_state.s2}")

placeholder = st.empty()
placeholder.image(draw(), width=400)

# =====================================================
# SIMULATION MODE (NUEVO CONTROLADO)
# =====================================================

if "simulate" not in st.session_state:
    st.session_state.simulate = False


if st.session_state.simulate:

    speed = st.slider("Velocidad del juego", 0.01, 0.5, 0.1)

    if st.button("▶ Iniciar simulación"):
        st.session_state.simulate_running = True

    if st.button("⏹ Parar simulación"):
        st.session_state.simulate_running = False

    if st.button("🔄 Reset simulación"):
        st.session_state.ball = [200, 100]
        st.session_state.vx = 4
        st.session_state.vy = 3
        st.session_state.player = 80
        st.session_state.ai = 80
        st.session_state.s1 = 0
        st.session_state.s2 = 0
        st.session_state.simulate_running = False


# ---------------- LOOP SIMULACIÓN ----------------
if st.session_state.get("simulate_running", False):

    for _ in range(2000):

        step()
        placeholder.image(draw(), width=400)

        time.sleep(speed)

        if st.session_state.s1 >= WIN:
            guardar("WIN")
            st.success("🏆 Has ganado")
            st.session_state.simulate_running = False
            break

        if st.session_state.s2 >= WIN:
            guardar("LOSE")
            st.error("💀 Has perdido")
            st.session_state.simulate_running = False
            break
