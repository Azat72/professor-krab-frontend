import streamlit as st
import requests
import os
import re
import uuid
from PIL import Image

st.set_page_config(page_title="Юридический консультант", layout="wide")

API_URL = "https://professor-krab-backend.onrender.com"
SOURCE_DOCS_DIR = "source_docs"
LOGO_PATH = "logo_krab.png"

if "projects" not in st.session_state:
    st.session_state.projects = {}
if "project_names" not in st.session_state:
    st.session_state.project_names = {}
if "active_project" not in st.session_state:
    new_id = str(uuid.uuid4())
    st.session_state.projects[new_id] = []
    st.session_state.project_names[new_id] = "Проект 1"
    st.session_state.active_project = new_id

# Заголовок и логотип
if os.path.exists(LOGO_PATH):
    st.image(LOGO_PATH, width=100)
st.markdown("## Профессор КРАБ")

# Выбор и переименование проектов
st.sidebar.subheader("📁 Мои проекты")
project_id_list = list(st.session_state.projects.keys())
current_project = st.sidebar.radio("Выберите проект:", project_id_list, format_func=lambda x: st.session_state.project_names.get(x, x))
st.session_state.active_project = current_project

new_name = st.sidebar.text_input("✏️ Переименовать проект:", value=st.session_state.project_names[current_project])
if st.sidebar.button("💾 Сохранить имя"):
    st.session_state.project_names[current_project] = new_name
    st.rerun()

if st.sidebar.button("➕ Новый проект"):
    new_id = str(uuid.uuid4())
    st.session_state.projects[new_id] = []
    st.session_state.project_names[new_id] = f"Проект {len(st.session_state.projects)}"
    st.session_state.active_project = new_id
    st.rerun()

question = st.chat_input("Задайте вопрос по нормативной базе:")

def find_matching_doc(source_name):
    def normalize(text):
        return re.sub(r"[^а-яa-z0-9]", "", text.lower())
    target = normalize(source_name)
    for file in os.listdir(SOURCE_DOCS_DIR):
        if normalize(file).startswith(target):
            return os.path.join(SOURCE_DOCS_DIR, file)
    return None

# История чата
for entry in st.session_state.projects[st.session_state.active_project]:
    with st.chat_message("user"):
        st.markdown(entry["question"])
    with st.chat_message("assistant"):
        st.markdown(entry["answer"])
        sources = entry.get("filtered_sources", [])
        if sources:
            st.markdown("**📄 Документы с ответом:**")
            for doc in sources:
                doc_path = find_matching_doc(doc)
                if doc_path and os.path.exists(doc_path):
                    with open(doc_path, "rb") as f:
                        st.download_button(
                            label=f"📥 Скачать {os.path.basename(doc_path)}",
                            data=f,
                            file_name=os.path.basename(doc_path),
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                else:
                    st.warning(f"⚠ Документ не найден: {doc}")

# Запрос
if question:
    with st.chat_message("user"):
        st.markdown(question)
    try:
        history = [
            {"question": h["question"], "answer": h["answer"]}
            for h in st.session_state.projects[st.session_state.active_project]
        ]
        response = requests.post(API_URL, json={
            "question": question,
            "chat_history": history
        }, timeout=60)
        response.raise_for_status()
        result = response.json()

        debug_info = result.get("debug", [])
        filtered_sources = []
        seen_titles = set()
        for item in debug_info:
            score = item.get("score", 0)
            title = item.get("title")
            if title and score >= 0.58 and title not in seen_titles:
                filtered_sources.append(title)
                seen_titles.add(title)

        new_entry = {
            "question": question,
            "answer": result.get("answer", "Нет ответа"),
            "sources": result.get("sources", []),
            "filtered_sources": filtered_sources
        }
        st.session_state.projects[st.session_state.active_project].append(new_entry)

        with st.chat_message("assistant"):
            st.markdown(new_entry["answer"])
            if filtered_sources:
                st.markdown("**📄 Документы с ответом:**")
                for doc in filtered_sources:
                    doc_path = find_matching_doc(doc)
                    if doc_path and os.path.exists(doc_path):
                        with open(doc_path, "rb") as f:
                            st.download_button(
                                label=f"📥 Скачать {os.path.basename(doc_path)}",
                                data=f,
                                file_name=os.path.basename(doc_path),
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            )
                    else:
                        st.warning(f"⚠ Документ не найден: {doc}")

    except Exception as e:
        st.error(f"Ошибка API: {e}")

st.markdown("---")
if st.button("🗑 Очистить текущий проект"):
    st.session_state.projects[st.session_state.active_project] = []
    st.rerun()
