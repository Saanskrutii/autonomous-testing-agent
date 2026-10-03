import os
import streamlit as st
from dotenv import load_dotenv
from src.code_analyzer import analyze_repository
from src.agent import run_agent
from src.tools import clone_github_repo, prepare_repo_for_import

load_dotenv()

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Autonomous Testing Agent",
    page_icon="assets/favicon.png" if os.path.exists("assets/favicon.png") else None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Background */
.stApp {
    background: #0d0f14;
    color: #e2e8f0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #111318 !important;
    border-right: 1px solid #1e2330 !important;
}

[data-testid="stSidebar"] * {
    color: #c8d0de !important;
}

/* Header strip */
.header-strip {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 28px 36px;
    margin-bottom: 28px;
}

.header-strip h1 {
    font-size: 1.8rem;
    font-weight: 700;
    color: #f1f5f9;
    margin: 0 0 6px 0;
    letter-spacing: -0.5px;
}

.header-strip p {
    font-size: 0.88rem;
    color: #64748b;
    margin: 0;
}

.badge {
    display: inline-block;
    background: #0ea5e910;
    border: 1px solid #0ea5e9;
    color: #38bdf8;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.75rem;
    font-weight: 500;
    margin-right: 6px;
    margin-bottom: 12px;
}

/* Cards */
.card {
    background: #111318;
    border: 1px solid #1e2330;
    border-radius: 12px;
    padding: 24px;
}

/* Section labels */
.section-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: #475569;
    margin-bottom: 10px;
}

/* Metric cards */
.metric-row {
    display: flex;
    gap: 16px;
    margin-top: 20px;
}

.metric-card {
    flex: 1;
    background: #111318;
    border: 1px solid #1e2330;
    border-radius: 10px;
    padding: 18px 20px;
    text-align: center;
}

.metric-card .val {
    font-size: 1.6rem;
    font-weight: 700;
    color: #38bdf8;
}

.metric-card .lbl {
    font-size: 0.76rem;
    color: #64748b;
    margin-top: 4px;
}

/* Status pill */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #052e16;
    border: 1px solid #166534;
    color: #4ade80;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.8rem;
    font-weight: 500;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #0ea5e9, #3b82f6) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    padding: 10px 22px !important;
    transition: opacity 0.2s ease !important;
    letter-spacing: 0.3px !important;
}

.stButton > button:hover {
    opacity: 0.88 !important;
}

/* Inputs */
.stTextInput > div > div > input,
.stSelectbox > div > div {
    background: #1a1f2e !important;
    border: 1px solid #2a3347 !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: #111318 !important;
    border: 1.5px dashed #2a3347 !important;
    border-radius: 10px !important;
}

/* Divider */
hr {
    border-color: #1e2330 !important;
    margin: 20px 0 !important;
}

/* Tabs */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid #1e2330 !important;
    gap: 8px;
}

[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    color: #64748b !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    border-bottom: 2px solid transparent !important;
    padding: 8px 16px !important;
}

[data-testid="stTabs"] [aria-selected="true"] {
    color: #38bdf8 !important;
    border-bottom: 2px solid #38bdf8 !important;
}

/* Code block */
.stCodeBlock {
    border-radius: 10px !important;
    border: 1px solid #1e2330 !important;
}

/* Sidebar selectbox label */
.stSidebar .stSelectbox label,
.stSidebar .stTextInput label {
    font-size: 0.8rem !important;
    color: #94a3b8 !important;
    font-weight: 500 !important;
    letter-spacing: 0.5px !important;
}

