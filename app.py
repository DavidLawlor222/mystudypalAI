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

# 📄 Use Irish Past Papers (Optional)
st.subheader("📄 Use Irish Past Papers (Optional)")

folder_path = "/Users/davidlawlor/Documents/Past Exams/Maths"
pdf_files = list_papers(folder_path)

if pdf_files:
    selected_pdf = st.selectbox("Choose a past paper", pdf_files)
    if st.button("📘 Summarise this Paper"):
        with st.spinner("Reading and summarising..."):
            pdf_text = read_pdf(selected_pdf)
            prompt = f"""
            You are an Irish maths teacher. Summarise key topics, question types,
            and exam trends found in this past paper. Focus on marking scheme expectations
            and tips for Leaving/Junior Cert students.
            Content:
            {pdf_text[:8000]}  # limit to avoid hitting token limits
            """
            response = client.responses.create(
                model="gpt-4.1-mini",
                input=prompt,
                temperature=0.4,
            )
            summary = response.output_text
            st.subheader("📘 Paper Summary")
            st.markdown(summary)
else:
    st.info("No PDF files found in your Maths folder. Add some to /Users/davidlawlor/Documents/Past Exams/Maths")


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

