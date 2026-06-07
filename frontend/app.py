import streamlit as st
import os
import requests
import json
import logging

# Set up logging for frontend
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Frontend")

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# Page configuration
st.set_page_config(
    page_title="BRD Genie - Multi-Agent PM System",
    page_icon="🧞‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling Injection (Premium Dark/Neon Glassmorphism Theme)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"], .stMarkdown {
    font-family: 'Outfit', sans-serif;
}

.main-header {
    background: linear-gradient(135deg, #7F00FF 0%, #E100FF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 3.5rem;
    font-weight: 700;
    text-align: center;
    margin-bottom: 5px;
}

.sub-header {
    font-size: 1.2rem;
    color: #a0aec0;
    text-align: center;
    margin-bottom: 30px;
    font-weight: 300;
}

.glass-card {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(8px);
    border-radius: 12px;
    padding: 20px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    margin-bottom: 20px;
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
}

.sidebar-title {
    font-weight: 600;
    font-size: 1.3rem;
    color: #E100FF;
    margin-bottom: 15px;
}

div.stButton > button:first-child {
    background: linear-gradient(135deg, #7F00FF 0%, #E100FF 100%);
    color: white;
    border: none;
    padding: 10px 24px;
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.3s ease;
}

div.stButton > button:first-child:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(225, 0, 255, 0.4);
}
</style>
""", unsafe_allow_html=True)

# Initialize Session States
if "step" not in st.session_state:
    st.session_state.step = "input"
if "graph_state" not in st.session_state:
    st.session_state.graph_state = {}
if "questions" not in st.session_state:
    st.session_state.questions = []
if "answers" not in st.session_state:
    st.session_state.answers = []
if "english_brd" not in st.session_state:
    st.session_state.english_brd = ""
if "localized_brd" not in st.session_state:
    st.session_state.localized_brd = ""
if "language" not in st.session_state:
    st.session_state.language = "Hindi"

# ==========================================
# SIDEBAR - HISTORY & CONTROLS
# ==========================================
st.sidebar.markdown('<div class="sidebar-title">📜 BRD Generation History</div>', unsafe_allow_html=True)

try:
    res = requests.get(f"{BACKEND_URL}/api/history", timeout=5)
    if res.status_code == 200:
        history_list = res.json()
        if not history_list:
            st.sidebar.info("No past BRDs found.")
        else:
            for item in history_list:
                btn_label = f"📁 {item['project_name']} ({item['language']})"
                if st.sidebar.button(btn_label, key=f"hist_{item['id']}", use_container_width=True):
                    try:
                        detail_res = requests.get(f"{BACKEND_URL}/api/history/{item['id']}", timeout=5)
                        if detail_res.status_code == 200:
                            detail = detail_res.json()
                            st.session_state.english_brd = detail.get("english_brd", "")
                            st.session_state.localized_brd = detail.get("localized_brd", "")
                            st.session_state.language = detail.get("language", "English")
                            st.session_state.graph_state = {
                                "raw_input": detail.get("raw_input", ""),
                                "cleaned_input": detail.get("cleaned_input", ""),
                                "brd_draft": detail.get("english_brd", ""),
                                "language": detail.get("language", "English")
                            }
                            st.session_state.step = "completed"
                            st.rerun()
                        else:
                            st.sidebar.error("Failed to fetch BRD details.")
                    except requests.exceptions.RequestException as e:
                        logger.error(f"Failed to fetch history details: {e}")
                        st.sidebar.error("Network error fetching details.")
    else:
        st.sidebar.error(f"Error connecting to backend: {res.status_code}")
except requests.exceptions.RequestException as e:
    logger.error(f"Failed to fetch history: {e}")
    st.sidebar.error("Backend server is unreachable.")


# ==========================================
# MAIN PAGE LAYOUT
# ==========================================
st.markdown('<div class="main-header">BRD Genie 🧞‍♂️</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Multi-Agent AI PM: Turning Messy Voice & Text Notes into Professional BRDs</div>', unsafe_allow_html=True)

# ------------------------------------------
# STEP 1: INPUT REQUIREMENTS
# ------------------------------------------
if st.session_state.step == "input":
    st.markdown('<div class="glass-card"><h3>📥 Step 1: Tell Genie about your Project</h3></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        lang_option = st.selectbox(
            "Target Localization Language (for translation of final BRD)",
            ["Hindi", "Tamil", "Telugu", "Kannada", "Bengali", "Marathi", "Gujarati", "Malayalam", "Punjabi", "Spanish", "French", "English"],
            index=0
        )
        st.session_state.language = lang_option
        
        input_type = st.radio("Choose Input Type:", ["🎙️ Audio File Upload", "✍️ Paste Text Notes"])
        
        raw_text_input = ""
        uploaded_file = None
        
        if input_type == "✍️ Paste Text Notes":
            raw_text_input = st.text_area(
                "Write or paste your messy notes here (any language):",
                placeholder="Example: Mujhe ek app chahiye jo dukaan ka hisaab rakhe...",
                height=200
            )
        else:
            uploaded_file = st.file_uploader(
                "Upload a voice note recording (.wav, .mp3, .m4a):",
                type=["wav", "mp3", "m4a", "ogg"]
            )
            st.info("💡 You can record a brief audio on your phone and upload it here.")
            
        if st.button("🚀 Process & Analyze Requirements"):
            if input_type == "✍️ Paste Text Notes" and not raw_text_input.strip():
                st.error("Please enter some text notes.")
            elif input_type == "🎙️ Audio File Upload" and not uploaded_file:
                st.error("Please upload an audio file.")
            else:
                with st.spinner("Analyzing requirements via Sarvam AI and CrewAI Agents... This may take up to 60 seconds."):
                    try:
                        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)} if uploaded_file else None
                        data = {"language": lang_option}
                        if raw_text_input:
                            data["raw_text"] = raw_text_input
                            
                        # Post to start endpoint
                        if files:
                            response = requests.post(f"{BACKEND_URL}/api/start", data=data, files=files, timeout=300)
                        else:
                            response = requests.post(f"{BACKEND_URL}/api/start", data=data, timeout=300)
                            
                        if response.status_code == 200:
                            state = response.json()
                            st.session_state.graph_state = state
                            questions = state.get("questions", [])
                            
                            if questions:
                                st.session_state.questions = questions
                                st.session_state.step = "clarification"
                            else:
                                # If no questions generated, it must have skipped to end (unlikely, but handled)
                                st.session_state.english_brd = state.get("final_brd", state.get("brd_draft", ""))
                                st.session_state.localized_brd = state.get("localized_brd", "")
                                st.session_state.step = "completed"
                            st.rerun()
                        else:
                            error_detail = response.json().get('detail', 'Unknown error')
                            st.error(f"Backend processing failed: {response.status_code} - {error_detail}")
                            
                    except requests.exceptions.Timeout:
                        st.error("The request timed out. The AI agents are taking too long to process the request.")
                    except requests.exceptions.RequestException as e:
                        logger.error(f"API Start Error: {e}")
                        st.error("Failed to connect to the backend server. Is it running?")

    with col2:
        st.markdown("""
        <div class="glass-card" style="height: 100%;">
            <h4>🧠 Meet the Genie Multi-Agent Squad:</h4>
            <ul>
                <li><strong>🗣️ Sarvam AI</strong>: Transcribes voice and cleans up slang.</li>
                <li><strong>🕵️ Context & Requirements Crews</strong>: Sorts notes into problems, actors, features.</li>
                <li><strong>❓ Ambiguity & Risk Agents</strong>: Identifies gaps and asks follow-up questions.</li>
                <li><strong>🏗️ BRD Generation Crew</strong>: Structuring and technical writing powered by Groq.</li>
                <li><strong>🌍 Localization Agent</strong>: Translates the verified BRD back into your selected language.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# ------------------------------------------
# STEP 2: CLARIFICATION CHAT
# ------------------------------------------
elif st.session_state.step == "clarification":
    st.markdown('<div class="glass-card"><h3>❓ Step 2: Clarifying Your Requirements</h3></div>', unsafe_allow_html=True)
    st.write("The Ambiguity Detection Agent detected some missing details in your description. Please provide answers to continue.")

    questions = st.session_state.questions
    answers = []

    for idx, question in enumerate(questions):
        st.markdown(f"**Question {idx + 1}:** {question}")
        ans = st.text_input(f"Your answer to Question {idx + 1}:", key=f"q_{idx}")
        answers.append(ans)

    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("🏗️ Generate BRD"):
            processed_answers = [a if a.strip() else "Not specified" for a in answers]
            
            with st.spinner("Generating Professional BRD... Executing Structuring, BRD, and QA Agents..."):
                try:
                    payload = {"state": st.session_state.graph_state, "answers": processed_answers}
                    response = requests.post(f"{BACKEND_URL}/api/clarify", json=payload, timeout=300)
                    
                    if response.status_code == 200:
                        state = response.json()
                        st.session_state.graph_state = state
                        st.session_state.english_brd = state.get("final_brd", state.get("brd_draft", ""))
                        st.session_state.localized_brd = state.get("localized_brd", "")
                        st.session_state.step = "completed"
                        st.rerun()
                    else:
                        error_detail = response.json().get('detail', 'Unknown error')
                        st.error(f"Backend clarification failed: {response.status_code} - {error_detail}")
                except requests.exceptions.Timeout:
                    st.error("The document generation timed out.")
                except requests.exceptions.RequestException as e:
                    logger.error(f"API Clarify Error: {e}")
                    st.error("Failed to connect to the backend server.")
                    
    with col2:
        if st.button("⬅️ Start Over"):
            st.session_state.step = "input"
            st.session_state.questions = []
            st.session_state.answers = []
            st.rerun()

# ------------------------------------------
# STEP 3: BRD OUTPUT & REGENERATION
# ------------------------------------------
elif st.session_state.step == "completed":
    st.markdown('<div class="glass-card"><h3>📄 Step 3: Your Generated BRD is Ready!</h3></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🇬🇧 English Business Requirements Document")
        st.markdown(st.session_state.english_brd)
        st.download_button(
            label="📥 Download English BRD (.md)",
            data=st.session_state.english_brd,
            file_name="BRD_English.md",
            mime="text/markdown"
        )
        
    with col2:
        st.subheader(f"🌐 Localized BRD ({st.session_state.language})")
        st.markdown(st.session_state.localized_brd)
        st.download_button(
            label=f"📥 Download Localized BRD ({st.session_state.language})",
            data=st.session_state.localized_brd,
            file_name=f"BRD_{st.session_state.language}.md",
            mime="text/markdown"
        )

    st.markdown("---")
    
    st.subheader("✏️ Edit and Refine")
    edit_col1, edit_col2 = st.columns([2, 1])
    
    with edit_col1:
        edit_notes = st.text_area("Need changes? Send feedback to the Refinement Agent:", placeholder="Example: Add a feature for exporting sales reports to PDF.")
        if st.button("🔄 Refine BRD"):
            with st.spinner("Refining requirements... The Refinement Agent is editing your document."):
                try:
                    # To trigger refinement, we pass the feedback as a new "answer" to the clarify endpoint
                    # The graph_state already contains the brd_draft
                    st.session_state.graph_state["answers"] = [edit_notes]
                    st.session_state.graph_state["questions"] = ["User Feedback Revision"]
                    
                    payload = {"state": st.session_state.graph_state, "answers": [edit_notes]}
                    response = requests.post(f"{BACKEND_URL}/api/clarify", json=payload, timeout=300)
                    
                    if response.status_code == 200:
                        state = response.json()
                        st.session_state.graph_state = state
                        st.session_state.english_brd = state.get("final_brd", state.get("brd_draft", ""))
                        st.session_state.localized_brd = state.get("localized_brd", "")
                        st.rerun()
                    else:
                        st.error(f"Refinement failed: {response.status_code}")
                except Exception as e:
                    st.error(f"Error triggering refinement: {e}")
                    
    with edit_col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🆕 Create New Project", use_container_width=True):
            st.session_state.step = "input"
            st.session_state.graph_state = {}
            st.session_state.questions = []
            st.session_state.answers = []
            st.session_state.english_brd = ""
            st.session_state.localized_brd = ""
            st.rerun()
