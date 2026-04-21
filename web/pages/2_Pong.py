import streamlit as st
import time
from PIL import Image, ImageDraw

from utils.supabase_client import supabase
from utils.session import get_user

st.set_page_config(page_title="Pong IA", layout="wide")
st.title("🏓 Pong IA vs Humano")

user = get_user()

WIN_SCORE = 5

# ---------------- SPEED ----------------
speed = st.slider("Velocidad del juego", 0.01, 0.1, 0.03)

# ---------------- STATE ----------------
if "ball" not in st.session_state:
    st.session_state.ball = [200, 100]
    st.session_state.vx = 3
    st.session_state.vy = 2

if "player_y" not in st.session_state:
    st.session_state.player_y = 80

if "ai_y" not in st.session_state:
    st.session_state.ai_y = 80

if "score_p" not in st.session_state:
    st.session_state.score_p = 0

if "score_ai" not in st.session_state:
    st.session_state.score_ai = 0

if "game_over" not in st.session_state:
    st.session_state.game_over = False

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

    st.rerun()

# ---------------- CONTROLES ----------------
col1, col2 = st.columns(2)

with col1:
    if st.button("⬆️"):
        st.session_state.player_y -= 10

with col2:
    if st.button("⬇️"):
        st.session_state.player_y += 10

st.session_state.player_y = max(0, min(150, st.session_state.player_y))

# ---------------- GAME OVER ----------------
if st.session_state.game_over:
    st.warning("La partida ha terminado. Pulsa Reset para jugar otra vez.")
    st.stop()

# ---------------- FÍSICA ----------------
ball = st.session_state.ball
vx = st.session_state.vx
vy = st.session_state.vy

ball[0] += vx
ball[1] += vy

# rebote arriba/abajo
if ball[1] <= 0 or ball[1] >= 190:
    vy *= -1

# ---------------- IA SIMPLE ----------------
if ball[1] > st.session_state.ai_y:
    st.session_state.ai_y += 3
else:
    st.session_state.ai_y -= 3

st.session_state.ai_y = max(0, min(150, st.session_state.ai_y))

# ---------------- COLISIONES ----------------
# jugador
if ball[0] <= 20:
    if abs(ball[1] - st.session_state.player_y) < 50:
        vx *= -1

# IA
if ball[0] >= 380:
    if abs(ball[1] - st.session_state.ai_y) < 50:
        vx *= -1

# ---------------- PUNTOS ----------------
if ball[0] < 0:
    st.session_state.score_ai += 1
    ball = [200, 100]

if ball[0] > 400:
    st.session_state.score_p += 1
    ball = [200, 100]

st.session_state.ball = ball
st.session_state.vx = vx
st.session_state.vy = vy

# ---------------- FIN DE PARTIDA ----------------
if st.session_state.score_p >= WIN_SCORE:

    st.success("🏆 ¡Has ganado!")

    if user:
        supabase.table("pong_stats").insert({
            "user_id": user.id,
            "display_name": user.user_metadata.get("display_name"),
            "mode": "HUMAN",
            "result": "WIN",
            "score_player": st.session_state.score_p,
            "score_ai": st.session_state.score_ai
        }).execute()

    st.session_state.game_over = True
    st.stop()


if st.session_state.score_ai >= WIN_SCORE:

    st.error("💀 Ha ganado la IA")

    if user:
        supabase.table("pong_stats").insert({
            "user_id": user.id,
            "display_name": user.user_metadata.get("display_name"),
            "mode": "HUMAN",
            "result": "LOSE",
            "score_player": st.session_state.score_p,
            "score_ai": st.session_state.score_ai
        }).execute()

    st.session_state.game_over = True
    st.stop()

# ---------------- RENDER ----------------
def draw():
    img = Image.new("RGB", (400, 200), (0, 0, 0))
    d = ImageDraw.Draw(img)

    x, y = st.session_state.ball

    # pelota
    d.ellipse([x, y, x+10, y+10], fill=(255, 255, 255))

    # jugador
    d.rectangle([
        10, st.session_state.player_y,
        20, st.session_state.player_y + 50
    ], fill=(0, 255, 0))

    # IA
    d.rectangle([
        380, st.session_state.ai_y,
        390, st.session_state.ai_y + 50
    ], fill=(255, 0, 0))

    return img

st.write(f"Jugador: {st.session_state.score_p} | IA: {st.session_state.score_ai}")

st.image(draw())

time.sleep(speed)
st.rerun()