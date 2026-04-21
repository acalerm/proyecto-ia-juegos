import streamlit as st
from supabase import create_client

try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

except Exception:
    supabase = None
    st.warning("Supabase no configurado correctamente")