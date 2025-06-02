import streamlit as st

st.set_page_config(page_title="Проверка Streamlit")
st.title("✅ Streamlit работает!")

if st.button("Нажми меня"):
    st.success("Streamlit живой 🟢")
