import streamlit as st
import requests
import os

API_HOST = os.getenv("BACKEND_URL", "http://localhost:8000")
st.title("🧠 Проверка чата с Профессором КРАБом")
st.write(f"🔗 API подключение: `{API_HOST}`")

question = st.text_input("Введите вопрос:")

if st.button("Отправить запрос"):
    if not question:
        st.warning("Введите вопрос.")
    else:
        payload = {"question": question, "chat_history": []}
        try:
            response = requests.post(f"{API_HOST}/ask", json=payload)
            if response.status_code == 200:
                result = response.json()
                st.success("✅ Ответ получен!")
                st.write(result["answer"])
                st.info("📚 Источники: " + ", ".join(result["sources"]))
            else:
                st.error(f"Ошибка API {response.status_code}: {response.text}")
        except Exception as e:
            st.error(f"Ошибка соединения: {e}")
