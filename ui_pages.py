import streamlit as st
from ml_engine import evaluate_news_claim
from storage_helper import add_history_entry, authenticate_user, create_account

NEWSCHECKR_CSS = """
<style>
    .stApp {
        background-color: #FFFFFF;
        background-image:
            linear-gradient(rgba(249,115,22,0.08) 1px, transparent 1px),
            linear-gradient(90deg, rgba(249,115,22,0.08) 1px, transparent 1px);
        background-size: 38px 38px;
        color: #1F1A17;
    }

    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] label {
        color: #1F1A17 !important;
        opacity: 1 !important;
    }

    button[data-baseweb="tab"], button[data-baseweb="tab"] p {
        color: #4B5563 !important;
        font-weight: 600 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"],
    button[data-baseweb="tab"][aria-selected="true"] p {
        color: #EA580C !important;
        font-weight: 700 !important;
    }

    div[data-testid="stAlert"] p, div[data-testid="stAlert"] div {
        color: #1F1A17 !important;
    }

    .stTextInput input, .stTextArea textarea {
        background-color: #FFFFFF !important;
        color: #1F1A17 !important;
        border: 1.5px solid rgba(249,115,22,0.4) !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
    }
    .stTextInput input::placeholder, .stTextArea textarea::placeholder {
        color: #6B7280 !important;
        opacity: 1 !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #16A34A !important;
        box-shadow: 0 0 0 3px rgba(22,163,74,0.15) !important;
    }

    /* Circular/pill buttons by default */
    div.stButton > button {
        background: linear-gradient(135deg, #FFF7ED 0%, #FFEDD5 100%);
        color: #9A3412;
        border: 1.5px solid #FDBA74;
        border-radius: 999px;
        font-weight: 700;
        padding: 0.48rem 1.2rem;
        white-space: nowrap;
        transition: all 0.15s ease;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #FFEDD5 0%, #FED7AA 100%);
        border-color: #EA580C;
        color: #7C2D12;
    }

    /* Rectangular green buttons for Check News & Clear */
    .st-key-check_news_action button,
    .st-key-clear_news_action button {
        background: linear-gradient(135deg, #16A34A 0%, #15803D 100%) !important;
        color: #FFFFFF !important;
        border: 1.5px solid #15803D !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        padding: 0.55rem 1.4rem !important;
        white-space: nowrap !important;
        box-shadow: 0 4px 12px rgba(22, 163, 74, 0.22) !important;
    }
    .st-key-check_news_action button:hover,
    .st-key-clear_news_action button:hover {
        background: linear-gradient(135deg, #15803D 0%, #166534 100%) !important;
        border-color: #166534 !important;
        color: #FFFFFF !important;
    }

    .brand-mark {
        font-size: 1.55rem;
        font-weight: 800;
        color: #1F1A17;
        padding-top: 6px;
    }
    .brand-mark span:first-child { color: #1F1A17; }
    .brand-mark span:last-child { color: #F97316; }

    .glass-box {
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid rgba(249, 115, 22, 0.22);
        border-radius: 18px;
        padding: 22px;
        box-shadow: 0 8px 24px rgba(31, 26, 23, 0.05);
        height: 100%;
    }

    .hero-h1 {
        font-size: 2.5rem;
        font-weight: 800;
        line-height: 1.12;
        color: #1F1A17;
        margin-bottom: 10px;
    }
    .hero-h1 span { color: #F97316; }

    .box-title {
        font-weight: 700;
        font-size: 1rem;
        color: #1F1A17;
        margin-top: 12px;
        margin-bottom: 2px;
    }
    .box-desc {
        font-size: 0.86rem;
        color: #6B5F55;
        margin-bottom: 6px;
    }

    .stat-tile {
        background: #FFF3E8;
        border: 1px solid #FDBA74;
        border-radius: 14px;
        padding: 14px;
        text-align: center;
    }
    .stat-num {
        font-size: 1.65rem;
        font-weight: 800;
        color: #EA580C;
    }
    .v-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 999px;
        color: #FFFFFF;
        font-weight: 700;
        font-size: 0.82rem;
    }
    .b-Real { background: #15803D; }
    .b-Fake { background: #DC2626; }
    .b-Misleading { background: #D97706; }
    .b-Unverified { background: #64748B; }
</style>
"""


