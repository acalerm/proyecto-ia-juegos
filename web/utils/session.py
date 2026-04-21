import streamlit as st
from utils.supabase_client import supabase


def init_session():
    if "user" not in st.session_state:
        st.session_state["user"] = None


def set_user(user):
    st.session_state["user"] = user


def get_user():
    return st.session_state.get("user")


def logout():
    st.session_state["user"] = None
    try:
        supabase.auth.sign_out()
    except:
        pass


# 🔥 LOGIN PERSISTENTE REAL
def load_user_from_supabase():
    try:
        user = supabase.auth.get_user()

        if user and getattr(user, "user", None):
            st.session_state["user"] = user.user
        else:
            st.session_state["user"] = None

    except Exception:
        st.session_state["user"] = None