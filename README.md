# ZEMA AI Assistant

A branded, multilingual Streamlit assistant for ZEMA product guidance and general business assistance.

## Current status

**Stage: deployed assistant / integration in progress.**

- Platform: Streamlit Community Cloud
- Repository: `ZemaEthio/chatbot`
- Current AI provider: Google Gemini Developer API
- Deployment branch: `main`
- Required secret: `GEMINI_API_KEY` in Streamlit Secrets
- Product direction: become an assistant layer that can be embedded into or connected with ZEMA CRM, ZEMA Digital, and other ZEMA products

The current public deployment should not receive confidential customer, employee, financial, or production database data unless the provider plan and data-handling controls have been explicitly approved for that use.

## Features

- Server-side provider credential handling
- Conversation-aware assistance
- ZEMA product guidance
- English, Amharic, and automatic language selection
- Quick-start prompts and transcript download
- Responsive ZEMA-branded interface
- User-friendly provider error handling

## Architecture direction

```text
ZEMA product UI
      |
      v
ZEMA Assistant service
      |
      +--> approved AI provider
      +--> product knowledge/context
      +--> controlled product APIs/tools
```

The assistant should not receive privileged database or integration credentials. Product actions should occur through authenticated, permission-checked APIs.

## Run locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Create `.streamlit/secrets.toml` locally with the required provider key. Never commit that file.

## Deploy on Streamlit Community Cloud

Deploy `streamlit_app.py` from this repository. Store `GEMINI_API_KEY` under the app's **Settings → Secrets**, save, reboot, and run a controlled test.

## DEV vs PROD rules

- Keep provider secrets server-side.
- Do not place API keys in issues, screenshots, transcripts, or README files.
- Use non-sensitive product/test context while developing tool integrations.
- Require authenticated product APIs before the assistant can read or change customer data.
- Add audit records for assistant-triggered business actions.
- Add human confirmation for high-impact outbound or destructive actions.

## Troubleshooting

| App message | Meaning | Action |
|---|---|---|
| Assistant not connected | Provider key is missing or assigned to another app | Add the exact secret name and reboot |
| `401 UNAUTHENTICATED` | Invalid provider credential | Replace/rotate the key |
| `403 PERMISSION_DENIED` | Project/model access issue | Verify provider project and model access |
| `404 NOT_FOUND` | Selected model unavailable | Select a supported configured model |
| `429 RESOURCE_EXHAUSTED` | Provider quota/rate limit reached | Wait for quota reset or change approved plan |

## Production gates for product integration

1. Authenticated user identity from the host ZEMA product
2. Permission-aware API/tool calls
3. Tenant isolation
4. Sensitive-data/provider review
5. Audit logging
6. Safe tool confirmation policies
7. Rate limiting and failure handling
8. Monitoring and rollback

## Engineering documentation

ZEMA-wide product, environment, architecture, security, deployment, and release standards are maintained in **`ZemaEthio/zema-platform-docs`**.
