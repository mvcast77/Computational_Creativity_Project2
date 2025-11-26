import streamlit as st
import json
import os
import requests
from datetime import datetime

# -------------------------
# 1. User uploads/inputs story idea
# -------------------------

st.set_page_config(page_title="Story Outline Builder", page_icon="📝", layout="wide")
st.title("📝 Story Outline Builder")
st.write("Generate and edit story outlines using an LLM (Claude or OpenAI).")

st.subheader("1. Describe Your Story Idea in the Text Box Below or Upload it")
story_idea = st.text_area(
    "Enter the premise or partial story description:",
    placeholder="Example: A young botanist discovers a glowing plant in the forest...",
    height=120
)

uploaded_file = st.file_uploader(
    "Upload a PDF, TXT, or DOCX file: ",
    type=["pdf", "txt", "docx"]
)

file_text = ""

if uploaded_file is not None:
    st.success(f"Uploaded: {uploaded_file.name}")

    # Read file based on type
    if uploaded_file.type == "text/plain":
        file_text = uploaded_file.read().decode("utf-8")

    elif uploaded_file.type == "application/pdf":
        import PyPDF2
        reader = PyPDF2.PdfReader(uploaded_file)
        file_text = "\n".join([page.extract_text() for page in reader.pages])

    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        import docx
        doc = docx.Document(uploaded_file)
        file_text = "\n".join([p.text for p in doc.paragraphs])

    st.text_area("Extracted Document Text:", value=file_text, height=200)

# -------------------------
# 2. Connect to LLM API to make the og outline
# -------------------------
 
api_key = "" #API KEY GOES HERE
model = "" #MODEL NAME GOES HERE
st.info(f"Using model: {model} (best free option for creative writing).")

# -------------------------
# 3. Function: Call LLM
# -------------------------

def call_llm(prompt):
    response = requests.get("http://0.0.0.0:8000/api/v1/methods/receive_result")
    print("Received: ")
    print(response.text)
    data = response.json()
    return data["new_text"]
    # print("THE FUNCTION THAT CALLS THE LLM GOES HERE!")


# -------------------------
# 4. Generate Visual Outline Only
# -------------------------

st.subheader("3. Generate Story Outline")

if st.button("Generate Story Outline"):
    if not story_idea and not file_text:
        st.error("Please enter a story idea or upload a document.")
    else:
        combined_text = story_idea + "\n\n" + file_text

        prompt = f"""Does this work"""
        """
            Create a clear, detailed, visual story outline based on the following material:

            {combined_text}

            Your outline must follow this format:

            ### 📚 Visual Outline
            - Act I
            - Setup
                - Key beat 1
                - Key beat 2
            - Act II
            - Rising Action
                - Key beat 1
                - Key beat 2
            - Act III
            - Climax & Resolution
                - Key beat 1
                - Key beat 2

            Guidelines:
            - Use hierarchical bullet formatting.
            - Do NOT include a summary or explanations.
            - Keep the outline tight and structured like a screenplay or novel planner.
            - Focus purely on plot beats and story flow.
            """

        with st.spinner("Generating outline..."):
            result = call_llm(prompt)

        st.subheader("📘 Generated Story Outline")
        st.markdown(result)
