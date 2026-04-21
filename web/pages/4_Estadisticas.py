import streamlit as st
from utils.supabase_client import supabase

st.set_page_config(page_title="Estadísticas", layout="wide")
st.title("📊 Estadísticas del sistema")

# ---------------- SNAKE ----------------
st.header("🐍 Snake Stats")

snake_data = supabase.table("snake_stats").select("*").execute().data

if snake_data:

    total_snake = len(snake_data)

    # ⚠️ sin tocar lógica, solo protección básica
    valid_max = [
        r["max_score"] for r in snake_data
        if r.get("max_score") is not None
    ]

    max_score = max(valid_max) if valid_max else 0

    avg_score = sum([
        r["last_score"] for r in snake_data
        if r.get("last_score") is not None
    ]) / total_snake if total_snake > 0 else 0

    st.write(f"Partidas: {total_snake}")
    st.write(f"Max score: {max_score}")
    st.write(f"Media last score: {avg_score:.2f}")

else:
    st.warning("No hay datos de Snake")

# ---------------- CHESS ----------------
st.header("♟ Chess Stats")

chess_data = supabase.table("chess_stats").select("*").execute().data

if chess_data:

    total_chess = len(chess_data)

    wins = len([r for r in chess_data if r["result"] == "WIN"])
    losses = len([r for r in chess_data if r["result"] == "LOSE"])

    winrate = (wins / total_chess) * 100 if total_chess > 0 else 0

    st.write(f"Partidas: {total_chess}")
    st.write(f"Victorias: {wins}")
    st.write(f"Derrotas: {losses}")
    st.write(f"Winrate: {winrate:.2f}%")

else:
    st.warning("No hay datos de Chess")

# ---------------- PONG ----------------
st.header("🏓 Pong Stats")

pong_data = supabase.table("pong_stats").select("*").execute().data

if pong_data:

    total_pong = len(pong_data)

    wins = len([r for r in pong_data if r.get("result") == "WIN"])
    losses = len([r for r in pong_data if r.get("result") == "LOSE"])

    winrate = (wins / total_pong) * 100 if total_pong > 0 else 0

    player_scores = [
        r.get("score_player", 0)
        for r in pong_data
        if r.get("score_player") is not None
    ]

    ai_scores = [
        r.get("score_ai", 0)
        for r in pong_data
        if r.get("score_ai") is not None
    ]

    avg_player = sum(player_scores) / len(player_scores) if player_scores else 0
    avg_ai = sum(ai_scores) / len(ai_scores) if ai_scores else 0

    st.write(f"Partidas: {total_pong}")
    st.write(f"Victorias: {wins}")
    st.write(f"Derrotas: {losses}")
    st.write(f"Winrate: {winrate:.2f}%")
    st.write(f"Media jugador: {avg_player:.2f}")
    st.write(f"Media IA: {avg_ai:.2f}")

else:
    st.info("No hay datos de Pong todavía")

# ---------------- DATOS BRUTOS ----------------
st.header("📦 Datos en bruto")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Snake")
    if snake_data:
        st.dataframe(snake_data)

with col2:
    st.subheader("Chess")
    if chess_data:
        st.dataframe(chess_data)

with col3:
    st.subheader("Pong")
    if pong_data:
        st.dataframe(pong_data)