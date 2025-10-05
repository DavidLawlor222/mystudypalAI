import streamlit as st
import os
import glob
from openai import OpenAI
from dotenv import load_dotenv
from pypdf import PdfReader

# --- Setup ---
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Helper Functions ---
def read_pdf(file_path):
    """Extracts text from a PDF file"""
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def list_papers(folder_path):
    """Lists all PDFs in a folder"""
    pdfs = glob.glob(f"{folder_path}/*.pdf")
    return pdfs

# --- Page Config ---
st.set_page_config(
    page_title="MyStudyPal — Ireland",
    page_icon="📘",
    layout="centered",
)

st.title("📘 MyStudyPal — Ireland")
st.write("Generate Irish-exam-focused notes, quizzes, and past paper summaries.")

# --- Inputs ---
cycle = st.selectbox("Cycle", ["Junior Cycle", "Leaving Certificate"])
level = st.selectbox("Level", ["Ordinary Level", "Higher Level"])
subject = st.selectbox(
    "Subject",
    ["Maths", "English", "Irish", "Biology", "Chemistry", "Physics", "Geography", "History"]
)
topic = st.text_input("Topic", placeholder="e.g. Photosynthesis, Macbeth, Algebra")

# --- Generate Notes ---
if st.button("📝 Generate Notes"):
    if topic.strip():
        with st.spinner("✍️ Creating your notes..."):
            prompt = f"""
            You are an experienced Irish secondary school teacher.
            Write detailed, exam-focused notes for:

            Cycle: {cycle}
            Level: {level}
            Subject: {subject}
            Topic: {topic}

            Focus on Irish curriculum points, marking schemes,
            and exam technique tips. Use clear bullet points.
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

# --- Generate Quiz ---
if "notes" in st.session_state:
    if st.button("🧠 Make Quiz from Notes"):
        with st.spinner("🧠 Creating quiz questions..."):
            quiz_prompt = f"""
            Based on these notes, create 5 Irish-exam-style quiz questions.
            Each question should include 4 multiple choice options (A-D)
            and mark the correct answer.

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

# --- Past Paper Summariser ---
st.divider()
st.subheader("📄 Use Irish Past Papers (Optional)")

# 📁 Folder path to your Maths papers
folder_path = "/Users/davidlawlor/Documents/Past Exams/Maths"

# 🧭 Find all PDFs
pdf_files = list_papers(folder_path)
st.write("Found files:", pdf_files)  # debug helper

if pdf_files:
    selected_pdf = st.selectbox("Choose a past paper", pdf_files)
    if st.button("📘 Summarise this Paper"):
        with st.spinner("📄 Reading and summarising your paper..."):
            pdf_text = read_pdf(selected_pdf)
            prompt = f"""
            You are an Irish maths teacher preparing students for the
            {cycle} {level} {subject} exam.
            
            Summarise the key topics, question types, marking scheme focus,
            and exam trends found in this past paper.
            
            Provide short bullet-point notes on what to revise and how to approach similar questions.
            
            Paper Content:
            {pdf_text[:8000]}  # limit tokens
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
    st.info("No PDF files found. Add Maths papers to /Users/davidlawlor/Documents/Past Exams/Maths")
