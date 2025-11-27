import streamlit as st
import json
import os
import requests
from datetime import datetime

# -------------------------
# 1. User uploads/inputs story idea
# -------------------------

st.set_page_config(page_title="Story Outline Builder", page_icon="📝", layout="wide")

# Button styling: make generate button blue and readable
st.markdown(
    """
    <style>
    .stButton>button {
        background-color: #B57170 !important;
        color: #ffffff !important;
        border-radius: 6px !important;
        padding: 6px 12px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


st.title("📝 Story Outline Builder")
st.write("Generate and edit story outlines using an LLM (Claude or OpenAI).")

# -----------------------------------------------------
# TOP CONTROL BAR
# -----------------------------------------------------

top_col1, top_col2, top_col3 = st.columns([3, 2, 2])

with top_col1:
    uploaded_file = st.file_uploader(
        "Upload PDF / TXT / DOCX",
        type=["pdf", "txt", "docx"]
    )

with top_col2:
    model = st.selectbox(
        "Choose LLM Model",
        ["local-test-server"],
        index=0
    )

with top_col3:
    # (button moved below the story text area)
    st.write("")


# -----------------------------------------------------
# FILE PROCESSING
# -----------------------------------------------------

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

    # st.text_area("Extracted Document Text:", value=file_text, height=200)


# -----------------------------------------------------
# LAYOUT: OUTLINE LEFT, STORY RIGHT
# -----------------------------------------------------
left_col, right_col = st.columns([1.2, 1])

with right_col:
    st.subheader("✏️ Story Text / Premise")
    story_idea = st.text_area(
        "Enter story idea:",
        placeholder="Example: A young botanist discovers a glowing plant...",
        height=320
    )

    # Generate button placed under the story text area (right column)
    generate_button = st.button("Generate Story Outline", use_container_width=True, key="generate_button")
    # Add vertical spacer so the prompt area sits lower on the page
    # This helps align the prompt button closer to the bottom of the outline box
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # Subheader and textbox for prompt to edit outline
    st.subheader("⚡ Spice up the outline!")
    prompt_edit_outline = st.text_area(
        "Type here to edit outline:",
        placeholder="E.g. Add a twist in Act II, make the ending more hopeful...",
        height=100,
        key="prompt_edit_outline"
    )

    # Prompt button placed under the prompt text area (right column)
    prompt_button = st.button("Prompt the model", use_container_width=True, key="prompt_button")

# Outline box placeholder — will update dynamically
if "generated_outline" not in st.session_state:
    st.session_state["generated_outline"] = ""


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
    response = requests.get("http://127.0.0.1:8000/api/v1/methods/receive_result")
    print("Received: ")
    print(response.text)
    data = response.json()
    return data["new_text"]
    # print("THE FUNCTION THAT CALLS THE LLM GOES HERE!")


# -------------------------
# 4. Generate Visual Outline Only
# -------------------------

if generate_button:
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

        st.session_state["generated_outline"] = result

# -----------------------------------------------------
# OUTLINE
# -----------------------------------------------------
with left_col:
    st.subheader("📚 Visual Outline")

    # Convert outline to list of lines
    outline_lines = [
        line for line in st.session_state["generated_outline"].split("\n") if line.strip()
    ]

    if outline_lines:
        # Limit height and add scroll bar to the entire outline box
        st.markdown(
            """
            <style>
            .st-emotion-cache-3n56ur.e1326t815 {
                max-height: 600px !important;
                overflow-y: auto !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        with st.expander("Editable Outline", expanded=True):
            edited_lines = []
            for i, line in enumerate(outline_lines):
                new_line = st.text_input(f"Item {i+1}", value=line, key=f"outline_edit_{i}")
                edited_lines.append(new_line)

        # Save updated outline (preserve order from edited_lines)
        st.session_state["generated_outline"] = "\n".join(edited_lines)

    else:
        st.info("No outline generated yet. Click 'Generate Story Outline' to create one.")


