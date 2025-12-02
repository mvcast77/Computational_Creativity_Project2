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

st.subheader("1. Describe Your Story Idea in the Text Box Below or Upload it")

# Create two columns for story input and file upload
col1, col2 = st.columns([2, 1])

with col1:
    story_idea = st.text_area(
        "Enter the premise or partial story description:",
        placeholder="Example: A young botanist discovers a glowing plant in the forest...",
        height=200
    )

with col2:
    uploaded_file = st.file_uploader(
        "Upload a PDF, TXT, or DOCX file:",
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

# Plot points selection - now as a number input
st.write("")
plot_points_per_act = st.number_input(
    "Number of plot points per act:",
    min_value=2,
    max_value=6,
    value=3,
    step=1,
    help="Enter how many key beats/plot points you want for each act (2-6)"
)

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

# def call_llm(prompt):
#     response = requests.get("http://127.0.0.1:8000/api/v1/methods/receive_result") #might need to change 0.0.0.0 to 127.0.0.1
#     print("Received: ")
#     print(response.text)
#     data = response.json()
#     return data["new_text"]
#     # print("THE FUNCTION THAT CALLS THE LLM GOES HERE!")

#FOR WHEN WE NO LONGER USE API RESPONSE; THIS IS FOR THE LLM CALL
def call_llm(prompt: str) -> str:
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful story outline assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.8,
    )
    return completion.choices[0].message.content

# -------------------------
# 4. Generate Visual Outline with Editable Sections
# -------------------------

# Initialize session state for storing outline sections and version history
if 'full_outline' not in st.session_state:
    st.session_state.full_outline = ""
if 'act1_beats' not in st.session_state:
    st.session_state.act1_beats = []
if 'act2_beats' not in st.session_state:
    st.session_state.act2_beats = []
if 'act3_beats' not in st.session_state:
    st.session_state.act3_beats = []
if 'outline_generated' not in st.session_state:
    st.session_state.outline_generated = False
# Version history: list of dicts with keys 'timestamp', 'outline', 'act1_beats', 'act2_beats', 'act3_beats'
if 'outline_versions' not in st.session_state:
    st.session_state.outline_versions = []
if 'selected_version_idx' not in st.session_state:
    st.session_state.selected_version_idx = None
if 'plot_points_per_act' not in st.session_state:
    st.session_state.plot_points_per_act = 3

st.subheader("2. Generate Story Outline")


