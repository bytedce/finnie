import streamlit as st
from finnieassistant.crew import Finnieassistant

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(page_title="Finnie Assistant", layout="wide")

# =====================================================
# GLOBAL STYLES
# =====================================================
st.markdown("""
<style>
html, body, .stApp {
    background-color: #FFFFFF;
    color: #111827;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                 Roboto, Helvetica, Arial, sans-serif;
}

.block-container {
    padding-top: 2rem;
}

/* Chat box */
.chat-box {
    border: 1px solid #D1D5DB;
    border-radius: 14px;
    background: #FFFFFF;
    display: flex;
    flex-direction: column;
}

/* Header */
.chat-header {
    padding: 14px 16px;
    font-size: 18px;
    font-weight: 600;
    border-bottom: 1px solid #E5E7EB;
}

/* Messages */
.user-msg {
    background: #EEF2FF;
    padding: 10px 12px;
    border-radius: 10px;
    margin: 6px 0 6px auto;
    max-width: 85%;
}

.assistant-msg {
    background: #F9FAFB;
    border: 1px solid #E5E7EB;
    padding: 10px 12px;
    border-radius: 10px;
    margin: 6px auto 6px 0;
    max-width: 85%;
}

/* Input row */
.chat-input-row {
    border-top: 1px solid #E5E7EB;
    padding: 10px;
}

/* Input */
.stTextInput input {
    background: #FFFFFF !important;
    color: #111827 !important;
    caret-color: #111827 !important;
    border: 1px solid #D1D5DB !important;
    border-radius: 10px !important;
}

/* Send button — forced style */
.send-btn button {
    background-color: #2563EB !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
    height: 42px;
    width: 42px;
    border-radius: 10px;
    font-size: 18px;
}

.send-btn button:hover,
.send-btn button:focus,
.send-btn button:active {
    background-color: #2563EB !important;
    color: #FFFFFF !important;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# SESSION STATE
# =====================================================
st.session_state.setdefault("messages", [])
st.session_state.setdefault("final_output", "")
st.session_state.setdefault("pending", False)

# =====================================================
# LAYOUT (30 / 70)
# =====================================================
left, right = st.columns([3, 7], gap="large")

# =====================================================
# LEFT — CHATBOX (BORDERED)
# =====================================================
with left:
    st.markdown("<div class='chat-box'>", unsafe_allow_html=True)

    st.markdown("<div class='chat-header'>Finnie Assistant</div>", unsafe_allow_html=True)

    chat_area = st.container(height=420)
    with chat_area:
        for msg in st.session_state.messages:
            cls = "user-msg" if msg["role"] == "user" else "assistant-msg"
            st.markdown(
                f"<div class='{cls}'>{msg['content']}</div>",
                unsafe_allow_html=True,
            )

        if st.session_state.pending:
            st.markdown(
                "<div class='assistant-msg'>Thinking…</div>",
                unsafe_allow_html=True,
            )

    with st.form("chat_form", clear_on_submit=True):
        st.markdown("<div class='chat-input-row'>", unsafe_allow_html=True)
        col1, col2 = st.columns([9, 1])
        with col1:
            user_input = st.text_input(
                "",
                placeholder="Tell me about Nvidia stock",
                label_visibility="collapsed",
            )
        with col2:
            send = st.form_submit_button("➤", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# RIGHT — OUTPUT
# =====================================================
with right:
    st.markdown("## Analysis Output")

    if st.session_state.final_output:
        st.markdown(st.session_state.final_output)
    else:
        st.info("Finnie output will appear here.")

# =====================================================
# EXECUTION (OPTIMISTIC UI)
# =====================================================
if send and user_input:
    # 1️⃣ Optimistically show user message immediately
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )
    st.session_state.pending = True

    st.rerun()

# =====================================================
# BACKGROUND EXECUTION (NEXT RUN)
# =====================================================
if st.session_state.pending:
    finnie = Finnieassistant()

    with st.spinner("Thinking..."):
        result = finnie.run_finnie(
            st.session_state.messages[-1]["content"]
        )

    st.session_state.final_output = str(result)
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": "Analysis complete. See the output on the right.",
        }
    )
    st.session_state.pending = False
    st.rerun()