def render_home_page():
    st.markdown(
        """
        <div class="glass-box" style="padding:28px;">
            <div class="hero-h1">Stop fake news <span>before it spreads</span></div>
            <p style="font-size:1.05rem; color:#6B5F55; max-width:740px; margin-bottom:0;">
                Type or paste any news headline and article text in English to evaluate its verdict,
                confidence score, red flags, and history with NewsCheckr.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    if st.button("Start checking", key="home_start_btn"):
        st.session_state.page = "Check News"
        st.rerun()

    st.write("")
    _, c1, c2, _ = st.columns([0.5, 2.5, 2.5, 0.5], gap="large")
    with c1:
        st.markdown(
            '<div class="glass-box"><div class="box-title" style="margin-top:0;">News Claim Check</div><div class="box-desc" style="margin-bottom:0;">Enter headline, main text, source, and platform to evaluate authenticity.</div></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            '<div class="glass-box"><div class="box-title" style="margin-top:0;">History</div><div class="box-desc" style="margin-bottom:0;">View all previously checked news items, verdicts, and confidence scores.</div></div>',
            unsafe_allow_html=True,
        )


def render_check_page(model, vectorizer, model_ready: bool):
    st.markdown("## Check a news claim")

    st.markdown('<div class="box-title" style="margin-top:4px;">Headline</div>', unsafe_allow_html=True)
    st.markdown('<div class="box-desc">Enter the news headline so NewsCheckr knows the main claim being made.</div>', unsafe_allow_html=True)
    st.text_input(
        "Headline",
        key="hl_box",
        label_visibility="collapsed",
        placeholder="e.g. Government announces free ₹5000 for all citizens",
    )

    st.markdown('<div class="box-title">Main text</div>', unsafe_allow_html=True)
    st.markdown('<div class="box-desc">Paste the article or forwarded message—this is analyzed by the ML model and text checks.</div>', unsafe_allow_html=True)
    st.text_area(
        "Main text",
        key="body_box",
        height=130,
        label_visibility="collapsed",
        placeholder="Paste the full message or article here...",
    )

    st.markdown('<div class="box-title">Claimed source (optional)</div>', unsafe_allow_html=True)
    st.markdown('<div class="box-desc">Enter the claimed publisher or sender—missing sources affect verification reliability.</div>', unsafe_allow_html=True)
    st.text_input(
        "Claimed source",
        key="src_box",
        label_visibility="collapsed",
        placeholder="e.g. Times of India, WhatsApp group, news website",
    )

    st.markdown('<div class="box-title">Where did you see it?</div>', unsafe_allow_html=True)
    st.markdown('<div class="box-desc">Select the platform where you saw this news.</div>', unsafe_allow_html=True)
    platforms = ["WhatsApp", "Facebook", "X / Twitter", "News site", "Other"]
    p_cols = st.columns(len(platforms))
    for i, plat in enumerate(platforms):
        with p_cols[i]:
            if st.button(plat, key=f"plat_btn_{plat}", use_container_width=True):
                st.session_state.plat_selected = plat
                st.rerun()

    st.write("")
    b1, b2, _ = st.columns([1.4, 1.4, 4.2], gap="small")
    with b1:
        run_btn = st.button("Check News", key="check_news_action", use_container_width=True)
    with b2:
        if st.button("Clear", key="clear_news_action", use_container_width=True):
            st.session_state.hl_box = ""
            st.session_state.body_box = ""
            st.session_state.src_box = ""
            st.session_state.last_result = None
            st.rerun()

    if run_btn:
        combined = f"{st.session_state.hl_box}. {st.session_state.body_box}".strip()
        if not combined or combined == ".":
            st.warning("Please enter a headline or main text to check.")
        elif not model_ready:
            st.error("ML model files (`model.joblib` / `vectorizer.joblib`) are missing.")
        else:
            res = evaluate_news_claim(
                st.session_state.hl_box,
                st.session_state.body_box,
                st.session_state.src_box,
                st.session_state.plat_selected,
                model,
                vectorizer,
            )
            st.session_state.last_result = res
            st.session_state.history = add_history_entry(
                st.session_state.history,
                st.session_state.user,
                combined,
                st.session_state.src_box,
                st.session_state.plat_selected,
                res,
            )

    if st.session_state.last_result:
        r = st.session_state.last_result
        st.write("")
        st.markdown(
            f"""
            <div class="glass-box">
                <span class="v-badge b-{r['cls']}">{r['verdict']}</span>
                <strong style="margin-left:8px;">Confidence: {r['confidence']}%</strong>
                <p style="margin-top:10px; color:#1F1A17;">{r['reason']}</p>
                <div class="box-desc" style="margin-bottom:0;">Red flags: {', '.join(r['red_flags']) if r['red_flags'] else 'None detected'}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        st.markdown("**Verify on trusted sources:**")
        link_cols = st.columns(4)
        for idx, (label, url) in enumerate(r["verify_links"]):
            with link_cols[idx % 4]:
                st.link_button(label, url)


def render_history_page():
    st.markdown("## History")

    if st.session_state.user:
        rows = [x for x in st.session_state.history if x.get("user_email") == st.session_state.user["email"]]
    else:
        rows = st.session_state.history

    counts = {k: sum(1 for x in rows if x.get("cls") == k) for k in ["Real", "Misleading", "Unverified", "Fake"]}
    cols = st.columns(4)
    for col, key in zip(cols, ["Real", "Misleading", "Unverified", "Fake"]):
        with col:
            st.markdown(
                f'<div class="stat-tile"><div class="stat-num">{counts[key]}</div><div>{key}</div></div>',
                unsafe_allow_html=True,
            )

    st.write("")
    if rows:
        for item in rows:
            cls = item.get("cls", "Unverified")
            st.markdown(
                f"""
                <div style="padding:12px 0; border-bottom:1px solid #F3E8D8;">
                    <span class="v-badge b-{cls}">{item.get('verdict', cls)}</span>
                    <strong>{item.get('confidence', 0)}%</strong> · <span style="color:#6B5F55; font-size:0.85rem;">{item.get('timestamp', '')}</span>
                    <div style="margin-top:6px;">{item.get('text', '')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("No checked news items in history yet.")


def render_account_page():
    st.markdown("## Account")

    if st.session_state.account_msg:
        st.success(st.session_state.account_msg)

    if st.session_state.user:
        st.markdown(f"**Name:** {st.session_state.user['name']}")
        st.markdown(f"**Email:** {st.session_state.user['email']}")
        st.write("")
        if st.button("Log out", key="acc_logout_btn"):
            st.session_state.user = None
            st.session_state.account_msg = ""
            st.rerun()
    else:
        t_login, t_create = st.tabs(["Log in", "Create account"])

        with t_login:
            st.markdown('<div class="box-title">Email</div>', unsafe_allow_html=True)
            st.markdown('<div class="box-desc">Enter your registered email address.</div>', unsafe_allow_html=True)
            l_email = st.text_input("Login Email", key="acc_l_email", label_visibility="collapsed", placeholder="you@example.com")

            st.markdown('<div class="box-title">Password</div>', unsafe_allow_html=True)
            st.markdown('<div class="box-desc">Enter your account password to sign in.</div>', unsafe_allow_html=True)
            l_pass = st.text_input("Login Password", type="password", key="acc_l_pass", label_visibility="collapsed", placeholder="Enter password")

            st.write("")
            if st.button("Log in", key="acc_l_submit"):
                found = authenticate_user(st.session_state.users, l_email, l_pass)
                if found:
                    st.session_state.user = found
                    st.session_state.account_msg = "Logged in successfully."
                    st.rerun()
                else:
                    st.error("Invalid email or password.")

        with t_create:
            st.markdown('<div class="box-title">Full name</div>', unsafe_allow_html=True)
            st.markdown('<div class="box-desc">Enter your full name to create your NewsCheckr account.</div>', unsafe_allow_html=True)
            c_name = st.text_input("Full name", key="acc_c_name", label_visibility="collapsed", placeholder="Your name")

            st.markdown('<div class="box-title">Email</div>', unsafe_allow_html=True)
            st.markdown('<div class="box-desc">Enter an email address for your new account.</div>', unsafe_allow_html=True)
            c_email = st.text_input("Email", key="acc_c_email", label_visibility="collapsed", placeholder="you@example.com")

            st.markdown('<div class="box-title">Password</div>', unsafe_allow_html=True)
            st.markdown('<div class="box-desc">Choose a password with at least 4 characters.</div>', unsafe_allow_html=True)
            c_pass = st.text_input("Password", type="password", key="acc_c_pass", label_visibility="collapsed", placeholder="At least 4 characters")

            st.write("")
            if st.button("Create account", key="acc_c_submit"):
                ok, msg, created_user = create_account(st.session_state.users, c_name, c_email, c_pass)
                if ok and created_user:
                    st.session_state.user = created_user
                    st.session_state.account_msg = msg
                    st.rerun()
                else:
                    st.warning(msg)