if st.button("Generate Complete Story Outline"):
    if not story_idea and not file_text:
        st.error("Please enter a story idea or upload a document.")
    else:
        # Store the plot points preference
        st.session_state.plot_points_per_act = plot_points_per_act
        
        combined_text = (story_idea or "") + "\n\n" + (file_text or "")
        
        # Create example beats based on the selected number
        example_beats = "\n".join([f"- Key beat {i+1}" for i in range(plot_points_per_act)])

        prompt = f"""
            Create a clear, detailed, visual story outline based on the following material:

            {combined_text}

            Your outline must follow this format with EXACTLY {plot_points_per_act} plot points per act:

            - Act I
            - Setup
{example_beats}
            - Act II
            - Rising Action
{example_beats}
            - Act III
            - Climax & Resolution
{example_beats}

            Guidelines:
            - Use hierarchical bullet formatting.
            - Provide EXACTLY {plot_points_per_act} key beats for each act.
            - Do NOT include a summary or explanations.
            - Keep the outline tight and structured like a screenplay or novel planner.
            - Focus purely on plot beats and story flow.
            """

        with st.spinner("Generating outline..."):
            result = call_llm(prompt)

            #FOR API CALL
            # st.subheader("📘 Generated Story Outline")
            # st.markdown(combined_text)

            # Save current version before overwriting (if any outline exists)
            if st.session_state.full_outline.strip():
                ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                st.session_state.outline_versions.append({
                    'label': f"Full outline generation @ {ts}",
                    'timestamp': ts,
                    'outline': st.session_state.full_outline,
                    'act1_beats': st.session_state.act1_beats[:],
                    'act2_beats': st.session_state.act2_beats[:],
                    'act3_beats': st.session_state.act3_beats[:]
                })

            st.session_state.full_outline = result #stores outline into current session
            st.session_state.outline_generated = True #marks outline as generated

            # Parse the outline into individual beats
            def parse_beats(text):
                """Extract individual beats from outline text, filtering out headers."""
                lines = text.split('\n')
                beats = []
                
                for line in lines:
                    line = line.strip()
                    # Skip empty lines
                    if not line:
                        continue
                    
                    # Skip structural headers (but be more specific)
                    line_lower = line.lower()
                    if line_lower in ['setup', 'rising action', 'climax', 'resolution', 'climax & resolution', 'climax and resolution']:
                        continue
                    if line.startswith('- **') and line.endswith('**'):
                        # This is a bold header like "- **Setup**"
                        continue
                    
                    # Extract actual beat content (remove bullet markers)
                    if line.startswith('- '):
                        beat = line[2:].strip()
                        # Remove "Key beat X:" prefix if present
                        if beat.lower().startswith('key beat'):
                            # Find the colon and take everything after it
                            if ':' in beat:
                                beat = beat.split(':', 1)[1].strip()
                            else:
                                continue  # Skip if it's just "Key beat X" without content
                        if beat:  # Only add non-empty beats
                            beats.append(beat)
                return beats

            lines = result.split('\n')
            act1_text = []
            act2_text = []
            act3_text = []
            current_act = 0

            for line in lines:
                line_stripped = line.strip()
                line_lower = line_stripped.lower()
                
                # Check for Act transitions - be more flexible
                if 'act i' in line_lower and 'act ii' not in line_lower and 'act iii' not in line_lower:
                    current_act = 1
                    continue  # Don't add the act header line itself
                elif 'act ii' in line_lower and 'act iii' not in line_lower:
                    current_act = 2
                    continue  # Don't add the act header line itself
                elif 'act iii' in line_lower:
                    current_act = 3
                    continue  # Don't add the act header line itself
                
                # Assign line to current act
                if current_act == 1:
                    act1_text.append(line)
                elif current_act == 2:
                    act2_text.append(line)
                elif current_act == 3:
                    act3_text.append(line)

            st.session_state.act1_beats = parse_beats('\n'.join(act1_text))
            st.session_state.act2_beats = parse_beats('\n'.join(act2_text))
            st.session_state.act3_beats = parse_beats('\n'.join(act3_text))

            # After generating, set selected_version_idx to None (current)
            st.session_state.selected_version_idx = None

        st.success("✅ Outline generated! You can now edit individual sections below.")

# -------------------------
# 5. Editable Outline Sections (Linear Layout) + Version History UI
# -------------------------

