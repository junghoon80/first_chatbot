import streamlit as st
import google.generativeai as genai
import requests
import datetime

# 비밀키 불러오기
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
GOOGLE_CSE_ID = st.secrets["GOOGLE_CSE_ID"]

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

def google_search(query, api_key, cse_id, num=3):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cse_id,
        "q": query,
        "num": num,
        "hl": "ko"
    }
    response = requests.get(url, params=params)
    data = response.json()
    if "items" not in data:
        return "검색 결과가 없습니다."
    results = []
    for item in data["items"]:
        title = item.get("title")
        link = item.get("link")
        snippet = item.get("snippet")
        results.append(f"제목: {title}\nURL: {link}\n요약: {snippet}")
    return "\n\n".join(results)

if "history" not in st.session_state:
    st.session_state.history = []
if "web_search_enabled" not in st.session_state:
    st.session_state.web_search_enabled = True

with st.sidebar:
    st.header("웹 검색 설정")
    st.session_state.web_search_enabled = st.checkbox("웹 검색 활성화", value=True)
    num_results = st.slider("검색 결과 수", 1, 5, 3)
    if st.button("대화 기록 초기화"):
        st.session_state.history = []

# 오늘 날짜 정보
current_date = datetime.date.today().strftime("%Y년 %m월 %d일")

st.title(f"🔎 Google Custom Search + Gemini 2.5 Flash 챗봇 ({current_date})")

# 대화 기록 표시
for role, msg in st.session_state.history:
    with st.chat_message("user" if role == "user" else "assistant"):
        st.write(msg)

user_input = st.chat_input("질문을 입력하세요...")
if user_input:
    st.session_state.history.append(("user", user_input))
    with st.chat_message("user"):
        st.write(user_input)

    search_results = ""
    if st.session_state.web_search_enabled:
        with st.spinner("Google에서 검색 중..."):
            search_results = google_search(
                user_input, GOOGLE_API_KEY, GOOGLE_CSE_ID, num=num_results
            )
            st.session_state.history.append(("system", f"🔍 검색 결과:\n{search_results}"))
            with st.chat_message("system"):
                st.markdown(f"🔍 **검색 결과**\n{search_results}")

    with st.chat_message("assistant"):
        with st.spinner("Gemini가 답변 중..."):
            try:
                chat_history = [
                    {"role": "user" if role == "user" else "model", "parts": [msg]}
                    for role, msg in st.session_state.history
                ]
                # 오늘 날짜와 검색 결과를 컨텍스트에 포함
                context = f"오늘 날짜는 {current_date}입니다.\n"
                if search_results:
                    context += f"최신 웹 검색 결과:\n{search_results}\n\n"
                convo = model.start_chat(history=chat_history)
                response = convo.send_message(f"{context}사용자 질문: {user_input}")
                ai_response = response.text
                st.write(ai_response)
                st.session_state.history.append(("model", ai_response))
            except Exception as e:
                error_msg = f"오류 발생: {str(e)}"
                st.error(error_msg)
                st.session_state.history.append(("model", error_msg))
