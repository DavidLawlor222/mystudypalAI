import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load your API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 🎨 Page setup
st.set_page_config(
    page_title="MyStudyPal — Ireland",
    page_icon="📘",
    layout="centered",
)

# 🧭 App Header
st.title("📘 MyStudyPal — Ireland")
st.write("Generate Irish-exam-focused notes, quizzes, and flashcards.")

# 🧩 Inputs
cycle = st.selectbox("Cycle", ["Junior Cycle", "Leaving Certificate"])
level = st.selectbox("Level", ["Ordinary Level", "Higher Level"])
subject = st.selectbox("Subject", [
    "English", "Irish", "Maths", "Biology", "Chemistry", "Physics", "Geography", "History"
])
topic = st.text_input("Topic", placeholder="e.g. Photosynthesis")

# ✍️ Generate Notes
if st.button("📝 Generate Notes"):
    if topic.strip():
        with st.spinner("✍️ Creating your notes..."):
            prompt = f"""
            You are an expert Irish secondary school teacher. 
            Create clear, exam-focused notes for the following:
            Cycle: {cycle}
            Level: {level}
            Subject: {subject}
            Topic: {topic}
            Format it in short, clear bullet points.
            """
            response = client.responses.create(
                model="gpt-4.1-mini",
                input=prompt,
                temperature=0.4,
            )
            notes = response.output_text
            st.session_state["notes"] = notes
            st.subheader("🧠 Your Study Notes")
            st.markdown(notes)
    else:
        st.warning("Please enter a topic before generating notes!")

# 🧩 Generate Quiz
if "notes" in st.session_state:
    if st.button("🧠 Make Quiz from Notes"):
        with st.spinner("🧠 Creating quiz questions..."):
            quiz_prompt = f"""
            Based on these notes, create 5 multiple-choice quiz questions.
            Provide 4 answer options for each (A-D), and mark the correct one.
            Notes:
            {st.session_state['notes']}
            """
            quiz_resp = client.responses.create(
                model="gpt-4.1-mini",
                input=quiz_prompt,
                temperature=0.4,
            )
            quiz_text = quiz_resp.output_text
            st.subheader("🧠 Quiz Questions")
            st.markdown(quiz_text)
else:
    st.button("🧠 Make Quiz from Notes", disabled=True)
