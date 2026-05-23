import streamlit as st
import chess
import chess.svg
from streamlit.components.v1 import html
import random

from utils.supabase_client import supabase
from utils.session import get_user

st.set_page_config(page_title="Ajedrez PRO", layout="wide")
st.title("♟️ Ajedrez: Usuario vs IA")

user = get_user()

# --- ESTADO ---
if "board" not in st.session_state:
    st.session_state.board = chess.Board()

if "selected_square" not in st.session_state:
    st.session_state.selected_square = None

# 🔐 control anti-duplicado real
if "last_action" not in st.session_state:
    st.session_state.last_action = None

board = st.session_state.board

# --- DIFICULTAD ---
dificultad = st.selectbox("Dificultad", ["Fácil (Rule Based)", "Difícil (Minimax)"])

# --- IA FÁCIL ---
def movimiento_ia_random(board):
    legal = list(board.legal_moves)
    if legal:
        board.push(random.choice(legal))

# --- IA DIFÍCIL ---
def evaluar_tablero(board):
    valores = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0
    }

    score = 0
    for pieza, valor in valores.items():
        score += len(board.pieces(pieza, chess.WHITE)) * valor
        score -= len(board.pieces(pieza, chess.BLACK)) * valor

    return score


def minimax(board, depth, maximizing):
    if depth == 0 or board.is_game_over():
        return evaluar_tablero(board)

    if maximizing:
        best = -9999
        for move in board.legal_moves:
            board.push(move)
            val = minimax(board, depth - 1, False)
            board.pop()
            best = max(best, val)
        return best
    else:
        best = 9999
        for move in board.legal_moves:
            board.push(move)
            val = minimax(board, depth - 1, True)
            board.pop()
            best = min(best, val)
        return best


def movimiento_ia_minimax(board):
    best_move = None
    best_value = 9999

    for move in board.legal_moves:
        board.push(move)
        value = minimax(board, 2, True)
        board.pop()

        if value < best_value:
            best_value = value
            best_move = move

    if best_move:
        board.push(best_move)

# --- CLICK CASILLA ---
def casilla_click(square):
    board = st.session_state.board

    if board.is_game_over():
        return

    piece = board.piece_at(square)

    if st.session_state.selected_square is None:
        if piece and piece.color == chess.WHITE:
            st.session_state.selected_square = square
    else:
        move = chess.Move(st.session_state.selected_square, square)

        if move in board.legal_moves:
            board.push(move)
            st.session_state.selected_square = None

            if not board.is_game_over():
                if dificultad == "Fácil":
                    movimiento_ia_random(board)
                else:
                    movimiento_ia_minimax(board)
        else:
            st.warning("Movimiento ilegal")
            st.session_state.selected_square = None

# --- TABLERO ---
def mostrar_tablero(board):
    squares = {}

    if st.session_state.selected_square is not None:
        for m in board.legal_moves:
            if m.from_square == st.session_state.selected_square:
                squares[m.to_square] = "X"

    svg = chess.svg.board(board=board, squares=squares, size=500)

    cols = st.columns([1, 2, 1])
    with cols[1]:
        html(svg, height=520)

st.write("### Click en la casilla:")

def square_to_notation(row, col):
    return chr(ord('A') + col) + str(8 - row)

for row in range(8):
    cols = st.columns(8)
    for col in range(8):
        square = (7 - row) * 8 + col
        with cols[col]:
            if st.button(square_to_notation(row, col), key=f"{row}-{col}"):
                casilla_click(square)

mostrar_tablero(board)

# --- RESULTADO ---
if board.is_game_over():
    if board.is_checkmate():
        if board.turn == chess.BLACK:
            st.success("🏆 ¡Has ganado!")
        else:
            st.error("💀 Has perdido")
    elif board.is_stalemate():
        st.info("🤝 Empate")

# --- REINICIAR (FIX DEFINITIVO) ---
if st.button("Reiniciar partida"):

    action_id = "restart_chess"

    # 🔒 evita doble ejecución en reruns
    if st.session_state.last_action == action_id:
        st.stop()

    st.session_state.last_action = action_id

    board = st.session_state.board

    # 💾 guardar SOLO UNA VEZ
    if user and not board.is_game_over():
        supabase.table("chess_stats").insert({
            "user_id": user.id,
            "display_name": user.user_metadata.get("display_name"),
            "moves": board.fullmove_number,
            "pieces_lost": len(board.piece_map()),
            "result": "lose",
            "difficulty": dificultad
        }).execute()

    # 🔄 reset
    st.session_state.board = chess.Board()
    st.session_state.selected_square = None

    # liberar acción
    st.session_state.last_action = None
