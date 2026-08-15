# ZEMA AI Assistant

A branded, multilingual Streamlit chatbot for business guidance, SQL Server expertise, ZEMA product questions, and general assistance.

## Features

- Secure server-side OpenAI key; visitors never enter or see the key
- OpenAI Responses API with conversation-aware answers
- Business, SQL Server, ZEMA product, and general assistant modes
- English, Amharic, and automatic language selection
- Quick-start prompts, new-chat control, and transcript download
- Responsive ZEMA-branded interface and user-friendly API error handling

## Run locally

1. Install dependencies: `pip install -r requirements.txt`
2. Add `OPENAI_API_KEY = "your-key"` to `.streamlit/secrets.toml`.
3. Start the app: `streamlit run streamlit_app.py`

## Deploy on Streamlit Community Cloud

Deploy `streamlit_app.py` from this repository. In **App settings → Secrets**, add:

```toml
OPENAI_API_KEY = "your-key"
```

Never commit `.streamlit/secrets.toml`; it is excluded by `.gitignore`.

## Configuration

The default model is `gpt-5-mini`. Users can select `gpt-4.1-mini` in the sidebar when needed.
