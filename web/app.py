import streamlit as st
from utils.session import init_session, get_user

st.set_page_config(page_title="Proyecto IA Juegos", layout="wide")

# 🔐 sesión persistente
init_session()
user = get_user()

st.title("🎮 Proyecto IA jugando videojuegos")

# 👤 estado usuario (VERSIÓN SEGURA)
if user:
    name = (user.user_metadata or {}).get('display_name', 'Usuario')
    st.success(f"Sesión iniciada como {name} 👤")
else:
    st.info("Estás usando la app como invitado 👤")

st.divider()

# 📖 explicación
st.header("📚 ¿En qué consiste este proyecto?")

st.write("""
Este proyecto demuestra diferentes aplicaciones de Inteligencia Artificial en videojuegos utilizando múltiples enfoques y algoritmos de decisión.

Los juegos implementados actualmente son:

- 🐍 Snake → Aprendizaje por refuerzo mediante SARSA
- 🏓 Pong → Aprendizaje por refuerzo mediante Q-Learning
- 🟦 GridWorld → Comparación entre SARSA y Q-Learning
- ♟️ Ajedrez → Algoritmo Minimax
- 🃏 Blackjack → IA basada en reglas (Rule-Based AI)

El objetivo principal es comparar distintos tipos de inteligencia artificial, analizando cómo aprenden, toman decisiones y se comportan en diferentes entornos de juego.
""")

# 🤖 IA usada
st.header("🤖 Tipos de IA utilizados")

st.write("""
- **SARSA**: algoritmo de aprendizaje por refuerzo que aprende en función de las acciones realmente ejecutadas.
- **Q-Learning**: algoritmo de aprendizaje por refuerzo que aprende la mejor acción posible para cada estado.
- **Minimax**: algoritmo de búsqueda utilizado en juegos de estrategia para evaluar posibles movimientos futuros.
- **Rule-Based AI**: inteligencia artificial basada en reglas predefinidas y decisiones heurísticas.
""")

# 🧪 funcionalidades
st.header("🧪 Funcionalidades del proyecto")

st.write("""
La aplicación permite explorar distintos sistemas de inteligencia artificial aplicados a videojuegos interactivos.

Entre las funcionalidades disponibles se incluyen:

- 🎮 Jugar manualmente contra distintas IA
- 🤖 Observar el comportamiento de algoritmos de aprendizaje
- 📊 Consultar estadísticas de partidas
- 👤 Sistema de autenticación y perfiles de usuario
- ☁️ Almacenamiento de datos mediante Supabase
- 🌐 Interfaz web desarrollada con Streamlit

Cada juego implementa un enfoque de IA diferente para mostrar cómo varían las estrategias y métodos de decisión según el entorno.
""")

st.divider()

# 🎯 objetivos
st.subheader("🎯 Objetivos del proyecto")

st.write("""
Los principales objetivos de este proyecto son:

- Comprender diferentes técnicas de Inteligencia Artificial
- Aplicar algoritmos de aprendizaje y toma de decisiones en videojuegos
- Comparar distintos modelos de IA en entornos interactivos
- Desarrollar una aplicación web funcional utilizando Python y Streamlit
- Integrar almacenamiento y gestión de datos mediante Supabase
- Crear una plataforma visual e interactiva orientada al aprendizaje y experimentación
""")
