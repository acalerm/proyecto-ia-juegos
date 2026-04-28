import streamlit as st
import random
from supabase import create_client
from streamlit.components.v1 import html

# =====================================================
# 🔗 SUPABASE
# =====================================================

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_user():
    return st.session_state.get("user", None)


# =====================================================
# 🎮 LÓGICA DEL JUEGO
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
# 🤖 IA MEJORADA (ESTRATEGIA)
# =====================================================

def ia_smart(hand, dealer_card):
    score = sum_hand(hand)

    if score >= 17:
        return "STAND"

    if score <= 11:
        return "HIT"

    if 12 <= score <= 16:
        if dealer_card >= 7:
            return "HIT"
        else:
            return "STAND"


# =====================================================
# 🎨 UI CASINO
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
        width:55px;
        height:80px;
        border-radius:10px;
        background:white;
        display:flex;
        justify-content:center;
        align-items:center;
        font-size:18px;
        font-weight:bold;
        border:2px solid black;
        margin:4px;
        box-shadow:2px 2px 5px rgba(0,0,0,0.2);
    ">
        {value}{suit}
    </div>
    """

def render_hand(hand):
    html_code = "<div style='display:flex; justify-content:center;'>"
    for c in hand:
        html_code += card_ui(c)
    html_code += "</div>"
    return html_code

def render_dealer(hand, reveal=False):
    if not reveal:
        return render_hand([hand[0]]) + "<div style='text-align:center;'>🂠 carta oculta</div>"
    return render_hand(hand)


# =====================================================
# 💾 GUARDAR PARTIDA
# =====================================================

def save_game(user, result, player_score, dealer_score, mode):
    if not user:
        return

    supabase.table("blackjack_stats").insert({
        "user_id": user.id,
        "username": user.email,
        "result": result,
        "player_score": player_score,
        "dealer_score": dealer_score,
        "mode": mode
    }).execute()


# =====================================================
# 📦 ESTADO
# =====================================================

if "player" not in st.session_state:
    st.session_state.player = draw_hand()
    st.session_state.dealer = draw_hand()
    st.session_state.done = False
    st.session_state.result = None
    st.session_state.mode = "Jugador"
    st.session_state.saved = False

# 📊 IA stats sesión
if "ia_stats" not in st.session_state:
    st.session_state.ia_stats = {
        "games": 0,
        "wins": 0,
        "losses": 0
    }


# =====================================================
# 🎰 UI
# =====================================================

st.set_page_config(page_title="Blackjack IA PRO", layout="centered")

st.title("🃏 Blackjack IA PRO")

mode = st.selectbox("Modo", ["Jugador", "IA", "Recomendación"])
st.session_state.mode = mode

user = get_user()

if not user:
    st.info("🔒 Inicia sesión para guardar estadísticas")

st.markdown("---")


# =====================================================
# 🤖 MODO IA AUTOMÁTICO
# =====================================================

if mode == "IA" and not st.session_state.done:

    st.info("🤖 IA jugando (estrategia básica)...")

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

    # 📊 stats IA
    st.session_state.ia_stats["games"] += 1
    if "Ganas" in result:
        st.session_state.ia_stats["wins"] += 1
    elif "Pierdes" in result:
        st.session_state.ia_stats["losses"] += 1


# =====================================================
# 🧑 JUGADOR
# =====================================================

st.markdown("## 🧑 Jugador")
html(render_hand(st.session_state.player), height=120)
st.write("🎯 Puntuación:", sum_hand(st.session_state.player))


# =====================================================
# 🏦 DEALER
# =====================================================

st.markdown("## 🏦 Dealer")

if st.session_state.done:
    html(render_dealer(st.session_state.dealer, reveal=True), height=120)
else:
    html(render_dealer(st.session_state.dealer, reveal=False), height=120)


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

with col3:
    if st.button("🔄 Nueva partida"):
        st.session_state.player = draw_hand()
        st.session_state.dealer = draw_hand()
        st.session_state.done = False
        st.session_state.result = None
        st.session_state.saved = False


# =====================================================
# 🧾 RESULTADO + GUARDADO
# =====================================================

if st.session_state.done:
    st.markdown("## 🧾 Resultado")

    if "Ganas" in str(st.session_state.result):
        st.success(st.session_state.result)
    elif "Pierdes" in str(st.session_state.result):
        st.error(st.session_state.result)
    else:
        st.info(st.session_state.result)

    if not st.session_state.saved:
        save_game(
            user=user,
            result=st.session_state.result,
            player_score=sum_hand(st.session_state.player),
            dealer_score=sum_hand(st.session_state.dealer),
            mode=st.session_state.mode
        )
        st.session_state.saved = True


# =====================================================
# 📊 STATS IA EN PANTALLA
# =====================================================

if mode == "IA":
    stats = st.session_state.ia_stats

    st.markdown("### 📊 Rendimiento IA (sesión)")

    if stats["games"] > 0:
        winrate = (stats["wins"] / stats["games"]) * 100
    else:
        winrate = 0

    st.write(f"Partidas: {stats['games']}")
    st.write(f"Victorias: {stats['wins']}")
    st.write(f"Derrotas: {stats['losses']}")
    st.write(f"Winrate: {winrate:.2f}%")