import streamlit as st
import google.generativeai as genai

# secret에서 API 키 불러오기
api_key = st.secrets["GEMINI_API_KEY"]

# Gemini API 설정
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")  # 또는 "gemini-1.5-pro"

# 대화 기록 관리
if "history" not in st.session_state:
    st.session_state.history = []

st.title("Gemini AI 챗봇")
for role, msg in st.session_state.history:
    with st.chat_message(role):
        st.write(msg)

user_input = st.chat_input("메시지를 입력하세요")
if user_input:
    st.session_state.history.append(("user", user_input))
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Gemini가 답변 중..."):
            convo = model.start_chat(history=[
                {"role": role, "parts": [msg]} for role, msg in st.session_state.history
            ])
            response = convo.send_message(user_input)
            st.write(response.text)
            st.session_state.history.append(("assistant", response.text))
