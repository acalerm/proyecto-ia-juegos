import streamlit as st
import random
from streamlit.components.v1 import html
from utils.supabase_client import supabase
from utils.session import get_user

# =====================================================
# 👤 USER
# =====================================================

user = get_user()

# =====================================================
# 🎮 LÓGICA
# =====================================================

def draw_card():
    deck = [1,2,3,4,5,6,7,8,9,10,10,10,10]
    return random.choice(deck)

def draw_hand():
    return [draw_card(), draw_card()]

def usable_ace(hand):
    return 1 in hand and sum(hand) + 10 <= 21

def sum_hand(hand):
    return sum(hand) + 10 if usable_ace(hand) else sum(hand)

def is_bust(hand):
    return sum_hand(hand) > 21

def dealer_play(hand):
    while sum_hand(hand) < 17:
        hand.append(draw_card())
    return hand

# =====================================================
# 🤖 IA
# =====================================================

def ia_smart(hand, dealer_card):
    score = sum_hand(hand)

    if score >= 17:
        return "STAND"
    if score <= 11:
        return "HIT"
    if 12 <= score <= 16:
        return "HIT" if dealer_card >= 7 else "STAND"

# =====================================================
# 🎨 CARTAS
# =====================================================

def card_ui(card):
    suits = ["♠", "♥", "♦", "♣"]
    suit = random.choice(suits)

    if card == 1:
        value = "A"
    elif card == 10:
        value = random.choice(["10", "J", "Q", "K"])
    else:
        value = str(card)

    return f"""
    <div style="
        width:55px;height:80px;
        border-radius:10px;
        background:white;
        display:flex;
        justify-content:center;
        align-items:center;
        font-size:18px;
        font-weight:bold;
        border:2px solid black;
        margin:4px;
    ">
        {value}{suit}
    </div>
    """

# =====================================================
# 🛡️ FIX RENDER HAND
# =====================================================

def render_hand(hand):
    if not isinstance(hand, list):
        return "<div>Sin cartas</div>"

    if len(hand) == 0:
        return "<div>Sin cartas</div>"

    html_code = "<div style='display:flex;justify-content:center;'>"
    for c in hand:
        html_code += card_ui(c)
    html_code += "</div>"
    return html_code

# =====================================================
# 💾 SUPABASE
# =====================================================

def save_game(user, result, player_score, dealer_score, mode):
    if not user:
        return

    display_name = None

    if hasattr(user, "user_metadata") and user.user_metadata:
        display_name = user.user_metadata.get("display_name")

    if not display_name:
        display_name = getattr(user, "email", "guest")

    supabase.table("blackjack_stats").insert({
        "user_id": user.id,
        "display_name": display_name,
        "result": result,
        "player_score": player_score,
        "dealer_score": dealer_score,
        "mode": mode
    }).execute()

# =====================================================
# 📦 ESTADO
# =====================================================

st.set_page_config(page_title="Blackjack", layout="centered")

if "player" not in st.session_state or not isinstance(st.session_state.player, list):
    st.session_state.player = draw_hand()

if "dealer" not in st.session_state or not isinstance(st.session_state.dealer, list):
    st.session_state.dealer = draw_hand()

if "done" not in st.session_state:
    st.session_state.done = False

if "result" not in st.session_state:
    st.session_state.result = None

if "saved" not in st.session_state:
    st.session_state.saved = False

# =====================================================
# 🎰 UI
# =====================================================

st.title("🃏 Blackjack IA PRO")

mode = st.selectbox("Modo", ["Jugador", "IA"])

# =====================================================
# 🤖 IA MODE
# =====================================================