if st.session_state.outline_generated or st.session_state.outline_versions:
    st.subheader("📘 Edit Your Story Outline")
    st.write("Edit each section independently below. Scroll down to save, download, or view previous versions.")

    # Version history UI (show numeric index + label)
    version_options = [f"{i+1}: {v.get('label', v.get('timestamp',''))}" for i, v in enumerate(st.session_state.outline_versions)]
    if st.session_state.outline_generated:
        version_options.append("Current")

    selected = st.selectbox(
        "Outline Version History:",
        version_options,
        index=len(version_options)-1 if version_options else 0,
        key="version_selectbox"
    )

    # If user selects a previous version, load its content into the editors (read-only)
    if selected != "Current":
        # parse index from option like '1: label'
        try:
            idx = int(selected.split(":")[0].strip()) - 1
        except Exception:
            idx = 0
        v = st.session_state.outline_versions[idx]
        st.info(f"Viewing version: {v.get('label', v.get('timestamp'))}. To restore, click below.")

        # allow renaming the version
        new_label = st.text_input("Rename version:", value=v.get('label',''), key=f"rename_input_{idx}")
        if st.button("Rename", key=f"rename_btn_{idx}"):
            st.session_state.outline_versions[idx]['label'] = new_label
            st.success("Version renamed.")
            st.rerun()

        if st.button("Restore This Version", key=f"restore_{idx}"):
            st.session_state.full_outline = v['outline']
            st.session_state.act1_beats = v.get('act1_beats', [])
            st.session_state.act2_beats = v.get('act2_beats', [])
            st.session_state.act3_beats = v.get('act3_beats', [])
            st.session_state.outline_generated = True
            st.session_state.selected_version_idx = None
            st.success("Restored selected version. You can now edit and save as a new version.")
            st.rerun()

        # Show the outline sections as read-only
        with st.expander("📖 Act I - Setup", expanded=True):
            for i, beat in enumerate(v.get('act1_beats', [])):
                st.text_area(f"Beat {i+1}:", value=beat, height=80, key=f"act1_beat{i}_view_{idx}", disabled=True, label_visibility="collapsed")
        with st.expander("🎬 Act II - Rising Action", expanded=True):
            for i, beat in enumerate(v.get('act2_beats', [])):
                st.text_area(f"Beat {i+1}:", value=beat, height=80, key=f"act2_beat{i}_view_{idx}", disabled=True, label_visibility="collapsed")
        with st.expander("🎯 Act III - Climax & Resolution", expanded=True):
            for i, beat in enumerate(v.get('act3_beats', [])):
                st.text_area(f"Beat {i+1}:", value=beat, height=80, key=f"act3_beat{i}_view_{idx}", disabled=True, label_visibility="collapsed")
        st.stop()

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
    with st.expander("📖 Act I - Setup", expanded=True):
        for i in range(len(st.session_state.act1_beats)):
            st.session_state.act1_beats[i] = st.text_area(
                f"Beat {i+1}:",
                value=st.session_state.act1_beats[i],
                height=80,
                key=f"act1_beat_{i}",
                label_visibility="collapsed"
            )

    # Act II - Rising Action
    with st.expander("🎬 Act II - Rising Action", expanded=True):
        for i in range(len(st.session_state.act2_beats)):
            st.session_state.act2_beats[i] = st.text_area(
                f"Beat {i+1}:",
                value=st.session_state.act2_beats[i],
                height=80,
                key=f"act2_beat_{i}",
                label_visibility="collapsed"
            )

    # Act III - Climax & Resolution
    with st.expander("🎯 Act III - Climax & Resolution", expanded=True):
        for i in range(len(st.session_state.act3_beats)):
            st.session_state.act3_beats[i] = st.text_area(
                f"Beat {i+1}:",
                value=st.session_state.act3_beats[i],
                height=80,
                key=f"act3_beat_{i}",
                label_visibility="collapsed"
            )

    # -------------------------
    # Regenerate Entire Outline Section
    # -------------------------
    st.divider()
    st.markdown("### 🔄 Regenerate Entire Outline")
    st.write("Provide specific instructions to regenerate the complete outline based on your current story idea.")
    
    regenerate_prompt = st.text_area(
        "Regeneration Instructions:",
        placeholder="Example: Make the story darker and add more mystery elements...",
        height=100,
        key="regenerate_prompt_input"
    )
    
    if st.button("🔄 Regenerate Complete Outline", type="secondary"):
        if not regenerate_prompt.strip():
            st.error("Please provide instructions for regenerating the outline.")
        else:
            # Save a version before regenerating
            if st.session_state.full_outline.strip():
                ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                st.session_state.outline_versions.append({
                    'label': f"Before Regenerate Outline @ {ts}",
                    'timestamp': ts,
                    'outline': st.session_state.full_outline,
                    'act1_beats': st.session_state.act1_beats[:],
                    'act2_beats': st.session_state.act2_beats[:],
                    'act3_beats': st.session_state.act3_beats[:]
                })

            combined_text = (story_idea or "") + "\n\n" + (file_text or "")
            prompt = f"""
                Create a clear, detailed, visual story outline based on the following material:

                {combined_text}

                Additional instructions for this regeneration:
                {regenerate_prompt}

                Your outline must follow this format:

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

            with st.spinner("Regenerating complete outline..."):
                result = call_llm(prompt)
                st.session_state.full_outline = result
                
                # Reuse the parse_beats function from the initial generation
                def parse_beats(text):
                    """Extract individual beats from outline text, filtering out headers."""
                    lines = text.split('\n')
                    beats = []
                    
                    for line in lines:
                        line = line.strip()
                        # Skip empty lines
                        if not line:
                            continue
                        
                        # Skip structural headers (but be more specific)
                        line_lower = line.lower()
                        if line_lower in ['setup', 'rising action', 'climax', 'resolution', 'climax & resolution', 'climax and resolution']:
                            continue
                        if line.startswith('- **') and line.endswith('**'):
                            # This is a bold header like "- **Setup**"
                            continue
                        
                        # Extract actual beat content (remove bullet markers)
                        if line.startswith('- '):
                            beat = line[2:].strip()
                            # Remove "Key beat X:" prefix if present
                            if beat.lower().startswith('key beat'):
                                # Find the colon and take everything after it
                                if ':' in beat:
                                    beat = beat.split(':', 1)[1].strip()
                                else:
                                    continue  # Skip if it's just "Key beat X" without content
                            if beat:  # Only add non-empty beats
                                beats.append(beat)
                    return beats
                
                # Parse the outline into sections
                lines = result.split('\n')
                act1_text = []
                act2_text = []
                act3_text = []
                current_act = 0

                for line in lines:
                    line_stripped = line.strip()
                    line_lower = line_stripped.lower()
                    
                    # Check for Act transitions - be more flexible
                    if 'act i' in line_lower and 'act ii' not in line_lower and 'act iii' not in line_lower:
                        current_act = 1
                        continue  # Don't add the act header line itself
                    elif 'act ii' in line_lower and 'act iii' not in line_lower:
                        current_act = 2
                        continue  # Don't add the act header line itself
                    elif 'act iii' in line_lower:
                        current_act = 3
                        continue  # Don't add the act header line itself
                    
                    # Assign line to current act
                    if current_act == 1:
                        act1_text.append(line)
                    elif current_act == 2:
                        act2_text.append(line)
                    elif current_act == 3:
                        act3_text.append(line)

                st.session_state.act1_beats = parse_beats('\n'.join(act1_text))
                st.session_state.act2_beats = parse_beats('\n'.join(act2_text))
                st.session_state.act3_beats = parse_beats('\n'.join(act3_text))
                
            st.success("✅ Outline regenerated successfully!")
            st.rerun()

# -------------------------
# 6. Save and Export Options
# -------------------------
    st.divider()
    col1, col2, col3 = st.columns([2, 2, 2])

    with col1:
        if st.button("💾 Save Changes", type="primary"):
            # Reconstruct full outline from beats
            act1_text = "\n".join([f"- {beat}" for beat in st.session_state.act1_beats])
            act2_text = "\n".join([f"- {beat}" for beat in st.session_state.act2_beats])
            act3_text = "\n".join([f"- {beat}" for beat in st.session_state.act3_beats])
            st.session_state.full_outline = f"""Act I - Setup\n{act1_text}\n\nAct II - Rising Action\n{act2_text}\n\nAct III - Climax & Resolution\n{act3_text}"""
            st.success("✅ Changes saved to session!")

    with col2:
        # Download as text file
        act1_text = "\n".join([f"- {beat}" for beat in st.session_state.act1_beats])
        act2_text = "\n".join([f"- {beat}" for beat in st.session_state.act2_beats])
        act3_text = "\n".join([f"- {beat}" for beat in st.session_state.act3_beats])
        download_content = f"""Act I - Setup\n{act1_text}\n\nAct II - Rising Action\n{act2_text}\n\nAct III - Climax & Resolution\n{act3_text}"""

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
            st.session_state.act1_beats = []
            st.session_state.act2_beats = []
            st.session_state.act3_beats = []
            st.rerun()
