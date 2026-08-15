import os
from datetime import datetime, timezone

import streamlit as st
from google import genai
from google.genai import errors, types


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

PRODUCT_CONTEXTS = {
    "general": {
        "name": "ZEMA AI",
        "subtitle": "Your intelligent business companion",
        "mode": "Business Assistant",
        "guidance": "Help across ZEMA products and general business operations.",
        "prompts": {
            "Create a business plan": "Create a practical one-page business plan for my idea.",
            "Analyze SQL performance": "Help me diagnose a SQL Server performance problem step by step.",
            "Write customer outreach": "Write a concise, professional customer outreach message.",
        },
    },
    "crm": {
        "name": "ZEMA CRM Assistant",
        "subtitle": "Your AI sales and customer operations partner",
        "mode": "Business Assistant",
        "guidance": "Focus on CRM workflows: lead qualification, pipeline health, follow-ups, sales tasks, customer communication, and retention. Give practical next actions and never invent customer data.",
        "prompts": {
            "Qualify a lead": "Help me qualify a lead and recommend the next best action.",
            "Draft a follow-up": "Draft a concise, professional follow-up message for a sales lead.",
            "Review my pipeline": "Help me review pipeline risks and prioritize follow-ups.",
        },
    },
    "digital": {
        "name": "ZEMA Digital Assistant",
        "subtitle": "Your AI marketing and campaign partner",
        "mode": "Business Assistant",
        "guidance": "Focus on digital marketing workflows: campaign strategy, content creation, client approvals, social media, email, local marketing, lead generation, and reporting. Never invent performance results or client facts.",
        "prompts": {
            "Create campaign ideas": "Create three practical campaign ideas for a local service business.",
            "Draft social content": "Draft a social media post with a clear call to action.",
            "Prepare a client report": "Help me summarize marketing activity and business outcomes for a client.",
        },
    },
}

GEMINI_MODELS = (
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash-lite",
)


def get_api_key() -> str | None:
    """Read a server-side key without asking visitors to expose credentials."""
    environment_key = os.getenv("GEMINI_API_KEY")
    if environment_key:
        return environment_key
    try:
        return st.secrets.get("GEMINI_API_KEY")
    except (FileNotFoundError, KeyError):
        return None


def build_instructions(
    mode: str, language: str, product_guidance: str, product_context: str
) -> str:
    context_guidance = (
        f" Current DEV product context: {product_context}. "
        "Treat these values as read-only context and do not invent missing records."
        if product_context
        else ""
    )
    return (
        "You are ZEMA AI, a helpful, accurate, and friendly assistant. "
        f"{ASSISTANT_MODES[mode]} {LANGUAGE_GUIDANCE[language]} {product_guidance}"
        f"{context_guidance} "
        "Lead with the answer, use concise structure, and ask a clarifying question only when essential. "
        "Do not claim to have completed external actions you did not perform."
    )


def transcript() -> str:
    lines = ["ZEMA AI Assistant conversation", ""]
    for message in st.session_state.messages:
        speaker = "You" if message["role"] == "user" else "ZEMA AI"
        lines.extend([f"{speaker}:", message["content"], ""])
    return "\n".join(lines)


def generate_response(
    client: genai.Client, model: str, instructions: str
) -> tuple[str, str]:
    history = [
        types.Content(
            role="model" if message["role"] == "assistant" else "user",
            parts=[types.Part(text=message["content"])],
        )
        for message in st.session_state.messages
    ]
    candidates = (model, *(candidate for candidate in GEMINI_MODELS if candidate != model))
    last_not_found = None
    for candidate in candidates:
        try:
            response = client.models.generate_content(
                model=candidate,
                contents=history,
                config=types.GenerateContentConfig(system_instruction=instructions),
            )
            if not response.text:
                raise RuntimeError("Gemini returned an empty response")
            return response.text, candidate
        except errors.ClientError as error:
            if error.code != 404:
                raise
            last_not_found = error
    raise last_not_found or RuntimeError("No Gemini model is available")


product_key = st.query_params.get("product", "general").lower()
product = PRODUCT_CONTEXTS.get(product_key, PRODUCT_CONTEXTS["general"])
product_context = st.query_params.get("context", "").strip()[:1000]

if "messages" not in st.session_state:
    st.session_state.messages = []

api_key = get_api_key()

with st.sidebar:
    st.markdown(f"## ✨ {product['name']}")
    st.caption(product["subtitle"])
    st.markdown("---")
    mode_names = list(ASSISTANT_MODES)
    mode = st.selectbox(
        "Assistant mode",
        mode_names,
        index=mode_names.index(product["mode"]),
    )
    language = st.selectbox("Response language", list(LANGUAGE_GUIDANCE))
    model = st.selectbox("AI model", GEMINI_MODELS[:2])
    st.markdown("---")
    st.caption("QUICK START")
    quick_prompts = product["prompts"]
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
    connection_status = "● Gemini connected" if api_key else "● Setup required"
    st.markdown(f'<p class="status-pill">{connection_status}</p>', unsafe_allow_html=True)

st.markdown(
    f"""
    <section class="zema-hero">
      <div class="zema-badge">{product['name']}</div>
      <h1>How can I help you today?</h1>
      <p>{product['subtitle']}</p>
    </section>
    """,
    unsafe_allow_html=True,
)

if not st.session_state.messages:
    st.info("Ask a question below or choose a quick start from the sidebar.", icon="💡")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = selected_prompt or st.chat_input("Message ZEMA AI…", disabled=not api_key)

if not api_key:
    st.error(
        "The assistant is not connected yet. The app owner must add GEMINI_API_KEY "
        "in Streamlit App settings → Secrets."
    )
elif prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    client = genai.Client(api_key=api_key)
    try:
        with st.chat_message("assistant"):
            with st.spinner("ZEMA AI is thinking…"):
                response, used_model = generate_response(
                    client,
                    model,
                    build_instructions(
                        mode, language, product["guidance"], product_context
                    ),
                )
            st.markdown(response)
            if used_model != model:
                st.caption(f"Answered with fallback model: {used_model}")
        st.session_state.messages.append({"role": "assistant", "content": response})
    except errors.APIError as error:
        explanations = {
            400: "Google rejected the request configuration.",
            401: "The Gemini API key is invalid.",
            403: "This API key or region does not have access to the selected model.",
            404: "The selected Gemini model is not available for this API key.",
            429: "The Gemini free-tier request limit has been reached.",
        }
        explanation = explanations.get(error.code, "Google Gemini returned an API error.")
        st.error(
            f"{explanation} Error `{error.code} {error.status or 'UNKNOWN'}`."
        )
    except Exception as error:
        st.error(
            "Gemini could not complete the request. "
            f"Diagnostic code: `{type(error).__name__}`. Please try again."
        )
