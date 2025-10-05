import streamlit as st
import os
import glob
from io import BytesIO
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader

# -----------------------------
# API KEY (works on Cloud + local)
# -----------------------------
load_dotenv()  # lets local runs read .env, harmless on Cloud

api_key = None
try:
    # Streamlit Cloud secrets (Settings → Secrets)
    api_key = st.secrets["OPENAI_API_KEY"]
except Exception:
    pass
if not api_key:
    # Local fallback
    api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error(
        "OPENAI_API_KEY is missing.\n\n"
        "• On Streamlit Cloud: Settings → Secrets → `OPENAI_API_KEY=\"sk-...\"`\n"
        "• Locally: create a `.env` with `OPENAI_API_KEY=sk-...`"
    )
    st.stop()

client = OpenAI(api_key=api_key)

# -----------------------------
# Helpers for PDFs
# -----------------------------
def read_pdf_from_filelike(fileobj: BytesIO) -> str:
    """Read text from an uploaded PDF file."""
    reader = PdfReader(fileobj)
    pages = [p.extract_text() or "" for p in reader.pages]
    return "\n".join(pages)

def read_pdf_from_path(path: str) -> str:
    """Read text from a PDF on disk (useful when running locally)."""
    with open(path, "rb") as f:
        return read_pdf_from_filelike(f)

def list_pdfs_in_folder(folder_path: str):
    """List full paths to PDFs in a local folder (for local runs only)."""
    if not os.path.exists(folder_path):
        return []
    return glob.glob(os.path.join(folder_path, "*.pdf"))

# -----------------------------
# UI
# -----------------------------
st.set_page_config(page_title="MyStudyPal — Ireland", page_icon="📘", layout="centered")
st.title("📘 MyStudyPal — Ireland")
st.write("Generate **Irish-exam-focused** notes, quizzes, and (optionally) summaries of your own past papers.")

# Inputs
cycle = st.selectbox("Cycle", ["Junior Cycle", "Leaving Certificate"])
level = st.selectbox("Level", ["Ordinary Level", "Higher Level"])
subject = st.selectbox(
    "Subject",
    ["Maths", "English", "Irish", "Biology", "Chemistry", "Physics", "Geography", "History"],
)
topic = st.text_input("Topic", placeholder="e.g. Photosynthesis, Macbeth, Algebra")

st.divider()

# -----------------------------
# Notes generator
# -----------------------------
if st.button("📝 Generate Notes"):
    if topic.strip():
        with st.spinner("✍️ Creating examiner-style notes..."):
            prompt = f"""
You are an experienced Irish secondary school teacher producing SEC-style notes.

Cycle: {cycle}
Level: {level}
Subject: {subject}
Topic: {topic}

Write concise, exam-focused bullet points with:
- key definitions / formulae (if relevant)
- step-by-step explanations
- common mistakes and how to avoid them
- what examiners look for to award full marks
- 4 sample exam questions with brief marking-scheme points
"""
            resp = client.responses.create(
                model="gpt-4.1-mini",
                input=prompt,
                temperature=0.4,
            )
            notes = resp.output_text
            st.session_state["notes"] = notes
            st.subheader("🧠 Your Study Notes")
            st.markdown(notes)
    else:
        st.warning("Please enter a topic before generating notes.")

# -----------------------------
# Quiz generator (from notes)
# -----------------------------
if "notes" in st.session_state:
    if st.button("🧠 Make Quiz from Notes"):
        with st.spinner("🧩 Creating exam-style MCQs..."):
            quiz_prompt = f"""
Create 5 Irish-exam-style multiple choice questions (A–D) based on these notes.
Mark the correct answer after each question.

Notes:
{st.session_state['notes']}
"""
            qresp = client.responses.create(
                model="gpt-4.1-mini",
                input=quiz_prompt,
                temperature=0.4,
            )
            st.subheader("🧠 Quiz Questions")
            st.markdown(qresp.output_text)
else:
    st.button("🧠 Make Quiz from Notes", disabled=True)

st.divider()

# -----------------------------
# Past Paper Summaries
# -----------------------------
st.subheader("📄 Use Irish Past Papers (Optional)")

st.caption(
    "Upload **your own** PDFs (past papers, your notes, examiner reports). "
    "Files are read temporarily for this session only."
)

# A) Upload PDFs (works on Streamlit Cloud and locally)
uploaded_files = st.file_uploader(
    "Upload one or more PDFs", type=["pdf"], accept_multiple_files=True
)

# B) (Optional) Local folder (for your Mac only; ignored on Cloud)
LOCAL_MATHS_FOLDER = "/Users/davidlawlor/Documents/Past Exams/Maths"
local_pdfs = list_pdfs_in_folder(LOCAL_MATHS_FOLDER)

chosen_source = st.radio(
    "Choose source",
    ["Uploaded PDFs", "Local Maths folder (Mac only)"],
    index=0 if uploaded_files else 1 if local_pdfs else 0,
    help="Cloud apps can only use 'Uploaded PDFs'. The local folder works when running on your Mac.",
)

paper_texts = []
paper_labels = []

if chosen_source == "Uploaded PDFs" and uploaded_files:
    for f in uploaded_files:
        try:
            text = read_pdf_from_filelike(f)
            paper_texts.append(text)
            paper_labels.append(f.name)
        except Exception as e:
            st.warning(f"Could not read {f.name}: {e}")

elif chosen_source == "Local Maths folder (Mac only)" and local_pdfs:
    st.caption(f"Reading local PDFs from: {LOCAL_MATHS_FOLDER}")
    for path in local_pdfs:
        try:
            text = read_pdf_from_path(path)
            paper_texts.append(text)
            paper_labels.append(os.path.basename(path))
        except Exception as e:
            st.warning(f"Could not read {os.path.basename(path)}: {e}")

if paper_texts:
    label = st.selectbox("Choose a paper to summarise", paper_labels)
    idx = paper_labels.index(label)

    if st.button("📘 Summarise this Paper"):
        with st.spinner("Summarising paper with SEC-style focus..."):
            content = paper_texts[idx][:8000]  # keep within token limits
            sprompt = f"""
You are an Irish {subject} teacher preparing students for the {cycle} {level} exam.

Summarise this past paper with:
- key topics and learning outcomes examined
- typical question styles and difficulty
- marking-scheme expectations
- common pitfalls
- targeted revision checklist for students

Paper content:
{content}
"""
            sresp = client.responses.create(
                model="gpt-4.1-mini",
                input=sprompt,
                temperature=0.3,
            )
            st.subheader("📘 Paper Summary")
            st.markdown(sresp.output_text)
elif chosen_source == "Uploaded PDFs":
    st.info("Upload one or more PDFs above to enable summarising.")
elif chosen_source == "Local Maths folder (Mac only)":
    st.info(f"No PDFs found in {LOCAL_MATHS_FOLDER}.")

