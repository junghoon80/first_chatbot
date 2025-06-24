import streamlit as st
import google.generativeai as genai
from duckduckgo_search import DDGS

# Gemini 설정
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash")

# 웹 검색 함수
def web_search(query: str, max_results: int = 3) -> str:
    """DuckDuckGo를 이용한 웹 검색"""
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=max_results)]
            if not results:
                return "검색 결과가 없습니다."
                
            return "\n\n".join([
                f"제목: {r['title']}\n링크: {r['href']}\n요약: {r['body']}"
                for r in results
            ])
    except Exception as e:
        return f"검색 오류: {str(e)}"

# 대화 기록 관리
if "history" not in st.session_state:
    st.session_state.history = []
    
# 웹 검색 활성화 상태
if "web_search_enabled" not in st.session_state:
    st.session_state.web_search_enabled = False

# 사이드바 설정
with st.sidebar:
    st.header("웹 검색 설정")
    st.session_state.web_search_enabled = st.checkbox("웹 검색 활성화")
    max_results = st.slider("최대 검색 결과 수", 1, 5, 3)
    
    if st.button("대화 기록 초기화"):
        st.session_state.history = []

# 채팅 UI
st.title("🔍 웹 검색 통합 AI 챗봇")

# 대화 기록 표시
for role, msg in st.session_state.history:
    with st.chat_message(role):
        st.write(msg)

# 사용자 입력 처리
user_input = st.chat_input("메시지를 입력하세요...")
if user_input:
    # 사용자 메시지 저장 및 표시
    st.session_state.history.append(("user", user_input))
    with st.chat_message("user"):
        st.write(user_input)
    
    # 웹 검색 실행 (활성화된 경우)
    search_results = ""
    if st.session_state.web_search_enabled:
        with st.spinner("웹 검색 중..."):
            search_results = web_search(user_input, max_results)
            
            # 검색 결과를 대화 기록에 추가
            st.session_state.history.append(("system", f"🔍 검색 결과:\n{search_results}"))
            with st.chat_message("system"):
                st.markdown(f"🔍 **검색 결과**\n{search_results}")

    # AI 응답 생성
    with st.chat_message("assistant"):
        with st.spinner("Gemini가 답변 중..."):
            try:
                # Gemini가 요구하는 role만 사용
                chat_history = [
                    {"role": "user" if role == "user" else "model", "parts": [msg]}
                    for role, msg in st.session_state.history
                ]
                
                # 검색 결과를 컨텍스트에 포함
                context = f"최신 웹 검색 결과:\n{search_results}\n\n" if search_results else ""
                
                convo = model.start_chat(history=chat_history)
                response = convo.send_message(f"{context}사용자 질문: {user_input}")
                
                # 응답 저장 및 표시
                ai_response = response.text
                st.write(ai_response)
                st.session_state.history.append(("model", ai_response))
                
            except Exception as e:
                error_msg = f"오류 발생: {str(e)}"
                st.error(error_msg)
                st.session_state.history.append(("model", error_msg))
