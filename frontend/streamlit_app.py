# frontend/streamlit_app.py
import streamlit as st
import requests

API_URL = "http://chat_service:8005/chat"

st.set_page_config(
    page_title="Unified Financial Chat",
    layout="wide",
)

mode = st.sidebar.selectbox(
    "Navigation",
    options=["Introduction", "Chat with Financial Assistant"]
)

if mode == "Introduction":
    st.title("💹 Financial Assistant - Introduction")
    st.markdown(
        "Welcome to the Unified Financial Assistant! Use the **Chat** tab to ask questions or request reports.\n"
        "- Navigate to **Chat** to interact in natural language.\n"
        "- Type queries like 'What was AAPL's closing price yesterday?' or 'Generate report' to get a full PDF report.")
    st.markdown(
        "## About the Financial Assistant\n"
        "This application provides two capabilities:\n"
        "1. **RAG-powered Q&A**: Ask questions about recent stock price history, powered by a Retrieval-Augmented-Generation (RAG) agent.\n"
        "2. **Report Generation**: Generate a formatted PDF financial analysis report based on the latest data.\n"
    )
    st.markdown(
        "###Currently supported stock symbols:\n"
        "-AAPL(Apple).\n"
        "-MSFT(Microsoft).")

# --- Chat interface page ---
else:
    st.title("💹 Financial Assistant - Chat")

    if "history" not in st.session_state:
        st.session_state.history = []

    for msg in st.session_state.history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask me anything…"):
        st.session_state.history.append({"role": "user", "content": prompt})
        with st.chat_message("assistant"):
            st.markdown("⏳ Thinking…")

        res = requests.get(API_URL, params={"q": prompt}, timeout=60)
        res.raise_for_status()
        payload = res.json()

        st.empty()

        if payload["type"] == "text":
            raw = payload["data"]
            if isinstance(raw, dict):
                answer = raw.get("output", "")
            else:
                answer = str(raw)

            with st.chat_message("assistant"):
                st.markdown(answer)
            st.session_state.history.append({"role": "assistant", "content": answer})

        else:
            b64 = payload["data"]
            pdf_display = (
                '<iframe src="data:application/pdf;base64,'
                + b64
                + '" width="100%" height="600px"></iframe>'
            )
            with st.chat_message("assistant"):
                st.markdown("Here’s your report:")
                st.markdown(pdf_display, unsafe_allow_html=True)
            st.session_state.history.append({"role": "assistant", "content": "[PDF report displayed]"})
