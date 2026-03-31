import streamlit as st
import httpx
import json
import re

# API Configuration - Use 127.0.0.1 to avoid localhost resolution issues
API_BASE_URL = "http://127.0.0.1:8000/api/v1"

st.set_page_config(
    page_title="AI Exam Question Generator", page_icon="📝", layout="wide"
)

st.title("📝 AI Exam Question Generator")
st.markdown("Generate practice exam questions instantly from your course materials.")

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("⚙️ Configuration")

    question_type = st.selectbox(
        "Question Type",
        options=[
            "multiple_choice",
            "short_answer",
            "true_false",
            "essay",
            "scenario_based",
        ],
        index=0,
        format_func=lambda x: x.replace("_", " ").title(),
    )

    difficulty = st.select_slider(
        "Difficulty",
        options=["easy", "medium", "hard"],
        value="medium",
        format_func=lambda x: x.title(),
    )

    num_questions = st.number_input(
        "Number of Questions", min_value=1, max_value=20, value=5
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
if "gen_id" not in st.session_state:
    st.session_state.gen_id = 0

# --- Main Interface ---

tab1, tab2 = st.tabs(["📁 Upload File", "✍️ Paste Text"])

input_method = None
input_data = None

with tab1:
    uploaded_file = st.file_uploader(
        "Upload Course Material (PDF, TXT, DOCX)", type=["pdf", "txt", "docx"]
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
        placeholder="Deep Learning is a subset of machine learning...",
    )
    if raw_text.strip():
        input_method = "text"
        input_data = raw_text

# --- Generation Trigger ---
st.divider()
generate_btn = st.button(
    "🚀 Generate Questions", type="primary", use_container_width=True
)

if generate_btn:
    st.session_state.questions = []  # Clear old results immediately
    st.session_state.gen_id += 1  # Force unique keys for new session
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
    payload.update(
        {
            "question_type": question_type,
            "difficulty": difficulty,
            "num_questions": int(num_questions),
        }
    )

    with st.spinner("Generating questions using AI..."):
        try:
            # Using 127.0.0.1 directly to match backend binding
            response = httpx.post(
                f"{API_BASE_URL}/generate/",
                json=payload,
                timeout=600.0,  # Increased timeout for complex generations
                follow_redirects=True,
            )

            if response.status_code == 404:
                st.error(f"❌ Route not found (404). Tried: {response.url}")
                st.info("Check if the FastAPI backend is running.")
            else:
                response.raise_for_status()
                data = response.json()
                st.session_state.questions = data.get("questions", [])

                if not st.session_state.questions:
                    st.warning(
                        "⚠️ No questions were generated. The LLM output might be malformed."
                    )
                else:
                    st.success(
                        f"✅ Generated {len(st.session_state.questions)} questions!"
                    )
        except httpx.HTTPStatusError as e:
            st.error(f"❌ API Error ({e.response.status_code}): {e.response.text}")
            try:
                error_detail = e.response.json()
                st.json(error_detail)
            except Exception:
                pass
        except Exception as e:
            st.error(f"❌ Generation failed: {str(e)}")
            st.exception(e)

# --- Display Results ---
if st.session_state.questions:
    st.divider()
    st.subheader(f"📑 Generated Questions ({len(st.session_state.questions)})")

    for i, q in enumerate(st.session_state.questions, 1):
        with st.container():
            st.markdown(f"**{i}. {q['question']}**")

            # Display scenario context for scenario_based questions
            if question_type == "scenario_based" and q.get("scenario"):
                st.info(f"📖 **Scenario:**\n{q['scenario']}")

            # Display concepts tested (for scenario_based or if present)
            if q.get("concepts_tested"):
                st.caption(f"🎯 **Concepts tested:** {', '.join(q['concepts_tested'])}")

            # Show Options for MCQs
            if q.get("options") and question_type == "multiple_choice":
                user_choice = st.radio(
                    f"Select your answer for Q{i}:",
                    options=q["options"],
                    key=f"q{i}_choice_{st.session_state.gen_id}",
                    index=None,
                )

                if user_choice:
                    # Logic to handle A/B/C/D answers from LLM
                    # Normalize answer_raw: remove dots, parentheses, and whitespace
                    answer_raw = str(q["answer"]).strip().upper()
                    clean_answer = (
                        re.sub(r"[^A-D]", "", answer_raw)
                        if len(answer_raw) <= 3
                        else ""
                    )

                    correct_text = None

                    # If it's a clear letter mapping (A, B, C, or D)
                    if len(clean_answer) == 1 and clean_answer in "ABCD":
                        index = ord(clean_answer) - ord("A")
                        if 0 <= index < len(q["options"]):
                            correct_text = q["options"][index]

                    # If mapping failed or answer is likely full text
                    if not correct_text:
                        correct_text = str(q["answer"])

                    is_correct = (
                        str(user_choice).strip().lower()
                        == str(correct_text).strip().lower()
                    )

                    if is_correct:
                        st.success(f"✨ Correct! (Answer: {answer_raw})")
                    else:
                        # Avoid showing (D) (D) if they are identical
                        if str(answer_raw).strip() == str(correct_text).strip():
                            st.error(
                                f"❌ Incorrect. The correct answer is: {answer_raw}"
                            )
                        else:
                            st.error(
                                f"❌ Incorrect. The correct answer is: {answer_raw} ({correct_text})"
                            )

            # Show Options for True/False
            elif question_type == "true_false":
                user_choice = st.radio(
                    f"Select your answer for Q{i}:",
                    options=["True", "False"],
                    key=f"q{i}_choice_tf_{st.session_state.gen_id}",
                    index=None,
                    horizontal=True,
                )

                if user_choice:
                    # Robust normalization for True/False
                    raw_ans = str(q["answer"]).strip().lower()

                    if raw_ans in ["true", "1", "t", "yes"]:
                        correct_answer_str = "True"
                    elif raw_ans in ["false", "0", "f", "no"]:
                        correct_answer_str = "False"
                    else:
                        correct_answer_str = str(q["answer"]).strip().capitalize()

                    if user_choice == correct_answer_str:
                        st.success("✨ Correct!")
                    else:
                        st.error(
                            f"❌ Incorrect. The correct answer is: {correct_answer_str}"
                        )

            # Interactive Answer Reveal (for other types or additional info)
            with st.expander("See Explanation"):
                if question_type not in ["multiple_choice", "true_false"]:
                    st.markdown(f"**Answer:**\n{q['answer']}")

                if q.get("explanation"):
                    st.info(f"💡 **Explanation:** {q['explanation']}")
            st.divider()

    # --- Export Feature ---
    st.subheader("📤 Export Questions")

    col1, col2, col3 = st.columns(3)

    with col1:
        export_format = st.selectbox(
            "Format",
            options=["json", "pdf", "txt"],
            index=0,
        )

    with col2:
        export_filename = st.text_input(
            "Filename (optional)",
            placeholder="exam_questions",
            key="export_filename_input",
        )

    with col3:
        export_btn = st.button("📥 Export", type="primary", use_container_width=True)

    if export_btn:
        try:
            export_payload = {
                "questions": st.session_state.questions,
                "format": export_format,
                "filename": export_filename.strip() if export_filename.strip() else None,
            }

            response = httpx.post(
                f"{API_BASE_URL}/export/",
                json=export_payload,
                timeout=60.0,
            )
            response.raise_for_status()

            # Get filename from headers or use default
            content_disposition = response.headers.get("Content-Disposition", "")
            if "filename=" in content_disposition:
                download_filename = content_disposition.split("filename=")[1].strip('"')
            else:
                download_filename = f"exam_questions.{export_format}"

            st.download_button(
                label=f"⬇️ Download {export_format.upper()}",
                data=response.content,
                file_name=download_filename,
                mime={
                    "json": "application/json",
                    "pdf": "application/pdf",
                    "txt": "text/plain",
                }.get(export_format, "application/octet-stream"),
                key=f"download_{export_format}_{st.session_state.gen_id}",
            )

        except httpx.HTTPStatusError as e:
            st.error(f"❌ Export failed ({e.response.status_code}): {e.response.text}")
        except Exception as e:
            st.error(f"❌ Export failed: {str(e)}")