/* Hide Streamlit branding */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-strip">
    <h1>Autonomous Software Testing Agent</h1>
    <p>AI-powered code analysis, pytest generation, self-healing retries, and coverage reporting.</p>
    <div style="margin-top:14px;">
        <span class="badge">AST Analysis</span>
        <span class="badge">LangGraph</span>
        <span class="badge">Pytest</span>
        <span class="badge">Self-Healing</span>
        <span class="badge">Coverage</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-label">Model Configuration</div>', unsafe_allow_html=True)

    selected_model = st.selectbox(
        "LLM Provider",
        ["gemini-2.5-flash", "gemini-3.8-flash"],
        label_visibility="visible"
    )
    os.environ["GEMINI_MODEL"] = selected_model  # wire to nodes.py

    api_key_input = st.text_input(
        "Gemini API Key Override",
        type="password",
        placeholder="Leave blank to use .env",
        value=""
    )

    if api_key_input:
        os.environ["GEMINI_API_KEY"] = api_key_input

    st.divider()

    st.markdown('<div class="section-label">Agent Pipeline</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.8rem; color:#475569; line-height:1.9;">
        1. AST Parser &nbsp;→&nbsp; Structural analysis<br>
        2. LangGraph &nbsp;→&nbsp; Planning graph<br>
        3. Code Generator &nbsp;→&nbsp; Pytest suite<br>
        4. Executor &nbsp;→&nbsp; Run &amp; measure<br>
        5. Self-Healer &nbsp;→&nbsp; Fix failing tests
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown('<div style="font-size:0.75rem; color:#334155;">Autonomous Testing Agent v1.0</div>', unsafe_allow_html=True)

# ── Main Layout ───────────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 1.8], gap="large")

with col1:
    st.markdown('<div class="section-label">Repository Input</div>', unsafe_allow_html=True)

    # Persist active repo across reruns
    if "target_repo" not in st.session_state:
        st.session_state["target_repo"] = "sample_repo"

    tab_upload, tab_github = st.tabs(["📁 Upload Files", "🔗 GitHub URL"])

    with tab_upload:
        uploaded_files = st.file_uploader(
            "Upload Python files",
            type=["py"],
            accept_multiple_files=True,
            help="Upload one or more .py files from your repository"
        )
        if uploaded_files:
            upload_dir = "uploaded_repo"
            os.makedirs(upload_dir, exist_ok=True)
            for file in uploaded_files:
                file_path = os.path.join(upload_dir, file.name)
                with open(file_path, "wb") as f:
                    f.write(file.getbuffer())
            prepare_repo_for_import(upload_dir)
            st.session_state["target_repo"] = upload_dir
            st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully.")

    with tab_github:
        github_url = st.text_input(
            "GitHub Repository URL",
            placeholder="https://github.com/username/repository",
            help="Public GitHub repos only. Cloned with --depth=1 (no auth required)."
        )
        clone_clicked = st.button("🔗 Clone Repository", use_container_width=True)
        if clone_clicked:
            if github_url.strip():
                with st.spinner("Cloning repository... (this may take a moment)"):
                    success, msg = clone_github_repo(github_url.strip())
                if success:
                    prepare_repo_for_import("cloned_repo")
                    st.session_state["target_repo"] = "cloned_repo"
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")
            else:
                st.warning("Please enter a GitHub URL first.")

    target_repo = st.session_state.get("target_repo", "sample_repo")
    st.markdown(
        f'<div style="font-size:0.78rem; color:#475569; margin-top:10px;">'
        f'📂 Active repo: <code style="color:#38bdf8;">{target_repo}</code></div>',
        unsafe_allow_html=True
    )

    st.markdown("---")

    scan_clicked = st.button("Scan Repository Structure", use_container_width=True)

    if scan_clicked:
        if os.path.exists(target_repo):
            with st.spinner("Running AST analysis..."):
                structure = analyze_repository(target_repo)
                st.session_state["structure"] = structure
        else:
            st.error(f"Directory '{target_repo}' not found.")

    if "structure" in st.session_state:
        st.markdown('<div class="section-label" style="margin-top:16px;">AST Structure</div>', unsafe_allow_html=True)
        st.json(st.session_state["structure"])

with col2:
    st.markdown('<div class="section-label">Agent Execution</div>', unsafe_allow_html=True)

    run_clicked = st.button("Run Autonomous Testing Workflow", type="primary", use_container_width=True)

    if run_clicked:
        target_repo = st.session_state.get("target_repo", "sample_repo")
        if not os.path.exists(target_repo):
            st.error(f"Repository path '{target_repo}' not found. Please upload files or clone a repo first.")
        else:
            status_box = st.status("Agent initializing...", expanded=True)

            with status_box:
                st.write("Phase 1 — Analyzing Python AST structure...")
                st.write("Phase 2 — Formulating edge-case test plan...")
                st.write("Phase 3 — Generating pytest code suite...")
                st.write("Phase 4 — Executing tests and measuring coverage...")

                final_state = run_agent(target_repo)

                status_box.update(label="Workflow completed successfully.", state="complete", expanded=False)

            st.markdown("---")

            # Metrics
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Pass Rate", f"{final_state.get('pass_rate', 0.0):.1f}%")
            m2.metric("Coverage", f"{final_state.get('coverage_percentage', 0.0):.1f}%")
            m3.metric("Iterations", final_state.get("iteration", 0))
            m4.metric("Status", final_state.get("status", "—").upper())

            st.markdown("---")

            # Result tabs
            tab1, tab2, tab3 = st.tabs(["Generated Tests", "Execution Logs", "Test Plan"])

            with tab1:
                test_code = final_state.get("generated_test_code", "# No code generated")
                st.code(test_code, language="python")
                st.download_button(
                    label="⬇️ Download Test File",
                    data=test_code,
                    file_name="test_generated.py",
                    mime="text/x-python",
                    use_container_width=True
                )

            with tab2:
                st.text_area(
                    "Terminal output",
                    value=final_state.get("test_output", ""),
                    height=320,
                    label_visibility="collapsed"
                )

            with tab3:
                st.write(final_state.get("test_plan", []))
