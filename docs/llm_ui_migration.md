# LLM-First UI Migration

This document explains the new architecture that converts the legacy Streamlit dashboard into a conversation-first experience backed by the LangGraph workflow.

## Components

- **FastAPI backend (`services/api.py`)** – exposes REST endpoints for sessions, chat messages, progress polling, and artifact retrieval.
- **Conversation manager (`services/conversation_manager.py`)** – maintains chat state, validates course requirements, launches the workflow in background threads, and surfaces summaries/errors.
- **Instrumentation (`services/instrumentation.py`)** – streams structured logs to `logs/conversations/` for auditing.
- **Chat UI (`ui/chat_app.py`)** – Streamlit-based chat surface that talks to the FastAPI backend, shows conversation context, workflow progress, and generated artifacts.

## Running locally

1. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Start the backend**

   ```bash
   uvicorn services.api:app --reload --port 8000
   ```

3. **Launch the chat UI**

   ```bash
   streamlit run ui/chat_app.py
   ```

   Set `COURSE_CHAT_API_URL` if the API is served on a different host/port.

## Conversation workflow

1. Create a session via `POST /api/sessions`.
2. Send free-form chat messages to collect requirements (`POST /api/sessions/{id}/messages`).
3. When ready, submit the form in the UI (or send a payload with `action=generate_course`) to kick off the LangGraph workflow.
4. Poll `/api/sessions/{id}/progress` for real-time status and `/api/sessions/{id}/artifacts` to fetch outputs.
5. Conversation logs and workflow summaries are persisted for later review.

## Next steps

- Swap the Streamlit chat UI with a dedicated React/Next.js front end.
- Wire moderation/guardrails before workflow launch.
- Expand instrumentation hooks to metrics backends (Prometheus/OpenTelemetry) for richer analytics.

