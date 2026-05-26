import streamlit as st
from PIL import Image, ImageDraw
import time

from utils.supabase_client import supabase
from utils.session import get_user

st.set_page_config(page_title="Pong IA", layout="wide")
st.title("🏓 Pong IA")

user = get_user()

WIN = 5

# ---------------- MODE ----------------
mode = st.selectbox("Modo", [
    "Jugador vs IA",
    "IA vs Automático"
])

difficulty = None
if mode == "IA vs Automático":
    difficulty = st.selectbox("Dificultad automático", [
        "Fácil",
        "Avanzado"
    ])

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

if "ai_dir" not in st.session_state:
    st.session_state.ai_dir = 2

if "result" not in st.session_state:
    st.session_state.result = None


# ---------------- SAVE ----------------
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
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("▶️ Start"):
        st.session_state.running = True
        st.session_state.result = None

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
        st.session_state.ai_dir = 2
        st.session_state.result = None

if not isinstance(st.session_state.player, (int, float)):
    st.session_state.player = 80

if not isinstance(st.session_state.ai, (int, float)):
    st.session_state.ai = 80
    
st.session_state.player = max(0, min(150, st.session_state.player))
st.session_state.ai = max(0, min(150, st.session_state.ai))

# ---------------- SPEED ----------------
speed = st.slider("Velocidad del juego", 0.01, 0.3, 0.08)


# ---------------- STEP ----------------
def step():
    x, y = st.session_state.ball
    vx = st.session_state.vx
    vy = st.session_state.vy

    x += vx
    y += vy

    if y <= 0 or y >= 190:
        vy *= -1

    # LEFT PADDLE
    if mode == "IA vs Automático":
        if y > st.session_state.player:
            st.session_state.player += 3
        else:
            st.session_state.player -= 3

    st.session_state.player = max(0, min(150, st.session_state.player))

    # RIGHT PADDLE
    if mode == "Jugador vs IA":
        if y > st.session_state.ai:
            st.session_state.ai += 3
        else:
            st.session_state.ai -= 3

    elif mode == "IA vs Automático":
        if difficulty == "Avanzado":
            if y > st.session_state.ai:
                st.session_state.ai += 2
            else:
                st.session_state.ai -= 2
        else:
            st.session_state.ai += st.session_state.ai_dir

            if st.session_state.ai <= 0:
                st.session_state.ai_dir = 2
            elif st.session_state.ai >= 150:
                st.session_state.ai_dir = -2

    st.session_state.ai = max(0, min(150, st.session_state.ai))

    # COLLISIONS
    if x <= 20 and st.session_state.player <= y <= st.session_state.player + 50:
        vx *= -1
        x = 20

    if x >= 380 and st.session_state.ai <= y <= st.session_state.ai + 50:
        vx *= -1
        x = 380

    # SCORE
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

if st.session_state.result == "WIN":
    st.success("🏆 Has ganado")
elif st.session_state.result == "LOSE":
    st.error("💀 Has perdido")
elif st.session_state.result == "LEFT_WIN":
    st.success("🏆 Ha ganado la izquierda")
elif st.session_state.result == "RIGHT_WIN":
    st.error("💀 Ha ganado la derecha")


placeholder = st.empty()
placeholder.image(draw(), width=400)


# ---------------- LOOP ----------------
if st.session_state.running:

    step()
    placeholder.image(draw(), width=400)

    time.sleep(speed)

    if st.session_state.s1 >= WIN:
        st.session_state.running = False

        if mode == "Jugador vs IA":
            st.session_state.result = "WIN"
            guardar("WIN")
        else:
            st.session_state.result = "LEFT_WIN"
            guardar("WIN")

    elif st.session_state.s2 >= WIN:
        st.session_state.running = False

        if mode == "Jugador vs IA":
            st.session_state.result = "LOSE"
            guardar("LOSE")
        else:
            st.session_state.result = "RIGHT_WIN"
            guardar("LOSE")

    st.rerun()


# =====================================================
# 📄 EXPLICACIÓN
# =====================================================

st.divider()
st.header("📄 Explicación del juego")

st.write("""
Este proyecto implementa un juego de Pong con distintos modos de comportamiento para comparar inteligencia artificial y sistemas automáticos.

### 🧠 Modos disponibles
- Jugador vs IA
- IA vs Automático

### 🎯 Objetivo
Llegar a 5 puntos antes que el rival.

### 🤖 IA
Basada en reglas simples siguiendo la posición de la bola.

### 📊 Propósito
Comparar comportamientos simples vs IA.
""")
