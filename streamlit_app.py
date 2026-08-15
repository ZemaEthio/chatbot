import os
from datetime import datetime, timezone

import streamlit as st
from openai import APIConnectionError, APIStatusError, OpenAI, RateLimitError


st.set_page_config(page_title="ZEMA AI Assistant", page_icon="✨", layout="wide")

st.markdown(
    """
    <style>
      :root { --zema-gold: #f7b731; --zema-navy: #0b1930; }
      .stApp { background: linear-gradient(145deg, #f8fafc 0%, #eef4ff 100%); }
      [data-testid="stSidebar"] { background: var(--zema-navy); }
      [data-testid="stSidebar"] * { color: #f8fafc; }
      [data-testid="stSidebar"] .stButton button {
        border: 1px solid rgba(255,255,255,.24); background: rgba(255,255,255,.08);
      }
      .zema-hero {
        padding: 1.4rem 1.6rem; border-radius: 22px; color: white;
        background: linear-gradient(120deg, #0b1930, #143b69);
        box-shadow: 0 18px 45px rgba(11,25,48,.16); margin-bottom: 1rem;
      }
      .zema-hero h1 { margin: 0; font-size: clamp(1.8rem, 4vw, 3rem); }
      .zema-hero p { margin: .5rem 0 0; color: #dce9f8; }
      .zema-badge { color: var(--zema-gold); font-weight: 700; letter-spacing: .08em; }
      [data-testid="stChatMessage"] {
        border: 1px solid rgba(20,59,105,.10); border-radius: 18px;
        background: rgba(255,255,255,.84); padding: .35rem .65rem;
      }
      .status-pill { color: #55d68b; font-size: .88rem; font-weight: 650; }
      footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

ASSISTANT_MODES = {
    "Business Assistant": "Help with business planning, sales, marketing, operations, and customer communication.",
    "SQL Server Expert": "Act as a senior Microsoft SQL Server DBA specializing in Azure, HA/DR, Linux, performance tuning, and automation.",
    "ZEMA Product Guide": "Explain ZEMA products clearly and help customers choose the right solution. Never invent pricing or capabilities.",
    "General Assistant": "Be a versatile, practical assistant for everyday questions and tasks.",
}

LANGUAGE_GUIDANCE = {
    "Auto-detect": "Reply in the language used by the user.",
    "English": "Reply in clear English.",
    "Amharic": "Reply in natural Amharic unless technical terms are clearer in English.",
}


def get_api_key() -> str | None:
    """Read a server-side key without asking visitors to expose credentials."""
    try:
        return st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    except (FileNotFoundError, KeyError):
        return os.getenv("OPENAI_API_KEY")


def build_instructions(mode: str, language: str) -> str:
    return (
        "You are ZEMA AI, a helpful, accurate, and friendly assistant. "
        f"{ASSISTANT_MODES[mode]} {LANGUAGE_GUIDANCE[language]} "
        "Lead with the answer, use concise structure, and ask a clarifying question only when essential. "
        "Do not claim to have completed external actions you did not perform."
    )


def transcript() -> str:
    lines = ["ZEMA AI Assistant conversation", ""]
    for message in st.session_state.messages:
        speaker = "You" if message["role"] == "user" else "ZEMA AI"
        lines.extend([f"{speaker}:", message["content"], ""])
    return "\n".join(lines)


def stream_response(client: OpenAI, model: str, instructions: str):
    history = [
        {"role": message["role"], "content": message["content"]}
        for message in st.session_state.messages
    ]
    with client.responses.stream(model=model, instructions=instructions, input=history) as stream:
        for event in stream:
            if event.type == "response.output_text.delta":
                yield event.delta


if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.markdown("## ✨ ZEMA AI")
    st.caption("Your intelligent business companion")
    st.markdown("---")
    mode = st.selectbox("Assistant mode", list(ASSISTANT_MODES))
    language = st.selectbox("Response language", list(LANGUAGE_GUIDANCE))
    model = st.selectbox("AI model", ["gpt-5-mini", "gpt-4.1-mini"])
    st.markdown("---")
    st.caption("QUICK START")
    quick_prompts = {
        "Create a business plan": "Create a practical one-page business plan for my idea.",
        "Analyze SQL performance": "Help me diagnose a SQL Server performance problem step by step.",
        "Write customer outreach": "Write a concise, professional customer outreach message.",
    }
    selected_prompt = None
    for label, prompt_text in quick_prompts.items():
        if st.button(label, use_container_width=True):
            selected_prompt = prompt_text
    st.markdown("---")
    left, right = st.columns(2)
    if left.button("New chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    right.download_button(
        "Download",
        transcript(),
        file_name=f"zema-chat-{datetime.now(timezone.utc):%Y%m%d}.txt",
        mime="text/plain",
        use_container_width=True,
        disabled=not st.session_state.messages,
    )
    st.markdown('<p class="status-pill">● Secure connection ready</p>', unsafe_allow_html=True)

st.markdown(
    """
    <section class="zema-hero">
      <div class="zema-badge">ZEMA AI</div>
      <h1>How can I help you today?</h1>
      <p>Business strategy, SQL Server expertise, customer communication, and everyday answers—together in one assistant.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

if not st.session_state.messages:
    st.info("Ask a question below or choose a quick start from the sidebar.", icon="💡")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

api_key = get_api_key()
prompt = selected_prompt or st.chat_input("Message ZEMA AI…", disabled=not api_key)

if not api_key:
    st.error(
        "The assistant is not connected yet. The app owner must add OPENAI_API_KEY "
        "in Streamlit App settings → Secrets."
    )
elif prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    client = OpenAI(api_key=api_key)
    try:
        with st.chat_message("assistant"):
            response = st.write_stream(stream_response(client, model, build_instructions(mode, language)))
        st.session_state.messages.append({"role": "assistant", "content": response})
    except RateLimitError:
        st.warning("The AI service has reached its current usage limit. Please try again shortly.")
    except APIConnectionError:
        st.warning("ZEMA AI could not connect to the AI service. Please try again.")
    except APIStatusError as error:
        st.error(f"The AI service returned an error (status {error.status_code}).")
    except Exception:
        st.error("Something unexpected happened. Please try again or start a new chat.")
