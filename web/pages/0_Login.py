import streamlit as st
from utils.supabase_client import supabase
from utils.session import init_session, set_user, load_user_from_supabase

init_session()
load_user_from_supabase()

st.title("🔐 Login (opcional)")

# ---------------- INPUTS ----------------
email = st.text_input("Email").strip()
password = st.text_input("Contraseña", type="password").strip()
display_name = st.text_input("Nombre de usuario").strip()

# ---------------- LOGIN ----------------
if st.button("Login"):

    if not email or not password:
        st.warning("⚠️ Completa email y contraseña")
    else:
        try:
            res = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if res and getattr(res, "user", None):
                set_user(res.user)
                st.success("Login correcto ✅")

        except Exception as e:
            st.error(f"Error: {e}")

# ---------------- REGISTRO ----------------
if st.button("Registrarse"):

    if not email or not password or not display_name:
        st.warning("⚠️ Completa todos los campos")
    else:
        try:
            supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "display_name": display_name
                    }
                }
            })

            st.success("Usuario creado ✅")

        except Exception as e:
            st.error(f"Error: {e}")

# ---------------- ESTADO ----------------
user = st.session_state.get("user")

if user:
    meta = getattr(user, "user_metadata", {}) or {}
    name = meta.get("display_name", user.email)
    st.success(f"Conectado como: {name}")
else:
    st.info("Modo invitado 👤")