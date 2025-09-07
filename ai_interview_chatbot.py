import streamlit as st
import requests
import pandas as pd
import os
import re

from auth import show_login_signup


# Load environment variables from .env file
GEMINI_API_KEY = st.secrets["general"]["GEMINI_API_KEY"]


# --- STREAMLIT CONFIG ---
st.set_page_config(
    page_title="AI Interview Chatbot",
    page_icon="image.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

if not show_login_signup():
    st.stop()
# --- LOVABLE, CHATGPT-LIKE DARK THEME & CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700&display=swap');

body, .css-18e3th9 {
    font-family: 'Nunito', sans-serif !important;
    background: linear-gradient(135deg, #0A192F 0%, #1B2A47 100%);
    color: #f0f4f8;
    overflow-x: hidden;
}
body::before {
    content: "";
    position: fixed;
    width: 100vw;
    height: 100vh;
    z-index: -1;
    background:
      radial-gradient(circle at 20% 30%, #6a11cb88 20%, transparent 60%),
      radial-gradient(circle at 80% 70%, #2575fc88 25%, transparent 55%);
    animation: floatingBlobs 20s ease-in-out infinite alternate;
    filter: blur(80px);
    opacity: 0.5;
}
@keyframes floatingBlobs {
    0% { transform: translate(0, 0); }
    100% { transform: translate(30px, -30px); }
}
.container {
    max-width: 860px;
    margin: 2rem auto 5rem;
    padding: 0 1.5rem;
}
.header {
    font-size: 3rem;
    font-weight: 800;
    text-align: center;
    color: #ffffff;
    margin-bottom: 0.25rem;
    letter-spacing: 0.08em;
    text-shadow: 0 2px 15px #6a11cbbb;
}
.subtitle {
    color: #a0aec0;
    font-weight: 500;
    font-size: 1.25rem;
    text-align: center;
    margin-bottom: 3rem;
}
.stButton > button {
    background: linear-gradient(90deg, #6a11cb, #2575fc);
    border-radius: 40px;
    font-weight: 700;
    padding: 15px 48px;
    font-size: 1.3rem;
    color: white;
    box-shadow: 0 6px 25px rgba(101, 45, 255, 0.6);
    transition: all 0.3s ease;
    min-width: 180px;
}
.stButton > button:hover {
    background: linear-gradient(90deg, #2575fc, #6a11cb);
    box-shadow: 0 9px 32px rgba(101, 45, 255, 0.9);
    transform: translateY(-3px);
}
.chat-container {
    background: #12264ccc;
    border-radius: 30px;
    box-shadow: 0 0 45px #5216ff55 inset;
    max-height: 650px;
    overflow-y: auto;
    padding: 2rem 2.5rem;
    margin-bottom: 3rem;
}
.bubble {
    max-width: 85%;
    padding: 18px 28px;
    margin-bottom: 16px;
    border-radius: 24px;
    font-size: 1.1rem;
    font-weight: 600;
    line-height: 1.5;
    position: relative;
    animation: fadeInUp 0.5s ease forwards;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
.bubble.user {
    background: linear-gradient(160deg, #3e70ea, #1b49d4);
    color: white;
    margin-left: auto;
    border-bottom-right-radius: 0;
}
.bubble.ai {
    background: #273661;
    color: #dbeafe;
    margin-right: auto;
    border-bottom-left-radius: 0;
}
.avatar {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    box-shadow: 0 0 8px #6a11cbaa;
}
.avatar.user {
    right: -54px;
    background: url('https://cdn-icons-png.flaticon.com/512/194/194938.png') center/cover no-repeat;
}
.avatar.ai {
    left: -54px;
    background: url('https://cdn-icons-png.flaticon.com/512/4712/4712036.png') center/cover no-repeat;
}
@keyframes fadeInUp {
    0% { opacity: 0; transform: translateY(25px); }
    100% { opacity: 1; transform: translateY(0); }
}
.feedback-section {
    background: #1f2a57cc;
    border-radius: 25px;
    padding: 2.5rem 3rem;
    box-shadow: 0 16px 40px #5c43ff88;
    margin-top: 2rem;
    color: #ebf2ff;
    animation: fadeInUp 0.8s ease forwards;
}
.feedback-header {
    font-size: 2.8rem;
    font-weight: 900;
    text-align: center;
    margin-bottom: 2rem;
    color: #bbe1fa;
    text-shadow: 0 0 18px #5c43ffcc;
}
.feedback-group {
    display: flex;
    flex-wrap: wrap;
    gap: 1.5rem 2.5rem;
    justify-content: center;
}
.feedback-card {
    flex: 1 1 320px;
    background: #273661cc;
    border-radius: 22px;
    padding: 2rem 2.5rem;
    min-height: 220px;
    font-weight: 600;
    font-size: 1.15rem;
    box-shadow: 0 12px 28px #3d52a8aa;
}
.feedback-card h3 {
    color: #aad8ff;
    margin-bottom: 0.8rem;
    font-weight: 800;
    display: flex;
    align-items: center;
}
.feedback-card ul {
    margin-left: 22px;
}
.rating-container {
    margin-top: 3rem;
    text-align: center;
    color: #bbe1fa;
    font-weight: 900;
}
.rating-number {
    font-size: 5rem;
    margin-bottom: 0.5rem;
    text-shadow: 0 0 25px #5c43ffcc;
}
.stars {
    color: #ffd700;
    font-size: 3.2rem;
    filter: drop-shadow(0 0 3px #ffec3744);
}
textarea, .stTextArea textarea {
    font-size: 1.15rem !important;
    padding: 1rem !important;
    border-radius: 20px !important;
    border: 1.7px solid #3a4a7d !important;
    background-color: #192745 !important;
    color: #e0e7ff !important;
    transition: border-color 0.3s ease;
}
textarea:focus, .stTextArea textarea:focus {
    border-color: #5c43ff !important;
    box-shadow: 0 0 18px #5c43ffbb !important;
}
@media (max-width: 720px) {
    .feedback-group {
        flex-direction: column;
        gap: 2rem;
    }
    .feedback-card {
        min-height: auto;
    }
}
</style>
""", unsafe_allow_html=True)


# --- HEADER ---
st.markdown("""
<div class="container">
    <div class="header">🤖 AI Interview Chatbot</div>
    <div class="subtitle">Practice your interview skills with AI-powered personalized feedback</div>
</div>
""", unsafe_allow_html=True)


# --- SESSION STATE ---
if "started" not in st.session_state: st.session_state.started = False
if "finished" not in st.session_state: st.session_state.finished = False
if "question_num" not in st.session_state: st.session_state.question_num = 0
if "user_answers" not in st.session_state: st.session_state.user_answers = []
if "current_question" not in st.session_state: st.session_state.current_question = ""
if "feedback" not in st.session_state: st.session_state.feedback = ""
if "messages" not in st.session_state: st.session_state.messages = []
if "qa_feedback" not in st.session_state: st.session_state.qa_feedback = []


# Role-Domain mapping    
role_domains = {
    "Software Engineer": ["Frontend", "Backend", "ML", "System Design", "DevOps"],
    "Data Scientist": ["ML", "Data Engineering", "Statistics"],
    "Product Manager": ["Agile", "UX", "Market Analysis"],
    "Marketing Specialist": ["SEO", "Content Marketing", "Social Media"],
}


# Inputs (No API Key input - loaded from env)
role = st.selectbox("Choose Role:", list(role_domains.keys()), key="role_sel")
domain = st.selectbox("Choose Domain (optional):", ["None"] + role_domains.get(role, []), key="domain_sel")
level = st.selectbox("Select Level:", ["Junior", "Mid", "Senior"], key="level_sel")
mode = st.selectbox("Interview Mode:", ["Technical Interview", "Behavioral Interview"], key="mode_sel")
num_questions = st.slider("Number of Questions:", 1, 5, 3, key="num_q")


def ask_gemini(prompt, history=[]):
    if not GEMINI_API_KEY:
        return "⚠️ Gemini API key not found. Please set GEMINI_API_KEY in your environment."
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    contents = []
    for sender, msg in history:
        role_label = "user" if sender == "User" else "model"
        contents.append({"role": role_label, "parts": [{"text": msg}]})
    contents.append({"role": "user", "parts": [{"text": prompt}]})
    payload = {"contents": contents}
    try:
        response = requests.post(url, json=payload)
        data = response.json()
        if "candidates" in data and data["candidates"]:
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        elif "error" in data:
            message = data["error"].get("message", "Unknown error")
            return f"⚠️ API Error: {message}"
        else:
            return "⚠️ Unexpected API response format."
    except Exception as e:
        return f"⚠️ Exception: {str(e)}"


# Better rating parsing function
def parse_rating_better(feedback_text):
    """More flexible rating parser."""
    text = feedback_text.lower()
    rating_patterns = [
        r'overall[_ ]rating[: ]+(\d+\.?\d*)\s*/\s*10',
        r'rating[: ]+(\d+\.?\d*)\s*/\s*10',
        r'score[: ]+(\d+\.?\d*)\s*/\s*10',
        r'(\d+\.?\d*)\s*/\s*10'  # fallback catch all
    ]
    for pattern in rating_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                rating = float(match.group(1))
                if 0 <= rating <= 10:
                    return rating
            except:
                pass
    return None


# Pandas dataframe for session tracking    
if "interview_df" not in st.session_state:
    st.session_state.interview_df = pd.DataFrame(columns=["Question", "Answer", "Feedback", "Score"])


# Start interview    
if not st.session_state.started and not st.session_state.finished:
    if st.button("🚀 Start Interview"):
        if not GEMINI_API_KEY:
            st.error("API key not found in environment. Please configure GEMINI_API_KEY properly.")
        else:
            st.session_state.started = True
            st.session_state.question_num = 0
            st.session_state.user_answers = []
            st.session_state.messages = []
            st.session_state.qa_feedback = []
            st.session_state.interview_df = pd.DataFrame(columns=["Question", "Answer", "Feedback", "Score"])

            prompt = f"You are interviewing a candidate for {role}"
            if domain != "None":
                prompt += f" specialized in {domain}"
            prompt += f" at {level} level. Conduct a {mode.lower()}. Ask the first interview question."
            question = ask_gemini(prompt)
            st.session_state.current_question = question
            st.session_state.messages.append(("AI", question))
            st.rerun()


# Interview flow    
if st.session_state.started and not st.session_state.finished:
    st.markdown('<div class="container chat-container">', unsafe_allow_html=True)
    for sender, msg in st.session_state.messages:
        cls = "user" if sender == "User" else "ai"
        st.markdown(f"""
        <div class="bubble {cls}">
            {msg}
            <div class="avatar {cls}"></div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"### Question {st.session_state.question_num + 1} of {num_questions}")
    answer = st.text_area("Your Answer:", height=150, key=f"answer_{st.session_state.question_num}")

    if st.button("➡️ Submit Answer", key=f"submit_{st.session_state.question_num}"):
        if not answer.strip():
            st.warning("Please type your answer before submitting.")
        else:
            st.session_state.user_answers.append({"question": st.session_state.current_question, "answer": answer.strip()})
            st.session_state.messages.append(("User", answer.strip()))

            fb_prompt = f"""
Evaluate this {mode.lower()} interview answer for role {role} at {level} level.
Domain: {domain if domain != 'None' else 'General'}.
Question: {st.session_state.current_question}
Answer: {answer.strip()}
Give concise feedback considering clarity, correctness, completeness, and examples.
Format:
Feedback: ...
Score: X/10
"""
            feedback_resp = ask_gemini(fb_prompt, st.session_state.messages)
            fb_text, fb_score = "", ""
            for line in feedback_resp.splitlines():
                line = line.strip().lower()
                if line.startswith("feedback:"):
                    fb_text = line[len("feedback:"):].strip()
                elif line.startswith("score:"):
                    fb_score = line[len("score:"):].strip().split("/")[0]

            st.session_state.qa_feedback.append({'text': fb_text, 'score': fb_score})

            new_row = {
                "Question": st.session_state.current_question,
                "Answer": answer.strip(),
                "Feedback": fb_text,
                "Score": fb_score
            }
            st.session_state.interview_df = pd.concat([st.session_state.interview_df, pd.DataFrame([new_row])], ignore_index=True)

            st.session_state.question_num += 1

            if st.session_state.question_num >= num_questions:
                history_text = "\n".join([f"Q: {qa['question']}\nA: {qa['answer']}" for qa in st.session_state.user_answers])
                final_prompt = f"""
You are a senior interviewer analyzing a {mode.lower()} interview for role {role} at {level} level.
Domain: {domain if domain != 'None' else 'General'}.
Here are the Q&A:
{history_text}
Please provide a final summary with STRENGTHS, WEAKNESSES, SUGGESTIONS, and OVERALL_RATING (out of 10).
Format:
STRENGTHS:
- ...
WEAKNESSES:
- ...
SUGGESTIONS:
- ...
OVERALL_RATING: X/10
"""
                summary = ask_gemini(final_prompt, st.session_state.messages)
                st.session_state.feedback = summary
                st.session_state.finished = True
                st.session_state.started = False
                st.rerun()
            else:
                next_prompt = f"""
You are interviewing for a {role} at {level} level, domain {domain if domain != 'None' else 'general'}, conducting a {mode.lower()}.
The candidate's last answer was: "{answer.strip()}"
Ask the next relevant {mode.lower()} interview question.
Question {st.session_state.question_num + 1} of {num_questions}.
"""
                next_question = ask_gemini(next_prompt, st.session_state.messages)
                st.session_state.current_question = next_question
                st.session_state.messages.append(("AI", next_question))
                st.rerun()


# Show per-answer feedback during interview
if st.session_state.started and st.session_state.qa_feedback:
    for i, fb in enumerate(st.session_state.qa_feedback):
        st.success(f"Feedback for Answer {i+1}: {fb['text']}")
        st.info(f"Score: {fb['score']}/10")
        st.markdown("---")


# --- Show final feedback ---
def clean_md(text):
    # Remove Markdown bold (**text**), italic (*text*), underline or other markdown
    text = re.sub(r'\*\*', '', text)  # Remove **
    text = re.sub(r'\*', '', text)     # Remove *
    text = re.sub(r'__', '', text)
    text = re.sub(r'_', '', text)
    return text.strip()

def feedback_list_html(items):
    if not items:
        return "<p>None provided.</p>"
    cleaned_items = [clean_md(i) for i in items]
    list_items = "".join(f"<li>{i}</li>" for i in cleaned_items)
    return f"<ul style='margin-left:1.2rem; margin-top:0.3rem;'>{list_items}</ul>"

if st.session_state.finished and st.session_state.feedback:
    st.markdown('<div class="container feedback-section">', unsafe_allow_html=True)
    st.markdown('<div class="feedback-header">📋 Interview Feedback Report</div>', unsafe_allow_html=True)

    lines = st.session_state.feedback.splitlines()
    strengths, weaknesses, suggestions = [], [], []
    section = None

    for line in lines:
        line_strip = line.strip()
        if line_strip.upper().startswith("STRENGTHS:"):
            section = "strengths"
            continue
        elif line_strip.upper().startswith("WEAKNESSES:"):
            section = "weaknesses"
            continue
        elif line_strip.upper().startswith("SUGGESTIONS:"):
            section = "suggestions"
            continue
        elif line_strip.upper().startswith("OVERALL_RATING:"):
            section = None
            continue

        if section == "strengths" and line_strip:
            strengths.append(line_strip.lstrip("-•123456789. ").strip())
        elif section == "weaknesses" and line_strip:
            weaknesses.append(line_strip.lstrip("-•123456789. ").strip())
        elif section == "suggestions" and line_strip:
            suggestions.append(line_strip.lstrip("-•123456789. ").strip())

    strengths_html = feedback_list_html(strengths)
    weaknesses_html = feedback_list_html(weaknesses)
    suggestions_html = feedback_list_html(suggestions)

    overall_rating = parse_rating_better(st.session_state.feedback)

    summary_html = f"""
    <div style='
        font-family: Nunito, -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 1.1rem;
        line-height: 1.6;
        color: #f8fafc;
        padding: 2rem 2.5rem;
        background: rgba(30, 41, 70, 0.95);
        border-radius: 16px;
        border: 1px solid rgba(148, 163, 184, 0.2);
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    '>
        <div style='
            font-size: 1.4rem; 
            font-weight: 700; 
            color: #e2e8f0; 
            margin-bottom: 1.5rem;
            border-bottom: 1px solid rgba(148, 163, 184, 0.3);
            padding-bottom: 0.75rem;
            display: flex;
            align-items: center;
        '>
            📋 &nbsp;&nbsp;Interview Performance Summary
        </div>
        <div style='margin-bottom: 1.2rem;'>
            <strong>Position:</strong> {role} ({domain if domain != "None" else "General"}) at <strong>{level}</strong> level
            <br>
            <strong>Interview Type:</strong> {mode} with {num_questions} questions assessed
        </div>
        <div style='margin-bottom: 1.2rem;'>
            <strong>Key Strengths:</strong><br>
            {strengths_html}
        </div>
        <div style='margin-bottom: 1.2rem;'>
            <strong>Areas for Development:</strong><br>
            {weaknesses_html}
        </div>
        <div style='margin-bottom: 1.5rem;'>
            <strong>Recommendations:</strong><br>
            {suggestions_html}
        </div>
        <div style='
            border-top: 1px solid rgba(148, 163, 184, 0.3);
            padding-top: 1rem;
            font-size: 1.15rem;
        '>
            <strong>Overall Performance Rating:</strong> 
            <span style='font-weight: 800; font-size: 1.3rem;'>
                {f"{overall_rating:.1f}/10.0" if overall_rating is not None else "Pending Evaluation"}
            </span>
        </div>
    </div>
    """

    st.markdown(summary_html, unsafe_allow_html=True)

    

    if overall_rating is not None:
        full_stars = int(overall_rating)
        half_star = overall_rating - full_stars >= 0.5
        empty_stars = 10 - full_stars - (1 if half_star else 0)
        stars_html = "★" * full_stars + ("⯪" if half_star else "") + "☆" * empty_stars

        st.markdown(f"""
        <div class="rating-container">
            <div class="stars">{stars_html}</div>
            <div class="rating-number">{overall_rating:.1f} / 10</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📊 Interview Summary Data")

    df = st.session_state.interview_df.copy()
    if not df.empty:
        st.dataframe(df, use_container_width=True, height=(40 * len(df) + 50))

        with st.expander("📂 View Interview Session JSON"):
            json_str = df.to_json(orient="records", indent=2)
            st.code(json_str, language="json")

    if st.button("🔄 Restart Interview"):
        for key in [
            "started", "finished", "question_num", "user_answers", "current_question",
            "feedback", "messages", "qa_feedback", "interview_df"
        ]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
