import streamlit as st
import config
from db.database import init_db


st.set_page_config(
    page_title="AI Interior Copilot",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_db()

if "current_design" not in st.session_state:
    st.session_state["current_design"] = None
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

st.markdown("""
<style>
    .stApp { background-color: #fafafa; }
    .main-header { font-size: 2.5rem; font-weight: bold; color: #1a1a2e; text-align: center; padding: 1rem 0; }
    .feature-card { background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border: 1px solid #e8e8e8; }
    .hero-section { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 16px; padding: 3rem; margin: 2rem 0; text-align: center; }
    .hero-title { color: white; font-size: 2.8rem; font-weight: bold; margin-bottom: 1rem; }
    .hero-subtitle { color: rgba(255,255,255,0.9); font-size: 1.2rem; margin-bottom: 2rem; }
    footer {display: none;}
    .stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)


with st.sidebar:
    st.title("🏠 AI Interior Copilot")
    
    st.divider()
    
    st.page_link("app.py", label="🏠 Home", icon="🏠")
    st.page_link("pages/1_Generate.py", label="✨ Generate", icon="🎨")
    st.page_link("pages/2_Results.py", label="📋 Results", icon="📊")
    st.page_link("pages/3_Saved_Designs.py", label="💾 Saved", icon="💾")
    
    st.divider()
    
    st.caption("Settings")

if not config.GROQ_API_KEY or config.GROQ_API_KEY == "your_groq_api_key_here":
    st.warning("Add GROQ_API_KEY to .env")

if not config.HF_TOKEN or config.HF_TOKEN == "your_huggingface_token_here":
    st.warning("Add HF_TOKEN to .env")


if "current_design" not in st.session_state or not st.session_state["current_design"]:
    st.markdown('<p class="main-header">AI Interior Design Copilot</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="hero-section">
        <p class="hero-title">Design Your Dream Room</p>
        <p class="hero-subtitle">Describe any room and get AI-generated design with furniture recommendations</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")
    
    f1, f2, f3 = st.columns(3)
    
    with f1:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #667eea;">🎨 AI Generation</h3>
            <p>Describe your dream room and get photorealistic AI-generated interior designs instantly.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with f2:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #667eea;">🛋️ Furniture Match</h3>
            <p>Get product recommendations matched by visual similarity to your generated design.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with f3:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #667eea;">💰 Budget Smart</h3>
            <p>Stay on budget with smart allocation and cheaper alternatives.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("")
    
    st.subheader("Example Designs")
    
    examples = [
        ("Living Room", "Modern", "A bright living room with large windows, comfortable sectional sofa, and minimal decor"),
        ("Bedroom", "Scandinavian", "Cozy bedroom with white walls, wooden bed frame, and warm lighting"),
        ("Home Office", "Minimalist", "Clean home office with standing desk, ergonomic chair, and plants")
    ]
    
    for room, style, prompt in examples:
        with st.expander(f"{room} - {style}"):
            st.write(prompt)
    
    st.markdown("")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("Start Creating", type="primary", use_container_width=True):
            st.switch_page("pages/1_Generate.py")
    
    with col2:
        if st.button("View Saved", use_container_width=True):
            st.switch_page("pages/3_Saved_Designs.py")
    
    with col3:
        pass

else:
    design = st.session_state.get("current_design")
    if design and isinstance(design, dict) and design.get("image_url"):
        st.switch_page("pages/2_Results.py")
    else:
        st.session_state["current_design"] = None
        st.switch_page("pages/1_Generate.py")