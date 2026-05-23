import streamlit as st
import numpy as np
import random
import time
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt

# 🔌 NUEVO (supabase)
from utils.supabase_client import supabase
from utils.session import get_user

st.set_page_config(page_title="GridWorld IA PRO FIX", layout="centered")

st.title("🤖 GridWorld IA PRO (FIX UI + visión 3x3)")

# 👤 NUEVO (usuario)
user = get_user()

# ---------------- FONT ----------------
try:
    FONT = ImageFont.truetype("arial.ttf", 24)
except:
    FONT = ImageFont.load_default()

# ---------------- CONSTANTES ----------------
GRID = 8
CELL = 70

# ---------------- STATE ----------------
if "Q_sarsa" not in st.session_state:
    st.session_state.Q_sarsa = {}

if "Q_ql" not in st.session_state:
    st.session_state.Q_ql = {}

if "results" not in st.session_state:
    st.session_state.results = {}

# =========================================================
# 🧱 MAPAS
# =========================================================
def generate_map(difficulty):

    agent = (0,0)
    goal = (7,7)

    if difficulty == "Fácil":
        walls = [(3,3)]
        traps = []

    elif difficulty == "Media":
        walls = [(2,2),(2,3),(3,2),(4,4)]
        traps = [(5,5)]

    else:
        walls = [
            (1,1),(1,2),(1,3),
            (2,3),(3,3),(4,3),
            (5,1),(5,2),(5,3),
            (6,5),(5,5)
        ]
        traps = [(2,5),(3,5),(4,5),(6,2)]

    return agent, goal, walls, traps

# =========================================================
# 🧠 VISIÓN 3x3
# =========================================================
def get_vision(agent, walls, traps, goal):

    ax, ay = agent
    v = []

    for dy in [-1,0,1]:
        for dx in [-1,0,1]:

            x = ax + dx
            y = ay + dy

            if x < 0 or x >= GRID or y < 0 or y >= GRID:
                v.append(-1)
            elif (x,y) == goal:
                v.append(3)
            elif (x,y) in walls:
                v.append(1)
            elif (x,y) in traps:
                v.append(2)
            else:
                v.append(0)

    return tuple(v)

# =========================================================
# ⚙️ STEP
# =========================================================
def step(agent, action, goal, walls, traps):

    x,y = agent

    if action == 0: y -= 1
    elif action == 1: x += 1
    elif action == 2: y += 1
    elif action == 3: x -= 1

    new = (x,y)

    if x<0 or x>=GRID or y<0 or y>=GRID:
        return agent, -5, False

    if new in walls:
        return agent, -10, False

    if new in traps:
        return new, -20, False

    if new == goal:
        return new, 100, True

    d1 = abs(agent[0]-goal[0]) + abs(agent[1]-goal[1])
    d2 = abs(new[0]-goal[0]) + abs(new[1]-goal[1])

    return new, -1 + (2 if d2 < d1 else -1), False

# =========================================================
# 🧠 RL
# =========================================================
def state(v,gdir):
    return v + gdir

def choose(Q,s):
    if s not in Q:
        Q[s]=[0,0,0,0]

    if random.random()<0.1:
        return random.randint(0,3)

    return int(np.argmax(Q[s]))

def update(Q,s,a,r,ns,na,algo):

    alpha=0.1
    gamma=0.9

    if s not in Q:
        Q[s]=[0,0,0,0]
    if ns not in Q:
        Q[ns]=[0,0,0,0]

    if algo=="SARSA":
        Q[s][a]+=alpha*(r+gamma*Q[ns][na]-Q[s][a])
    else:
        Q[s][a]+=alpha*(r+gamma*np.max(Q[ns])-Q[s][a])

# =========================================================
# 🏋️ TRAIN
# =========================================================
def train(algo,difficulty,episodes):

    Q = st.session_state.Q_sarsa if algo=="SARSA" else st.session_state.Q_ql

    rewards=[]

    for _ in range(episodes):

        a,g,w,t = generate_map(difficulty)

        v = get_vision(a,w,t,g)

        gdir = (np.sign(g[0]-a[0]), np.sign(g[1]-a[1]))

        s = state(v,gdir)
        act = choose(Q,s)

        total=0
        done=False

        for _ in range(80):

            na,r,done = step(a,act,g,w,t)

            v2 = get_vision(na,w,t,g)
            gdir2 = (np.sign(g[0]-na[0]), np.sign(g[1]-na[1]))

            ns = state(v2,gdir2)
            nxt = choose(Q,ns)

            update(Q,s,act,r,ns,nxt,algo)

            a=na
            s=ns
            act=nxt

            total+=r

            if done:
                break

        rewards.append(total)

    return np.mean(rewards)

