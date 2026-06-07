import streamlit as st
import os

# Configuration
# TODO: Connect this to the actual backend API URL
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

/* Apply modern font */
html, body, [class*="css"], .stMarkdown {
    font-family: 'Outfit', sans-serif;
}

/* Main gradient header */
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

/* Styled glassmorphism card */
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

/* Gradient buttons custom classes */
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

/* Secondary helper buttons */
div.stButton > button.secondary-btn {
    background: rgba(255, 255, 255, 0.1);
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.2);
}
</style>
""", unsafe_allow_html=True)

# Initialize Session States for Page Routing and Flow
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

# TODO: Frontend Developer - Connect this to retrieve past BRDs from database via `/api/history`
# Example API Fetch Structure:
# try:
#     res = requests.get(f"{BACKEND_URL}/api/history")
#     history_list = res.json()
# except Exception as e:
#     st.sidebar.error("Error connecting to backend database API")

# Mock History items for UI presentation
mock_history = [
    {"id": 1, "project_name": "Retail Billing System", "language": "Hindi"},
    {"id": 2, "project_name": "E-Commerce App", "language": "Tamil"},
]

for item in mock_history:
    btn_label = f"📁 {item['project_name']} ({item['language']})"
    if st.sidebar.button(btn_label, key=f"hist_{item['id']}", use_container_width=True):
        # TODO: Implement database detail fetch when clicking history items
        # Example: detail = requests.get(f"{BACKEND_URL}/api/history/{item['id']}").json()
        st.session_state.english_brd = f"# Mock BRD for {item['project_name']}\nDetails retrieved from history."
        st.session_state.localized_brd = f"# Localized Mock BRD for {item['project_name']}\nDetails translated."
        st.session_state.language = item['language']
        st.session_state.step = "completed"
        st.rerun()

st.sidebar.info("💡 Note: The history list above is currently mocked. Integrate the REST API to load database logs.")

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
            ["Hindi", "Tamil", "Telugu", "Kannada", "Bengali", "Spanish", "French"],
            index=0
        )
        st.session_state.language = lang_option
        
        input_type = st.radio("Choose Input Type:", ["🎙️ Audio File Upload", "✍️ Paste Text Notes"])
        
        raw_text_input = ""
        uploaded_file = None
        
        if input_type == "✍️ Paste Text Notes":
            raw_text_input = st.text_area(
                "Write or paste your messy notes here (any language - e.g., Hindi, Tamil, English):",
                placeholder="Example: Mujhe ek app chahiye jo dukaan ka hisaab rakhe. Dukandaar saara samaan enter kar sake, billing kar sake. Offline bhi chalna chahiye.",
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
                with st.spinner("Processing..."):
                    # TODO: Frontend Developer - Connect to backend endpoint `/api/start`
                    # Example payload construction:
                    # files = {"file": uploaded_file} if uploaded_file else None
                    # data = {"raw_text": raw_text_input, "language": lang_option}
                    # response = requests.post(f"{BACKEND_URL}/api/start", data=data, files=files).json()
                    
                    # Mock state transition
                    st.session_state.graph_state = {
                        "raw_input": raw_text_input if raw_text_input else "Uploaded Audio Path Mock",
                        "language": lang_option,
                        "cleaned_input": "Mock Cleaned Input"
                    }
                    st.session_state.questions = [
                        "Should this app run as a Mobile App, a Web App, or both?",
                        "Do you need automated inventory deduction when billing occurs?"
                    ]
                    st.session_state.step = "clarification"
                    st.rerun()
                        
    with col2:
        st.markdown("""
        <div class="glass-card" style="height: 100%;">
            <h4>🧠 Meet the Genie Multi-Agent Squad:</h4>
            <ul>
                <li><strong>🗣️ Input Processor</strong>: Transcribes voice and cleans up slang/noise into English.</li>
                <li><strong>🧠 Requirements Extractor</strong>: Sorts notes into problems, actors, features, and constraints.</li>
                <li><strong>❓ Clarification Agent</strong>: Identifies gaps and asks you smart follow-up questions.</li>
                <li><strong>🏗️ BRD Structuring Agent</strong>: Translates requirements into an official PM-ready draft.</li>
                <li><strong>✅ Quality Auditor</strong>: Checks the draft for consistency, omissions, and details.</li>
                <li><strong>🌍 Localization Agent</strong>: Translates the verified BRD back into your selected language!</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# ------------------------------------------
# STEP 2: CLARIFICATION CHAT
# ------------------------------------------
elif st.session_state.step == "clarification":
    st.markdown('<div class="glass-card"><h3>❓ Step 2: Clarifying Your Requirements</h3></div>', unsafe_allow_html=True)
    st.write("The Clarification Agent detected some ambiguities in your description. Please provide answers to continue.")

    questions = st.session_state.questions
    answers = []

    # Display question forms dynamically
    for idx, question in enumerate(questions):
        st.markdown(f"**Question {idx + 1}:** {question}")
        ans = st.text_input(f"Your answer to Question {idx + 1}:", key=f"q_{idx}")
        answers.append(ans)

    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("🏗️ Generate BRD"):
            # Ensure all questions have at least some answers
            processed_answers = [a if a.strip() else "Not specified" for a in answers]
            
            with st.spinner("Generating document..."):
                # TODO: Frontend Developer - Connect to backend `/api/clarify`
                # Example API request:
                # payload = {"state": st.session_state.graph_state, "answers": processed_answers}
                # response = requests.post(f"{BACKEND_URL}/api/clarify", json=payload).json()
                
                # Mock state transition
                st.session_state.english_brd = f"""# Business Requirements Document - Retail Billing App (Mock)
                
## 1. Executive Summary
Mock generated business requirement document.
                
## 2. Scope of Work
- **In Scope**: Billing client, offline synchronization.
- **Out of Scope**: Online credit card payment.

## 3. Mock Answers Log
- Q1 Answer: {processed_answers[0] if len(processed_answers) > 0 else 'N/A'}
- Q2 Answer: {processed_answers[1] if len(processed_answers) > 1 else 'N/A'}
"""
                st.session_state.localized_brd = f"""# [MOCK TRANSLATION TO {st.session_state.language.upper()}]
Business Requirements Document - Retail Billing App (Mock)
"""
                st.session_state.step = "completed"
                st.rerun()
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
    
    # Allow simple interactive edit/regeneration
    st.subheader("✏️ Edit and Regenerate")
    edit_col1, edit_col2 = st.columns([2, 1])
    
    with edit_col1:
        edit_notes = st.text_area("Need changes? Add feedback/revision requests here:", placeholder="Example: Add a feature for exporting sales reports to PDF.")
        if st.button("🔄 Regenerate BRD"):
            with st.spinner("Regenerating requirements document..."):
                # TODO: Frontend Developer - Connect to backend regeneration API path
                # Append feedback to input and trigger regenerate `/api/clarify` (or a direct edit API)
                st.session_state.english_brd += f"\n\n## Update (Revision Request)\n{edit_notes}"
                st.session_state.localized_brd += f"\n\n[MOCK TRANSLATION OF REVISION]\n{edit_notes}"
                st.rerun()
                    
    with edit_col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🆕 Create New BRD", use_container_width=True):
            st.session_state.step = "input"
            st.session_state.graph_state = {}
            st.session_state.questions = []
            st.session_state.answers = []
            st.session_state.english_brd = ""
            st.session_state.localized_brd = ""
            st.rerun()
