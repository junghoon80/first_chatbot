import streamlit as st
import google.generativeai as genai

api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash")

if "history" not in st.session_state:
    st.session_state.history = []

st.title("🚀 Gemini 2.5 Flash AI 챗봇")

# 기존 대화 내용 표시
for role, msg in st.session_state.history:
    with st.chat_message("user" if role == "user" else "assistant"):
        st.write(msg)

user_input = st.chat_input("메시지를 입력하세요")
if user_input:
    st.session_state.history.append(("user", user_input))
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Gemini 2.5 Flash가 답변 중..."):
            try:
                # Gemini가 요구하는 role만 사용
                chat_history = [
                    {"role": "user" if role == "user" else "model", "parts": [msg]}
                    for role, msg in st.session_state.history
                ]
                convo = model.start_chat(history=chat_history)
                response = convo.send_message(user_input)
                st.write(response.text)
                # 답변 role을 반드시 "model"로 저장
                st.session_state.history.append(("model", response.text))
            except Exception as e:
                error_msg = f"오류 발생: {str(e)}"
                st.error(error_msg)
                st.session_state.history.append(("model", error_msg))
