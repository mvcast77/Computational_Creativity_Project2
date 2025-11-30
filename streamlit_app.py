import streamlit as st
import json
import os
import requests
from openai import OpenAI
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
 
#API KEY GOES HERE
api_key = ""
#MODEL NAME GOES HERE
model = "gpt-4o" 

client = OpenAI(api_key=api_key) #might not need this line

st.info(f"Using model: {model} (best free option for creative writing).")

# -------------------------
# 3. Function: Call LLM
# -------------------------

def call_llm(prompt):
    response = requests.get("http://0.0.0.0:8000/api/v1/methods/receive_result") #might need to change 0.0.0.0 to 127.0.0.1
    print("Received: ")
    print(response.text)
    data = response.json()
    return data["new_text"]
    # print("THE FUNCTION THAT CALLS THE LLM GOES HERE!")

#FOR WHEN WE NO LONGER USE API RESPONSE; THIS IS FOR THE LLM CALL
# def call_llm(prompt: str) -> str:
#     completion = openai.chat.completions.create(
#         model=model,
#         messages=[
#             {"role": "system", "content": "You are a helpful story outline assistant."},
#             {"role": "user", "content": prompt},
#         ],
#         temperature=0.8,
#     )
#     return completion.choices[0].message.content

# -------------------------
# 4. Generate Visual Outline with Editable Sections
# -------------------------

# Initialize session state for storing outline sections
if 'full_outline' not in st.session_state:
    st.session_state.full_outline = ""
if 'act1_content' not in st.session_state:
    st.session_state.act1_content = ""
if 'act2_content' not in st.session_state:
    st.session_state.act2_content = ""
if 'act3_content' not in st.session_state:
    st.session_state.act3_content = ""
if 'outline_generated' not in st.session_state:
    st.session_state.outline_generated = False

st.subheader("2. Generate Story Outline")

if st.button("Generate Complete Story Outline"):
    if not story_idea and not file_text:
        st.error("Please enter a story idea or upload a document.")
    else:
        combined_text = (story_idea or "") + "\n\n" + (file_text or "")

        prompt = f"""
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

            #FOR API CALL
            #st.subheader("📘 Generated Story Outline")
                #st.markdown(result)
            
            st.session_state.full_outline = result #stores outline into current session
            st.session_state.outline_generated = True #marks outline as generated
            
            # Parse the outline into sections (simple split by Act headers)
            # This is a basic parser - you may need to adjust based on actual LLM output
            lines = result.split('\n')
            act1_lines = []
            act2_lines = []
            act3_lines = []
            current_act = 1  # Default to Act I for content before any headers
            
            for line in lines:
                # Check for Act transitions
                if 'Act I' in line or 'Setup' in line:
                    current_act = 1
                elif 'Act II' in line or 'Rising Action' in line:
                    current_act = 2
                elif 'Act III' in line or 'Climax' in line or 'Resolution' in line or 'End' in line:
                    current_act = 3
                
                # Assign line to current act
                if current_act == 1:
                    act1_lines.append(line)
                elif current_act == 2:
                    act2_lines.append(line)
                elif current_act == 3:
                    act3_lines.append(line)
            
            st.session_state.act1_content = '\n'.join(act1_lines)
            st.session_state.act2_content = '\n'.join(act2_lines)
            st.session_state.act3_content = '\n'.join(act3_lines)
        
        st.success("✅ Outline generated! You can now edit individual sections below.")

# -------------------------
# 5. Editable Outline Sections (Linear Layout)
# -------------------------

if st.session_state.outline_generated:
    st.subheader("📘 Edit Your Story Outline")
    st.write("Edit each section independently below. Scroll down to save or download your outline.")
    
    # Custom CSS to increase font size in text areas
    st.markdown("""
        <style>
        .stTextArea textarea {
            font-size: 16px !important;
            line-height: 1.6 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.write("")  # Small spacer
    
    # Act I - Setup
    st.markdown("#### 📖 Act I - Setup")
    col1, col2 = st.columns([5, 1])
    with col1:
        st.session_state.act1_content = st.text_area(
            "Edit Act I:",
            value=st.session_state.act1_content,
            height=120,
            key="act1_editor",
            label_visibility="collapsed"
        )
    with col2:
        st.write("")  # Spacer
        if st.button("🔄 Regenerate", key="regen_act1"):
            combined_text = (story_idea or "") + "\n\n" + (file_text or "")
            prompt = f"""Based on this story: {combined_text}
            
            Generate ONLY Act I - Setup section with key beats in hierarchical bullet format.
            Focus on the setup and introduction of the story."""
            
            with st.spinner("Regenerating Act I..."):
                st.session_state.act1_content = call_llm(prompt)
            st.rerun()
    
    # Act II - Rising Action
    st.markdown("#### 🎬 Act II - Rising Action")
    col1, col2 = st.columns([5, 1])
    with col1:
        st.session_state.act2_content = st.text_area(
            "Edit Act II:",
            value=st.session_state.act2_content,
            height=120,
            key="act2_editor",
            label_visibility="collapsed"
        )
    with col2:
        st.write("")  # Spacer
        if st.button("🔄 Regenerate", key="regen_act2"):
            combined_text = (story_idea or "") + "\n\n" + (file_text or "")
            prompt = f"""Based on this story: {combined_text}
            
            Generate ONLY Act II - Rising Action section with key beats in hierarchical bullet format.
            Focus on the rising action and conflict development."""
            
            with st.spinner("Regenerating Act II..."):
                st.session_state.act2_content = call_llm(prompt)
            st.rerun()
    
    # Act III - Climax & Resolution
    st.markdown("#### 🎯 Act III - Climax & Resolution")
    col1, col2 = st.columns([5, 1])
    with col1:
        st.session_state.act3_content = st.text_area(
            "Edit Act III:",
            value=st.session_state.act3_content,
            height=120,
            key="act3_editor",
            label_visibility="collapsed"
        )
    with col2:
        st.write("")  # Spacer
        if st.button("🔄 Regenerate", key="regen_act3"):
            combined_text = (story_idea or "") + "\n\n" + (file_text or "")
            prompt = f"""Based on this story: {combined_text}
            
            Generate ONLY Act III - Climax & Resolution section with key beats in hierarchical bullet format.
            Focus on the climax and resolution of the story."""
            
            with st.spinner("Regenerating Act III..."):
                st.session_state.act3_content = call_llm(prompt)
            st.rerun()
    
# -------------------------
# 6. Save and Export Options
# -------------------------
    
    st.divider()
    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
        if st.button("💾 Save Changes", type="primary"):
            st.session_state.full_outline = f"""{st.session_state.act1_content}

{st.session_state.act2_content}

{st.session_state.act3_content}"""
            st.success("✅ Changes saved to session!")
    
    with col2:
        # Download as text file
        download_content = f"""{st.session_state.act1_content}

{st.session_state.act2_content}

{st.session_state.act3_content}"""
        
        st.download_button(
            label="📥 Download Outline",
            data=download_content,
            file_name=f"story_outline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )
    
    with col3:
        if st.button("🗑️ Clear Outline"):
            st.session_state.outline_generated = False
            st.session_state.full_outline = ""
            st.session_state.act1_content = ""
            st.session_state.act2_content = ""
            st.session_state.act3_content = ""
            st.rerun()
