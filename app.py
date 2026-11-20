import streamlit as st
from ml_engine import load_ml_bundle
from storage_helper import HISTORY_FILE, USERS_FILE, load_list
from ui_pages import (
    NEWSCHECKR_CSS,
    render_account_page,
    render_check_page,
    render_history_page,
    render_home_page,
)

st.set_page_config(page_title="NewsCheckr", page_icon="🛡️", layout="wide")
st.markdown(NEWSCHECKR_CSS, unsafe_allow_html=True)

st.session_state.setdefault("page", "Home")
st.session_state.setdefault("user", None)
st.session_state.setdefault("account_msg", "")
st.session_state.setdefault("hl_box", "")
st.session_state.setdefault("body_box", "")
st.session_state.setdefault("src_box", "")
st.session_state.setdefault("plat_selected", "WhatsApp")
st.session_state.setdefault("last_result", None)
st.session_state.setdefault("users", load_list(USERS_FILE))
st.session_state.setdefault("history", load_list(HISTORY_FILE))

c0, c1, c2, c3, c4 = st.columns([4.3, 1.0, 1.35, 1.1, 1.55])
with c0:
    st.markdown('<div class="brand-mark"><span>News</span><span>Checkr</span></div>', unsafe_allow_html=True)
with c1:
    if st.button("Home", key="top_home", use_container_width=True):
        st.session_state.page = "Home"
        st.rerun()
with c2:
    if st.button("Check News", key="top_check", use_container_width=True):
        st.session_state.page = "Check News"
        st.rerun()
with c3:
    if st.button("History", key="top_history", use_container_width=True):
        st.session_state.page = "History"
        st.rerun()
with c4:
    top_acc_label = st.session_state.user["name"] if st.session_state.user else "Sign in"
    if st.button(top_acc_label, key="top_account", use_container_width=True):
        st.session_state.page = "Account"
        st.rerun()

st.write("")

try:
    model, vectorizer = load_ml_bundle()
    model_ready = True
except Exception as err:
    model, vectorizer = None, None
    model_ready = False
    st.error(f"Could not load model files: {err}")

if st.session_state.page == "Home":
    render_home_page()
elif st.session_state.page == "Check News":
    render_check_page(model, vectorizer, model_ready)
elif st.session_state.page == "History":
    render_history_page()
elif st.session_state.page == "Account":
    render_account_page()