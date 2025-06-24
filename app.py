import streamlit as st
from huggingface_hub import InferenceClient
import os

# 페이지 설정
st.set_page_config(
    page_title="🤗 HF Inference Chatbot",
    layout="wide"
)
st.title("🤗 HF Inference Chatbot")

# Hugging Face 토큰 설정
hf_token = st.secrets["HF_TOKEN"]
client = InferenceClient(model="mistralai/Mistral-7B-Instruct-v0.2", token=hf_token)

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 기존 메시지 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 사용자 입력 처리
if prompt := st.chat_input("메시지를 입력하세요..."):
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    # AI 응답 생성
    with st.chat_message("assistant"):
        response_container = st.empty()
        
        try:
            # 대화 기록을 포함한 메시지 구성
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            ]
            
            # InferenceClient로 생성 요청
            response = client.chat_completion(
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            # 응답에서 내용 추출
            ai_response = response.choices[0].message.content
            response_container.write(ai_response)
            
            # AI 응답을 히스토리에 추가
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            
        except Exception as e:
            response_container.error(f"오류 발생: {str(e)}")
