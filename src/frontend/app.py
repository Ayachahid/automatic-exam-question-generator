import streamlit as st
import httpx
import json
from pathlib import Path

# API Configuration - Use 127.0.0.1 to avoid localhost resolution issues
API_BASE_URL = "http://127.0.0.1:8000/api/v1"

st.set_page_config(
    page_title="AI Exam Question Generator",
    page_icon="📝",
    layout="wide"
)

st.title("📝 AI Exam Question Generator")
st.markdown("Upload your course material and generate practice exam questions instantly.")

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    question_type = st.selectbox(
        "Question Type",
        options=["multiple_choice", "short_answer", "true_false", "essay"],
        index=0
    )
    
    difficulty = st.select_slider(
        "Difficulty",
        options=["easy", "medium", "hard"],
        value="medium"
    )
    
    num_questions = st.number_input(
        "Number of Questions",
        min_value=1,
        max_value=20,
        value=5
    )
    
    st.divider()
    if st.button("🗑️ Clear History"):
        st.session_state.questions = []
        st.session_state.file_id = None
        st.session_state.file_path = None
        st.rerun()
    
    st.divider()
    st.info(f"Backend: {API_BASE_URL}")

# --- Session State Initialization ---
if "questions" not in st.session_state:
    st.session_state.questions = []
if "file_id" not in st.session_state:
    st.session_state.file_id = None
if "file_path" not in st.session_state:
    st.session_state.file_path = None
if "last_uploaded" not in st.session_state:
    st.session_state.last_uploaded = None

# --- Main Interface ---
uploaded_file = st.file_uploader(
    "Upload Course Material (PDF, TXT, DOCX)",
    type=["pdf", "txt", "docx"]
)

# Upload logic - trigger if new file or file_path is missing
if uploaded_file and (st.session_state.last_uploaded != uploaded_file.name):
    with st.spinner("Uploading file..."):
        try:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            response = httpx.post(f"{API_BASE_URL}/upload/", files=files)
            response.raise_for_status()
            data = response.json()
            
            st.session_state.file_id = data["file_id"]
            st.session_state.file_path = data["file_path"]
            st.session_state.last_uploaded = uploaded_file.name
            st.success(f"✅ File uploaded successfully: {uploaded_file.name}")
        except Exception as e:
            st.error(f"❌ Upload failed: {str(e)}")

# --- Generation Trigger ---
if st.session_state.file_path:
    if st.button("🚀 Generate Questions", type="primary"):
        with st.spinner("Generating questions using AI (Ollama)..."):
            try:
                payload = {
                    "file_path": st.session_state.file_path,
                    "question_type": question_type,
                    "difficulty": difficulty,
                    "num_questions": int(num_questions)
                }
                
                # Using 127.0.0.1 directly to match backend binding
                response = httpx.post(
                    f"{API_BASE_URL}/generate/",
                    json=payload,
                    timeout=600.0  # Increased timeout for complex generations
                )
                
                if response.status_code == 404:
                    st.error(f"❌ Route not found (404). Tried: {response.url}")
                    st.info("Check if the FastAPI backend is running with the latest code.")
                else:
                    response.raise_for_status()
                    st.session_state.questions = response.json()["questions"]
                    
                    if not st.session_state.questions:
                        st.warning("⚠️ No questions were generated. The LLM output might be malformed.")
                    else:
                        st.success(f"✅ Generated {len(st.session_state.questions)} questions!")
            except httpx.HTTPStatusError as e:
                st.error(f"❌ API Error: {e.response.text}")
            except Exception as e:
                st.error(f"❌ Generation failed: {str(e)}")

# --- Display Results ---
if st.session_state.questions:
    st.divider()
    st.header("📑 Generated Questions")
    
    for i, q in enumerate(st.session_state.questions, 1):
        with st.container():
            st.subheader(f"Question {i}")
            st.write(q["question"])
            
            # Show Options for MCQs
            if q.get("options"):
                st.markdown("**Options:**")
                for j, opt in enumerate(q["options"]):
                    st.write(f"{chr(65+j)}) {opt}")
            
            # Interactive Answer Reveal
            with st.expander("Show Answer"):
                st.write(f"**Answer:** {q['answer']}")
                if q.get("explanation"):
                    st.write(f"*Explanation:* {q['explanation']}")
            st.divider()
    
    # --- Export Feature ---
    st.download_button(
        label="📥 Download Questions (JSON)",
        data=json.dumps(st.session_state.questions, indent=2),
        file_name="generated_questions.json",
        mime="application/json"
    )
