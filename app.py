import streamlit as st
import requests

# --- APP CONFIG ---
st.set_page_config(page_title="Minaris Triage AI Assistant", layout="wide")

BACKEND_URL = "http://127.0.0.1:8001/analyze"  # ✅ Local FastAPI backend endpoint

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(
        """
        <div style='text-align:center; margin-bottom:20px;'>
            <img src='static/logo.png' style='width:180px; max-width:80%; transition: all 0.3s ease-in-out;'>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<h4 style='text-align:center; color:white;'>TRIAGE AI ASSISTANT</h4>", unsafe_allow_html=True)

    if st.button("➕ New Conversation", use_container_width=True):
        st.session_state.chat_history = []

    st.markdown("---")
    if "chat_history" in st.session_state and st.session_state.chat_history:
        st.markdown("<b>Previous Questions:</b>", unsafe_allow_html=True)
        for i, chat in enumerate(st.session_state.chat_history):
            st.markdown(f"• Q{i+1}: {chat['question']}")
    st.markdown("<br><br><small style='color:lightgray;'>User Active</small>", unsafe_allow_html=True)

# Sidebar styling
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        background-color: #001F3F;
        color: white;
        font-family: "Helvetica Neue", sans-serif;
    }
    .stButton > button {
        background-color: #00AEEF;
        color: white;
        border-radius: 6px;
        font-weight: 600;
        transition: 0.2s;
    }
    .stButton > button:hover {
        background-color: #007bb8;
        color: #fff;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- MAIN CHAT AREA ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.markdown("<h3 style='color:#004C97;'>Triage AI Assistant</h3>", unsafe_allow_html=True)

query = st.text_area("Type your message here...")

if st.button("Send"):
    if not query.strip():
        st.warning("Please enter a question first.")
    else:
        try:
            with st.spinner("Analyzing with GPT-5 Extended Reasoning..."):
                response = requests.post(BACKEND_URL, json={"message": query}, timeout=180)
                if response.status_code == 200:
                    answer = response.json().get("reply", "⚠️ No response from backend.")
                else:
                    answer = f"⚠️ Error: {response.status_code}"
        except Exception as e:
            answer = f"❌ Connection error: {e}"

        st.session_state.chat_history.append({"question": query, "answer": answer})

# --- DISPLAY AREA ---
if not st.session_state.chat_history:
    st.markdown(
        """
        <div class='fade-in' style='text-align:center; margin-top:100px;'>
            <img src='static/logo.png' width='90'><br><br>
            <h2 style='color:#0A1628;'>Enabling Innovation.</h2>
            <h2 style='color:#0A1628;'>Delivering Intelligence.</h2>
            <h2 style='color:#00AEEF;'>Empowering Solutions.</h2>
            <p style='color:gray;'>Your advanced AI partner for intelligent conversations and comprehensive solutions.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    for i, chat in enumerate(st.session_state.chat_history):
        st.markdown(f"**🧑‍💻 User Question {i+1}:** {chat['question']}")
        st.markdown(f"**🤖 AI Answer:** {chat['answer']}")
        st.markdown("---")

# --- FOOTER ---
st.markdown(
    """
    <div class='footer' style='text-align:right; color:#A0A0A0; font-size:12px; margin-top:20px;'>
        designed by <b>MERT TUZ</b>
    </div>
    """,
    unsafe_allow_html=True,
)
