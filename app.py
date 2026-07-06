import time
import json
import streamlit as st
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
import os

# ---------------------------------------------------------------------------
# 1. SETUP
# ---------------------------------------------------------------------------
load_dotenv()  # reads OPENAI_API_KEY from a local .env file

st.set_page_config(
    page_title="AI Workspace",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# 2. PROMPT TEMPLATES  (Assignment 3 requirement: "Prompt Templates")
# ---------------------------------------------------------------------------
PROMPT_TEMPLATES = {
    "None (free chat)": "",
    "Summarize Text": "Summarize the following text in 3-5 clear bullet points:\n\n{input}",
    "Explain Code": "Explain what the following code does, line by line, in simple terms:\n\n{input}",
    "Generate Ideas": "Brainstorm 10 creative ideas related to the following topic:\n\n{input}",
    "Rewrite Content": "Rewrite the following text to make it clearer and more professional, "
                        "without changing its meaning:\n\n{input}",
    "Translate": "Translate the following text into English (or specify a target language "
                 "at the start of your text):\n\n{input}",
    "Create Email": "Write a professional email based on this description:\n\n{input}",
    "Brainstorm": "Act as a brainstorming partner. Generate multiple angles, pros/cons, "
                  "and next steps for the following idea:\n\n{input}",
}

# Simulated model list — swap in real model names if you have multiple API keys
AVAILABLE_MODELS = {
    "GPT-4o Mini (fast, cheap)": "gpt-4o-mini",
    "GPT-4o (higher quality)": "gpt-4o",
    "GPT-3.5 Turbo (legacy)": "gpt-3.5-turbo",
}

# ---------------------------------------------------------------------------
# 3. SESSION STATE  (this is how we get "memory" during one browser session)
# ---------------------------------------------------------------------------
if "sessions" not in st.session_state:
    # Supports "Multiple Chat Sessions" bonus feature
    st.session_state.sessions = {"Chat 1": []}
if "active_session" not in st.session_state:
    st.session_state.active_session = "Chat 1"
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "total_tokens" not in st.session_state:
    st.session_state.total_tokens = 0


def get_messages():
    return st.session_state.sessions[st.session_state.active_session]


# ---------------------------------------------------------------------------
# 4. DARK MODE (bonus feature) — simple CSS injection
# ---------------------------------------------------------------------------
if st.session_state.dark_mode:
    st.markdown(
        """
        <style>
        .stApp { background-color: #0e1117; color: #fafafa; }
        </style>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# 5. SIDEBAR — settings, model selection, system prompt, templates
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("🧠 AI Workspace")
    st.caption("Your unified interface for AI models")

    st.divider()

    # --- API Key ---
    api_key_input = st.text_input(
        "OpenAI API Key",
        type="password",
        value=os.getenv("OPENAI_API_KEY", ""),
        help="You can also set this permanently in a .env file as OPENAI_API_KEY=sk-...",
    )

    # --- Model selection ---
    st.subheader("Model")
    model_label = st.selectbox("Choose a model", list(AVAILABLE_MODELS.keys()))
    model_name = AVAILABLE_MODELS[model_label]

    # --- System prompt ---
    st.subheader("System Prompt")
    system_prompt = st.text_area(
        "Define how the AI should behave",
        value="You are a helpful, knowledgeable assistant.",
        height=100,
    )

    # --- Prompt templates ---
    st.subheader("Prompt Template")
    template_choice = st.selectbox("Pick a template", list(PROMPT_TEMPLATES.keys()))

    st.divider()

    # --- Chat sessions (bonus) ---
    st.subheader("Chat Sessions")
    session_names = list(st.session_state.sessions.keys())
    st.session_state.active_session = st.radio(
        "Active session", session_names, index=session_names.index(st.session_state.active_session)
    )
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("➕ New Chat"):
            new_name = f"Chat {len(st.session_state.sessions) + 1}"
            st.session_state.sessions[new_name] = []
            st.session_state.active_session = new_name
            st.rerun()
    with col_b:
        if st.button("🗑️ Clear Chat"):
            st.session_state.sessions[st.session_state.active_session] = []
            st.rerun()

    st.divider()

    # --- Bonus features ---
    st.subheader("Options")
    st.session_state.dark_mode = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)

    st.metric("Tokens used (session est.)", st.session_state.total_tokens)

    chat_json = json.dumps(get_messages(), indent=2)
    st.download_button(
        "⬇️ Export This Chat (.json)",
        data=chat_json,
        file_name=f"{st.session_state.active_session.replace(' ', '_')}.json",
        mime="application/json",
    )

# ---------------------------------------------------------------------------
# 6. MAIN CHAT AREA
# ---------------------------------------------------------------------------
st.header(f"💬 {st.session_state.active_session}")
st.caption(f"Model: {model_label}")

# Render past messages (Assignment requirement: Markdown Rendering)
for msg in get_messages():
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "meta" in msg:
            st.caption(msg["meta"])

# Chat input box
user_input = st.chat_input("Ask me anything...")

if user_input:
    # --- Error Handling: empty prompt ---
    if not user_input.strip():
        st.warning("⚠️ Please enter a non-empty message.")
        st.stop()

    # --- Error Handling: missing API key ---
    if not api_key_input:
        st.error("❌ No API key provided. Add your OpenAI API key in the sidebar, "
                  "or place it in a .env file as OPENAI_API_KEY=sk-...")
        st.stop()

    # Apply the selected prompt template, if any
    template = PROMPT_TEMPLATES[template_choice]
    final_prompt = template.format(input=user_input) if template else user_input

    # Save & show the user's message
    get_messages().append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Call the AI model
    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("⏳ Thinking...")
        start_time = time.time()

        try:
            client = OpenAI(api_key=api_key_input)

            api_messages = [{"role": "system", "content": system_prompt}]
            # include recent chat history for context
            for m in get_messages()[:-1]:
                api_messages.append({"role": m["role"], "content": m["content"]})
            api_messages.append({"role": "user", "content": final_prompt})

            response = client.chat.completions.create(
                model=model_name,
                messages=api_messages,
                temperature=0.7,
            )

            reply = response.choices[0].message.content
            elapsed = round(time.time() - start_time, 2)

            # Bonus: token usage counter
            usage = response.usage.total_tokens if response.usage else 0
            st.session_state.total_tokens += usage

            meta = f"⏱️ {elapsed}s · 🔢 {usage} tokens · 📅 {datetime.now().strftime('%H:%M:%S')}"
            placeholder.markdown(reply)
            st.caption(meta)

            get_messages().append({"role": "assistant", "content": reply, "meta": meta})

        # --- Error Handling: invalid key / connection failure ---
        except Exception as e:
            error_msg = str(e)
            if "Incorrect API key" in error_msg or "401" in error_msg:
                friendly = "❌ Invalid API key. Please check the key in the sidebar."
            elif "Connection" in error_msg or "timeout" in error_msg.lower():
                friendly = "❌ Connection failed. Please check your internet connection and try again."
            else:
                friendly = f"❌ Something went wrong: {error_msg}"
            placeholder.markdown(friendly)
            get_messages().append({"role": "assistant", "content": friendly})

# ---------------------------------------------------------------------------
# 7. EMPTY STATE
# ---------------------------------------------------------------------------
if not get_messages():
    st.info(
        "👋 Start a conversation below, or pick a **prompt template** and a "
        "**system prompt** from the sidebar first. Your chat history is kept "
        "for this session and can be exported as JSON."
    )
