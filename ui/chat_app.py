"""Chat-first Streamlit UI that talks to the FastAPI backend."""

from __future__ import annotations

import os
import time
from typing import Any, Dict, Optional

import requests
import streamlit as st
from streamlit_autorefresh import st_autorefresh


API_BASE_URL = os.environ.get("COURSE_CHAT_API_URL", "http://localhost:8000/api")


def _api_url(path: str) -> str:
    return f"{API_BASE_URL}{path}"


def ensure_session() -> None:
    if "chat_session_id" in st.session_state:
        return
    title = st.session_state.get("chat_session_title") or "AI Course Builder Session"
    response = requests.post(_api_url("/sessions"), json={"title": title}, timeout=10)
    response.raise_for_status()
    data = response.json()
    st.session_state.chat_session_id = data["session_id"]
    st.session_state.chat_thread_id = data["thread_id"]


def fetch_session_state() -> Optional[Dict[str, Any]]:
    session_id = st.session_state.get("chat_session_id")
    if not session_id:
        return None
    response = requests.get(_api_url(f"/sessions/{session_id}"), timeout=10)
    response.raise_for_status()
    return response.json()


def send_message(message: str, action: Optional[str] = None, course_config: Optional[Dict[str, Any]] = None):
    session_id = st.session_state.get("chat_session_id")
    if not session_id:
        st.error("Session not initialized")
        return
    payload: Dict[str, Any] = {"message": message}
    if action:
        payload["action"] = action
    if course_config:
        payload["course_config"] = course_config

    response = requests.post(
        _api_url(f"/sessions/{session_id}/messages"),
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    st.session_state.last_session_state = response.json()


def fetch_progress() -> Dict[str, Any]:
    session_id = st.session_state.get("chat_session_id")
    if not session_id:
        return {}
    response = requests.get(_api_url(f"/sessions/{session_id}/progress"), timeout=10)
    if response.status_code == 404:
        return {}
    response.raise_for_status()
    return response.json()


def fetch_artifacts() -> Dict[str, Any]:
    session_id = st.session_state.get("chat_session_id")
    if not session_id:
        return {}
    response = requests.get(_api_url(f"/sessions/{session_id}/artifacts"), timeout=10)
    if response.status_code == 404:
        return {}
    response.raise_for_status()
    return response.json().get("artifacts", {})


def render_messages(session_state: Dict[str, Any]) -> None:
    st.subheader("Conversation")
    for msg in session_state.get("messages", []):
        role = msg["role"]
        if role == "system":
            st.info(msg["content"])
            continue
        with st.chat_message(role):
            st.write(msg["content"])


def render_progress(progress_data: Dict[str, Any]) -> None:
    st.subheader("Workflow Progress")
    steps = progress_data.get("steps", [])
    if not steps:
        st.info("No workflow activity yet.")
        return
    for step in reversed(steps[-8:]):
        st.write(f"{step['timestamp']} — **{step['step']}** {step['status']}")


def render_artifacts(artifacts: Dict[str, Any]) -> None:
    st.subheader("Artifacts")
    if not artifacts:
        st.info("No artifacts available yet.")
        return
    for key, value in artifacts.items():
        with st.expander(key, expanded=False):
            st.json(value)


def sidebar_form() -> Optional[Dict[str, Any]]:
    st.sidebar.subheader("Course Requirements")
    with st.sidebar.form("course_config_form"):
        course_subject = st.text_input("Course Subject", value="Generative AI Foundations")
        learner_level = st.selectbox("Learner Level", ["basic", "intermediate", "advanced"], index=1)
        course_duration = st.text_input("Course Duration", value="4 weeks")
        number_of_modules = st.slider("Number of Modules", min_value=1, max_value=12, value=4)
        graded_quizzes = st.slider("Graded Quizzes / Module", min_value=0, max_value=5, value=1)
        practice_quizzes = st.slider("Practice Quizzes / Module", min_value=0, max_value=10, value=2)
        needs_lab = st.checkbox("Include Lab Module", value=True)
        custom_prompt = st.text_area("Custom Instructions", value="", height=80)
        submitted = st.form_submit_button("Generate Course", use_container_width=True)

    if submitted:
        return {
            "course_subject": course_subject,
            "learner_level": learner_level,
            "course_duration": course_duration,
            "number_of_modules": number_of_modules,
            "graded_quizzes_per_module": graded_quizzes,
            "practice_quizzes_per_module": practice_quizzes,
            "needs_lab_module": needs_lab,
            "custom_prompt": custom_prompt,
        }
    return None


def main() -> None:
    st.set_page_config(page_title="AI Course Builder Assistant", layout="wide")
    st.title("🤝 AI Course Builder Assistant")
    st.caption("Chat-native front door for the LangGraph workflow.")

    ensure_session()
    st_autorefresh(interval=15_000, key="chat_auto_refresh")

    latest_state = fetch_session_state()
    if latest_state:
        st.session_state.last_session_state = latest_state

    col1, col2 = st.columns([2, 1])

    with col1:
        session_state = st.session_state.get("last_session_state")
        if session_state:
            render_messages(session_state)
        else:
            st.info("Start the conversation below.")

        prompt = st.chat_input("Send a message to the assistant")
        if prompt:
            send_message(prompt)
            time.sleep(0.2)
            st.experimental_rerun()

    with col2:
        config_data = sidebar_form()
        if config_data:
            send_message(
                "Here are my latest requirements – please build the course.",
                action="generate_course",
                course_config=config_data,
            )
            st.success("Workflow launched with the provided configuration.")
            st.experimental_rerun()

        progress_data = fetch_progress()
        render_progress(progress_data)

        artifacts = fetch_artifacts()
        render_artifacts(artifacts)


if __name__ == "__main__":
    main()

