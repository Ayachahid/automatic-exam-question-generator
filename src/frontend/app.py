import streamlit as st
import httpx
import json

# API Configuration - Use 127.0.0.1 to avoid localhost resolution issues
API_BASE_URL = "http://127.0.0.1:8000/api/v1"

st.set_page_config(
    page_title="AI Exam Question Generator",
    page_icon="📝",
    layout="wide"
)

st.title("📝 AI Exam Question Generator")
st.markdown("Generate practice exam questions instantly from your course materials.")

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    question_type = st.selectbox(
        "Question Type",
        options=["multiple_choice", "short_answer", "true_false", "essay"],
        index=0,
        format_func=lambda x: x.replace("_", " ").title()
    )
    
    difficulty = st.select_slider(
        "Difficulty",
        options=["easy", "medium", "hard"],
        value="medium",
        format_func=lambda x: x.title()
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
        st.session_state.last_uploaded = None
        st.rerun()
    
    st.divider()
    st.caption(f"Backend: `{API_BASE_URL}`")

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

tab1, tab2 = st.tabs(["📁 Upload File", "✍️ Paste Text"])

input_method = None
input_data = None

with tab1:
    uploaded_file = st.file_uploader(
        "Upload Course Material (PDF, TXT, DOCX)",
        type=["pdf", "txt", "docx"]
    )

    if uploaded_file:
        input_method = "file"
        # Upload logic - trigger if new file
        if st.session_state.last_uploaded != uploaded_file.name:
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
        
        if st.session_state.file_path:
            st.info(f"Using file: `{uploaded_file.name}`")

with tab2:
    raw_text = st.text_area(
        "Paste your study material here",
        height=300,
        placeholder="Deep Learning is a subset of machine learning..."
    )
    if raw_text.strip():
        input_method = "text"
        input_data = raw_text

# --- Generation Trigger ---
st.divider()
generate_btn = st.button("🚀 Generate Questions", type="primary", use_container_width=True)

if generate_btn:
    payload = {}
    
    # Determine source
    if input_method == "file" and st.session_state.file_path:
        payload["file_path"] = st.session_state.file_path
    elif input_method == "text" and input_data:
        payload["text"] = input_data
    else:
        st.warning("⚠️ Please upload a file or paste text first.")
        st.stop()

    # Add config
    payload.update({
        "question_type": question_type,
        "difficulty": difficulty,
        "num_questions": int(num_questions)
    })

    with st.spinner("Generating questions using AI..."):
        try:
            # Using 127.0.0.1 directly to match backend binding
            response = httpx.post(
                f"{API_BASE_URL}/generate/",
                json=payload,
                timeout=600.0  # Increased timeout for complex generations
            )
            
            if response.status_code == 404:
                st.error(f"❌ Route not found (404). Tried: {response.url}")
                st.info("Check if the FastAPI backend is running.")
            else:
                response.raise_for_status()
                data = response.json()
                st.session_state.questions = data.get("questions", [])
                
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
    st.subheader(f"📑 Generated Questions ({len(st.session_state.questions)})")
    
    for i, q in enumerate(st.session_state.questions, 1):
        with st.container():
            st.markdown(f"**{i}. {q['question']}**")
            
            # Show Options for MCQs
            if q.get("options") and question_type == "multiple_choice":
                # Use radio for display, disabled to act as a view-only list
                st.radio(
                    f"Options for Q{i}",
                    options=q["options"],
                    key=f"q{i}_opts",
                    index=None,
                    disabled=True,
                    label_visibility="collapsed"
                )
            
            # Interactive Answer Reveal
            with st.expander("Show Answer"):
                if question_type == "multiple_choice":
                    st.markdown(f"**Correct Answer:** `{q['answer']}`")
                else:
                    st.markdown(f"**Answer:**\n{q['answer']}")
                
                if q.get("explanation"):
                    st.info(f"💡 **Explanation:** {q['explanation']}")
            st.divider()
    
    # --- Export Feature ---
    st.download_button(
        label="📥 Download Questions (JSON)",
        data=json.dumps(st.session_state.questions, indent=2),
        file_name="generated_questions.json",
        mime="application/json"
    )
