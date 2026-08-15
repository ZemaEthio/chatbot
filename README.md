# ZEMA AI Assistant

A branded, multilingual Streamlit chatbot for business guidance, SQL Server expertise, ZEMA product questions, and general assistance.

## Current status

- **Platform:** Streamlit Community Cloud
- **Repository:** `ZemaEthio/chatbot`
- **AI provider:** Google Gemini Developer API
- **Default model:** `gemini-3.5-flash-lite`
- **Alternative model:** `gemini-3.1-flash-lite`
- **API plan:** Gemini free tier (subject to Google's rate limits and availability)
- **OpenAI dependency:** Removed; OpenAI billing and `OPENAI_API_KEY` are no longer required
- **Deployment state:** Code is published to `main`; the deployed app requires `GEMINI_API_KEY` in Streamlit Secrets

## Features

- Secure server-side Gemini key; visitors never enter or see the key
- Google Gemini API with conversation-aware answers
- Business, SQL Server, ZEMA product, and general assistant modes
- English, Amharic, and automatic language selection
- Quick-start prompts, new-chat control, and transcript download
- Responsive ZEMA-branded interface and user-friendly API error handling

## Run locally

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Create `.streamlit/secrets.toml` and add:

   ```toml
   GEMINI_API_KEY = "your-complete-key"
   ```

3. Start the app:

   ```bash
   streamlit run streamlit_app.py
   ```

## Deploy on Streamlit Community Cloud

Deploy `streamlit_app.py` from this repository. In **App settings → Secrets**, add:

```toml
GEMINI_API_KEY = "your-complete-key"
```

Save the secret, reboot the app, and test with `Hello ZEMA AI`.

Never commit `.streamlit/secrets.toml`, paste API keys into issues, or include keys in screenshots. The local secret file is excluded by `.gitignore`.

## Configuration

The default model is `gemini-3.5-flash-lite`. Users can select `gemini-3.1-flash-lite` in the sidebar when needed. Both have eligible free-tier usage.

Free-tier requests may be used by Google to improve its products. Do not send confidential customer, employee, financial, or production database information through the free-tier deployment.

## Troubleshooting

| App message | Meaning | Action |
|---|---|---|
| `The assistant is not connected yet` | `GEMINI_API_KEY` is missing or saved in a different Streamlit app | Add the exact variable name under the chatbot app's **Settings → Secrets**, save, and reboot |
| `401 UNAUTHENTICATED` | The Gemini key is invalid | Create a new Google AI Studio key and replace the Streamlit secret |
| `403 PERMISSION_DENIED` | The project or region cannot access the selected model | Verify Gemini API access for the Google project |
| `404 NOT_FOUND` | The selected model is unavailable | Reboot to load the current model list, then select `gemini-3.5-flash-lite` |
| `429 RESOURCE_EXHAUSTED` | The free-tier rate limit was reached | Wait for the quota window to reset or enable paid Gemini API usage |

## Upgrade history

The original repository was Streamlit's GPT-3.5 chatbot template. It has been upgraded with ZEMA branding, server-side credential handling, Gemini integration, multilingual support, specialized assistant modes, conversation history, transcript download, and actionable API diagnostics.
