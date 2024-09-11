import streamlit as st
from openai import OpenAI
import json
from dotenv import load_dotenv
import os
import time

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Set page configuration
st.set_page_config(
    page_title="맞춤형 학습 자료 생성기",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem !important;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem !important;
        color: #43A047;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1E88E5;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# Main header
st.markdown("<h1 class='main-header'>🎓 맞춤형 학습 자료 생성기</h1>", unsafe_allow_html=True)

# Introduction
with st.expander("ℹ️ 사용 방법", expanded=True):
    st.markdown("""
    1. 학습하고 싶은 과목을 선택하세요.
    2. 학습 자료의 난이도를 설정하세요.
    3. 배우고 싶은 구체적인 주제를 입력하세요.
    4. '학습 자료 생성하기' 버튼을 클릭하세요.
    5. AI가 맞춤형 학습 자료를 생성할 때까지 잠시 기다려주세요.
    """)

# Input section
st.markdown("<h2 class='sub-header'>📚 학습 정보 입력</h2>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    subject = st.selectbox(
        "과목 선택",
        ["수학", "영어", "국어", "생명과학", "지구과학"],
        help="학습하고 싶은 과목을 선택해주세요."
    )

with col2:
    difficulty = st.select_slider(
        "난이도 설정",
        options=["초급", "중급", "고급"],
        value="중급",
        help="학습 자료의 난이도를 선택해주세요."
    )

lesson = st.text_input(
    f'{subject} 과목의 어떤 주제에 대해 배우고 싶으신가요?',
    help="예: 수학의 미분, 영어의 관계대명사 등"
)

# Example response structure
example_response = {
    "title": "제목",
    "introduction": "소개",
    "main_content": ["주요 내용 1", "주요 내용 2", "주요 내용 3"],
    "examples": ["예시 1", "예시 2"],
    "practice_questions": ["연습 문제 1", "연습 문제 2", "연습 문제 3"]
}

# Generate learning material
if st.button("🚀 학습 자료 생성하기"):
    if not lesson:
        st.error("❗ 주제를 입력해주세요!")
    else:
        with st.spinner("🧠 맞춤형 학습 자료를 생성 중입니다..."):
            # First chatbot: Determine required information
            info_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 교육 전문가입니다. 학습 자료 생성에 필요한 정보를 결정해주세요."},
                    {"role": "user", "content": f"{subject} 과목의 '{lesson}' 주제에 대한 {difficulty} 수준의 학습 자료를 만들기 위해 필요한 정보는 무엇인가요?"}
                ]
            )
            required_info = info_response.choices[0].message.content

            # Second chatbot: Generate learning material (JSON mode)
            if required_info:
                learning_response = client.chat.completions.create(
                    model="gpt-3.5-turbo-1106",
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": "당신은 우수한 교사입니다. 학생들이 이해하기 쉽게 설명하고, 적절한 연습 문제를 제공해주세요. JSON 형식으로 응답해주세요."},
                        {"role": "user", "content": f"{subject} 과목의 '{lesson}' 주제에 대한 {difficulty} 수준의 학습 자료를 만들어주세요. 다음 정보를 포함해야 합니다: {required_info}. 응답은 'title', 'introduction', 'main_content' (리스트 형식), 'examples' (리스트 형식), 'practice_questions' (리스트 형식)을 포함해야 합니다. \n 응답은 위에 제시된 요소들을 포함하는 JSON 형식으로 응답해주세요. 예시 응답 형태는 다음과 같습니다: \n {example_response}"}
                    ]
                )
                learning_material = json.loads(learning_response.choices[0].message.content)

                st.success("🎉 학습 자료가 생성되었습니다!")
                
                # Display learning material
                st.markdown(f"<h2 class='sub-header'>📘 {learning_material['title']}</h2>", unsafe_allow_html=True)
                
                with st.expander("소개", expanded=True):
                    st.markdown(learning_material['introduction'])
                
                with st.expander("주요 내용", expanded=True):
                    for i, content in enumerate(learning_material['main_content'], 1):
                        st.markdown(f"**{i}.** {content}")
                
                with st.expander("예시", expanded=True):
                    for i, example in enumerate(learning_material['examples'], 1):
                        st.markdown(f"**예시 {i}:** {example}")
                
                with st.expander("연습 문제", expanded=True):
                    for i, question in enumerate(learning_material['practice_questions'], 1):
                        st.markdown(f"**문제 {i}:** {question}")
                        # Add a text input for the user to answer the question
                        user_answer = st.text_input(f"답변 {i}", key=f"answer_{i}")
                        if user_answer:
                            st.info("답변이 제출되었습니다. 실제 답안 확인은 추후 기능으로 추가될 예정입니다.")

# Sidebar
st.sidebar.image("https://www.example.com/logo.png", use_column_width=True)  # Replace with actual logo URL
st.sidebar.header("💡 학습 팁")
st.sidebar.info(
    "1. 규칙적인 학습 시간을 정하세요.\n"
    "2. 적극적으로 질문하세요.\n"
    "3. 복습은 학습의 핵심입니다.\n"
    "4. 실생활과 연관 지어 생각해보세요.\n"
    "5. 꾸준히 노력하면 반드시 성과가 있습니다!"
)

# Progress tracking
st.sidebar.markdown("---")
st.sidebar.subheader("📊 학습 진행도")
progress = st.sidebar.progress(0)
study_time = st.sidebar.empty()

# Initialize session state for study time
if 'total_study_time' not in st.session_state:
    st.session_state.total_study_time = 0

# Simulated study timer
if 'study_in_progress' not in st.session_state:
    st.session_state.study_in_progress = False

col1, col2 = st.sidebar.columns(2)

if col1.button("학습 시작" if not st.session_state.study_in_progress else "학습 재개"):
    st.session_state.study_in_progress = True
    start_time = time.time()
    
    while st.session_state.study_in_progress:
        elapsed_time = int(time.time() - start_time)
        progress.progress(min(elapsed_time, 100))
        study_time.text(f"현재 학습 시간: {elapsed_time} 초")
        st.session_state.total_study_time += 1
        time.sleep(1)

if col2.button("학습 중단"):
    st.session_state.study_in_progress = False

st.sidebar.markdown("---")
st.sidebar.markdown(f"총 학습 시간: {st.session_state.total_study_time} 초")
st.sidebar.markdown("열심히 공부하고 있어요! 💪")

# Feedback section
st.sidebar.markdown("---")
st.sidebar.subheader("📝 피드백")
feedback = st.sidebar.text_area("학습 경험에 대한 의견을 들려주세요:")
if st.sidebar.button("피드백 제출"):
    st.sidebar.success("피드백이 제출되었습니다. 감사합니다!")

# Footer
st.markdown("---")
st.markdown("© 2024 맞춤형 학습 자료 생성기 | 문의: gangj277@gmail.com")