if mode == "IA" and not st.session_state.done:

    player = draw_hand()
    dealer = draw_hand()
    dealer_card = dealer[0]

    while True:
        action = ia_smart(player, dealer_card)

        if action == "HIT":
            player.append(draw_card())
            if is_bust(player):
                result = "💀 Pierdes"
                break
        else:
            break

    dealer = dealer_play(dealer)

    p = sum_hand(player)
    d = sum_hand(dealer)

    if is_bust(player):
        result = "💀 Pierdes"
    elif is_bust(dealer):
        result = "🎉 Ganas"
    elif p > d:
        result = "🎉 Ganas"
    elif p < d:
        result = "💀 Pierdes"
    else:
        result = "🤝 Empate"

    st.session_state.player = player
    st.session_state.dealer = dealer
    st.session_state.result = result
    st.session_state.done = True

    st.rerun()

# =====================================================
# 🧑 JUGADOR
# =====================================================

st.subheader("🧑 Jugador")
html(render_hand(st.session_state.player), height=120)
st.write("Puntuación:", sum_hand(st.session_state.player))

# =====================================================
# 🏦 DEALER
# =====================================================

st.subheader("🏦 Dealer")

if st.session_state.done:
    html(render_hand(st.session_state.dealer), height=120)
    st.write("Puntuación:", sum_hand(st.session_state.dealer))
else:
    html(render_hand([st.session_state.dealer[0]]), height=120)
    st.write("Carta visible:", st.session_state.dealer[0])

# =====================================================
# 🎮 BOTONES
# =====================================================

game_over = st.session_state.done or mode == "IA"

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🎴 Pedir carta", disabled=game_over):
        st.session_state.player.append(draw_card())

        if is_bust(st.session_state.player):
            st.session_state.done = True
            st.session_state.result = "💀 Pierdes"

        st.rerun()

with col2:
    if st.button("🛑 Plantarse", disabled=game_over):
        st.session_state.done = True
        st.session_state.dealer = dealer_play(st.session_state.dealer)

        p = sum_hand(st.session_state.player)
        d = sum_hand(st.session_state.dealer)

        if is_bust(st.session_state.dealer):
            st.session_state.result = "🎉 Ganas"
        elif p > d:
            st.session_state.result = "🎉 Ganas"
        elif p < d:
            st.session_state.result = "💀 Pierdes"
        else:
            st.session_state.result = "🤝 Empate"

        st.rerun()

with col3:
    if st.button("🔄 Nueva partida"):
        st.session_state.player = draw_hand()
        st.session_state.dealer = draw_hand()
        st.session_state.done = False
        st.session_state.result = None
        st.session_state.saved = False

        st.rerun()

# =====================================================
# 🧾 RESULTADO + SUPABASE
# =====================================================

if st.session_state.done and not st.session_state.saved and user:

    save_game(
        user=user,
        result=st.session_state.result,
        player_score=sum_hand(st.session_state.player),
        dealer_score=sum_hand(st.session_state.dealer),
        mode=mode
    )

    st.session_state.saved = True

# =====================================================
# 📘 EXPLICACIÓN IA (RULE-BASED)
# =====================================================

if st.session_state.done:

    st.markdown("---")
    st.header("🤖 Explicación de la IA")

    st.markdown("""
## 🧠 Rule-Based AI

La IA de este Blackjack funciona con **reglas fijas programadas manualmente**.

---

## ⚙️ Decisión de la IA

La IA decide entre:

- 🎴 HIT (pedir carta)
- 🛑 STAND (plantarse)

según su puntuación y la carta del dealer.

---

## 📜 Reglas

- Si tiene **17 o más → STAND**
- Si tiene **11 o menos → HIT**
- Si está entre **12 y 16**:
  - dealer ≥ 7 → HIT
  - dealer < 7 → STAND

---

## 🎯 Objetivo

Maximizar la probabilidad de ganar evitando pasarse de 21
y reaccionando a la carta del dealer.

---

## 📌 Características

- No aprende
- No entrena
- Es determinista
- Es totalmente explicable

---

## 🔁 Comparación con otros sistemas

| Tipo | Ejemplo |
|------|--------|
| Rule-Based | Blackjack (este juego) |
| Reinforcement Learning | GridWorld |
| Deep Learning | Modelos neuronales |

---
""")