# =========================================================
# 🎮 DRAW
# =========================================================
def draw(a,g,w,t):

    img = Image.new("RGB",(GRID*CELL,GRID*CELL),(25,25,25))
    d = ImageDraw.Draw(img)

    for x in range(GRID):
        for y in range(GRID):
            d.rectangle([x*CELL,y*CELL,x*CELL+CELL,y*CELL+CELL],outline=(80,80,80))

    for ob in w:
        d.rectangle([ob[0]*CELL,ob[1]*CELL,ob[0]*CELL+CELL,ob[1]*CELL+CELL],fill=(200,50,50))

    for tr in t:
        d.rectangle([tr[0]*CELL,tr[1]*CELL,tr[0]*CELL+CELL,tr[1]*CELL+CELL],fill=(255,140,0))

    d.ellipse([g[0]*CELL+20,g[1]*CELL+20,g[0]*CELL+CELL-20,g[1]*CELL+CELL-20],fill=(0,255,0))

    d.ellipse([a[0]*CELL+20,a[1]*CELL+20,a[0]*CELL+CELL-20,a[1]*CELL+CELL-20],fill=(50,150,255))

    return img

# =========================================================
# UI
# =========================================================
modo = st.selectbox("Modo",[
    "Entrenar",
    "Comparación visual",
    "Explicación"
])

# =========================================================
# 🏋️ ENTRENAMIENTO
# =========================================================
if modo=="Entrenar":

    episodes = st.slider("Episodios",1000,20000,5000,step=1000)

    if st.button("Entrenar IA"):

        results={}

        for d in ["Fácil","Media","Difícil"]:

            st.write(f"Entrenando {d}...")

            s = train("SARSA",d,episodes)
            q = train("Q-Learning",d,episodes)

            results[d]={"SARSA":s,"Q":q}

        st.session_state.results=results

        # 💾 GUARDADO EN SUPABASE
        if user and results:
            for d in results:
                supabase.table("gridworld_stats").insert({
                    "user_id": user.id,
                    "display_name": user.user_metadata.get("display_name"),
                    "algorithm": "SARSA",
                    "difficulty": d,
                    "episodes": episodes,
                    "avg_reward": float(results[d]["SARSA"])
                }).execute()

                supabase.table("gridworld_stats").insert({
                    "user_id": user.id,
                    "display_name": user.user_metadata.get("display_name"),
                    "algorithm": "Q-Learning",
                    "difficulty": d,
                    "episodes": episodes,
                    "avg_reward": float(results[d]["Q"])
                }).execute()

        st.success("Entrenamiento completo")

        # 📊 GRÁFICA AUTOMÁTICA
        labels = list(results.keys())
        sarsa_vals = [results[d]["SARSA"] for d in labels]
        ql_vals = [results[d]["Q"] for d in labels]

        x = np.arange(len(labels))

        fig, ax = plt.subplots()
        ax.bar(x - 0.2, sarsa_vals, 0.4, label="SARSA")
        ax.bar(x + 0.2, ql_vals, 0.4, label="Q-Learning")

        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.set_ylabel("Recompensa media")
        ax.set_title("Comparación por dificultad")
        ax.legend()

        st.pyplot(fig)

# =========================================================
# ⚔️ COMPARACIÓN
# =========================================================
if modo=="Comparación visual":

    difficulty = st.selectbox("Dificultad",["Fácil","Media","Difícil"])

    if st.button("Simular batalla"):

        a1,g1,w1,t1 = generate_map(difficulty)
        a2,g2,w2,t2 = generate_map(difficulty)

        Q1 = st.session_state.Q_sarsa
        Q2 = st.session_state.Q_ql

        col1,col2 = st.columns(2)

        p1 = col1.empty()
        p2 = col2.empty()

        done1=False
        done2=False

        for _ in range(80):

            if not done1:
                v=get_vision(a1,w1,t1,g1)
                gdir=(np.sign(g1[0]-a1[0]),np.sign(g1[1]-a1[1]))
                s=state(v,gdir)
                act=choose(Q1,s)
                a1,_,done1=step(a1,act,g1,w1,t1)

            if not done2:
                v=get_vision(a2,w2,t2,g2)
                gdir=(np.sign(g2[0]-a2[0]),np.sign(g2[1]-a2[1]))
                s=state(v,gdir)
                act=choose(Q2,s)
                a2,_,done2=step(a2,act,g2,w2,t2)

            p1.image(draw(a1,g1,w1,t1))
            p2.image(draw(a2,g2,w2,t2))

            time.sleep(0.5)

# =========================================================
# 📄 EXPLICACIÓN
# =========================================================
if modo=="Explicación":

    if st.session_state.results:

        st.markdown("## 📄 Conclusión")

        st.write("""
SARSA es más conservador y evita trampas.
Q-Learning es más agresivo y optimiza rutas.

La visión 3x3 permite percepción local del entorno, haciendo que el laberinto influya realmente en las decisiones.
""")
