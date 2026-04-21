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
Este proyecto demuestra el uso de Inteligencia Artificial en videojuegos mediante distintos enfoques:

- 🐍 Snake → Aprendizaje por refuerzo (SARSA y Q-Learning)
- ♟️ Ajedrez → Algoritmo Minimax

El objetivo es comparar diferentes técnicas de IA y observar cómo aprenden o toman decisiones.
""")

# 🤖 IA usada
st.header("🤖 Tipos de IA utilizados")

st.write("""
- **SARSA**: aprende en función de la acción que realmente ejecuta.
- **Q-Learning**: aprende la mejor acción posible en cada estado.
- **Minimax**: evalúa posibles jugadas futuras para tomar la mejor decisión.
""")

# 🎮 cómo usar
st.header("🎮 ¿Cómo usar la aplicación?")

st.write("""
1. Puedes jugar o entrenar IA sin iniciar sesión.
2. Si inicias sesión, se guardarán tus estadísticas.
3. Explora:
   - 🐍 Snake → entrenar y ver IA
   - ♟️ Ajedrez → jugar contra IA
   - 📊 Estadísticas → ver resultados
""")

st.divider()

# 🚀 navegación sugerida
st.subheader("👉 Empieza por:")
st.write("""
- Entrenar la IA de Snake
- Jugar una partida de ajedrez
- Revisar estadísticas (si has iniciado sesión)
""")