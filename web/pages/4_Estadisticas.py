import streamlit as st
import pandas as pd
from utils.supabase_client import supabase
from utils.session import get_user

st.set_page_config(page_title="Estadísticas", layout="wide")
st.title("📊 Estadísticas del sistema")

user = get_user()

# ⚠️ si no hay usuario, no mostramos stats
if not user:
    st.warning("Inicia sesión para ver tus estadísticas 👤")
    st.stop()

# =====================================================
# 🐍 SNAKE
# =====================================================

st.header("🐍 Snake Stats")

snake_data = supabase.table("snake_stats") \
    .select("*") \
    .eq("user_id", user.id) \
    .execute().data

if snake_data:

    total_snake = len(snake_data)

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


# =====================================================
# ♟ CHESS
# =====================================================

st.header("♟ Chess Stats")

chess_data = supabase.table("chess_stats") \
    .select("*") \
    .eq("user_id", user.id) \
    .execute().data

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


# =====================================================
# 🏓 PONG
# =====================================================

st.header("🏓 Pong Stats")

pong_data = supabase.table("pong_stats") \
    .select("*") \
    .eq("user_id", user.id) \
    .execute().data

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


# =====================================================
# 🃏 BLACKJACK (UPDATED)
# =====================================================

st.header("🃏 Blackjack Stats")

blackjack_data = supabase.table("blackjack_stats") \
    .select("*") \
    .eq("user_id", user.id) \
    .execute().data

if blackjack_data:

    total_bj = len(blackjack_data)

    wins = len([r for r in blackjack_data if "Ganas" in str(r.get("result"))])
    losses = len([r for r in blackjack_data if "Pierdes" in str(r.get("result"))])
    draws = len([r for r in blackjack_data if "Empate" in str(r.get("result"))])

    winrate = (wins / total_bj) * 100 if total_bj > 0 else 0

    player_scores = [
        r.get("player_score", 0)
        for r in blackjack_data
        if r.get("player_score") is not None
    ]

    dealer_scores = [
        r.get("dealer_score", 0)
        for r in blackjack_data
        if r.get("dealer_score") is not None
    ]

    avg_player = sum(player_scores) / len(player_scores) if player_scores else 0
    avg_dealer = sum(dealer_scores) / len(dealer_scores) if dealer_scores else 0

    st.write(f"Partidas: {total_bj}")
    st.write(f"Victorias: {wins}")
    st.write(f"Derrotas: {losses}")
    st.write(f"Empates: {draws}")
    st.write(f"Winrate: {winrate:.2f}%")
    st.write(f"Media jugador: {avg_player:.2f}")
    st.write(f"Media dealer: {avg_dealer:.2f}")

else:
    st.warning("No hay datos de Blackjack")


# =====================================================
# 📦 DATOS EN BRUTO
# =====================================================

st.header("📦 Tus datos")

col1, col2, col3, col4 = st.columns(4)

def clean_df(data):
    df = pd.DataFrame(data)
    return df.drop(columns=["id", "user_id"], errors="ignore")

with col1:
    st.subheader("Snake")
    if snake_data:
        st.dataframe(clean_df(snake_data))

with col2:
    st.subheader("Chess")
    if chess_data:
        st.dataframe(clean_df(chess_data))

with col3:
    st.subheader("Pong")
    if pong_data:
        st.dataframe(clean_df(pong_data))

with col4:
    st.subheader("Blackjack")
    if blackjack_data:
        st.dataframe(clean_df(blackjack_data))
