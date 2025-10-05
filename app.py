import streamlit as st

st.set_page_config(page_title="Hello Streamlit")
st.title("👋 Hello from Streamlit")
st.write("If you can see this, Streamlit is working fine.")
import streamlit as st
import os
from openai import OpenAI

# Page setup
st.set_page_config(page_title="MyStudyPal", page_icon="📘", layout="centered")

# Title
st.title("📘 MyStudyPal.ie – Your AI Study Buddy")

# Sidebar for settings
st.sidebar.header("Study Settings")
cycle = st.sidebar.selectbox("Select Cycle", ["Junior Cert", "Leaving Cert"])
level = st.sidebar.selectbox("Select Level", ["Higher", "Ordinary"])
subject = st.sidebar.selectbox("Select Subject", ["English", "Irish", "Maths", "Biology", "Geography", "History"])
topic = st.sidebar.text_input("Enter Topic", "Photosynthesis")

# Load API key from secrets
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    st.error("OpenAI API key not found. Please add it in Streamlit Secrets.")
else:
    client = OpenAI(api_key=api_key)

# Main content
st.subheader(f"Generate study content for {topic}")

col1, col2 = st.columns(2)
with col1:
    generate_notes = st.button("📝 Generate Notes")
with col2:
    generate_quiz = st.button("❓ Generate Quiz")

if generate_notes and topic:
    with st.spinner("Creating notes..."):
        prompt = f"Create exam-focused revision notes for {cycle} {level} {subject} on the topic '{topic}', tailored to Irish exams."
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        st.markdown(response.choices[0].message.content)

if generate_quiz and topic:
    with st.spinner("Generating quiz..."):
        prompt = f"Create 5 exam-style questions with answers for {cycle} {level} {subject} on '{topic}', following Irish exam format."
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        st.markdown(response.choices[0].message.content)
