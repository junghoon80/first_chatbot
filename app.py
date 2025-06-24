import streamlit as st
import google.generativeai as genai

# secret에서 API 키 불러오기
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# Gemini 2.5 Flash 모델 초기화
model = genai.GenerativeModel("gemini-2.5-flash")

# 대화 기록 관리
if "history" not in st.session_state:
    st.session_state.history = []

st.title("🚀 Gemini 2.5 Flash AI 챗봇")

# 기존 대화 내용 표시
for role, msg in st.session_state.history:
    with st.chat_message(role):
        st.write(msg)

# 사용자 입력 처리
user_input = st.chat_input("메시지를 입력하세요")
if user_input:
    # 사용자 메시지 추가 및 표시
    st.session_state.history.append(("user", user_input))
    with st.chat_message("user"):
        st.write(user_input)

    # AI 응답 생성
    with st.chat_message("assistant"):
        with st.spinner("Gemini 2.5 Flash가 답변 중..."):
            try:
                # 대화 기록을 Gemini 형식으로 변환
                chat_history = [
                    {"role": role, "parts": [msg]} 
                    for role, msg in st.session_state.history
                ]
                
                # 대화 시작 및 응답 생성
                convo = model.start_chat(history=chat_history)
                response = convo.send_message(user_input)
                
                # 응답 표시 및 기록
                st.write(response.text)
                st.session_state.history.append(("assistant", response.text))
                
            except Exception as e:
                error_msg = f"오류 발생: {str(e)}"
                st.error(error_msg)
                st.session_state.history.append(("assistant", error_msg))
