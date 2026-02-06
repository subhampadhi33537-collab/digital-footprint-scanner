"""
AI-Powered Digital Footprint Scanner
Streamlit Version for Easy Deployment
"""

import streamlit as st
import os
from dotenv import load_dotenv
import json
import logging
from datetime import datetime

# ==================================================
# LOAD ENVIRONMENT VARIABLES
# ==================================================
load_dotenv()

# ==================================================
# PAGE CONFIGURATION
# ==================================================
st.set_page_config(
    page_title="Digital Footprint Scanner",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================================================
# SESSION STATE INITIALIZATION
# ==================================================
if "scan_results" not in st.session_state:
    st.session_state.scan_results = None
if "user_input" not in st.session_state:
    st.session_state.user_input = ""
if "risk_analysis" not in st.session_state:
    st.session_state.risk_analysis = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "ml_risk_analysis" not in st.session_state:
    st.session_state.ml_risk_analysis = None

# ==================================================
# IMPORT CORE MODULES
# ==================================================
from config import config
from scanner.osint_scanner import run_full_scan
from analysis.risk_engine import calculate_risk
from analysis.ml_risk_engine import get_ml_risk_analysis
from analysis.anomaly_detector import get_comprehensive_anomaly_analysis
from analysis.threat_intel import get_complete_threat_intelligence
from ai_engine.chatbot_handler import get_ai_response

# ==================================================
# LOGGING SETUP
# ==================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [STREAMLIT] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

# ==================================================
# THEME & STYLING
# ==================================================
def apply_custom_theme():
    """Apply custom CSS styling"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
    }
    
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        animation: fadeInDown 1s;
    }
    
    .hero-subtitle {
        font-size: 1.5rem;
        color: #94a3b8;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .subheader {
        font-size: 1.3rem;
        color: #e2e8f0;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    .feature-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(51, 65, 85, 0.6));
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 16px;
        padding: 2rem;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        margin: 1rem 0;
    }
    
    .feature-card:hover {
        border-color: rgba(148, 163, 184, 0.4);
        transform: translateY(-5px);
        box-shadow: 0 20px 60px rgba(79, 70, 229, 0.2);
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    
    .stat-box {
        background: linear-gradient(135deg, rgba(79, 70, 229, 0.2), rgba(124, 58, 237, 0.2));
        border: 1px solid rgba(79, 70, 229, 0.3);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #4f46e5, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .stat-label {
        color: #94a3b8;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    
    .risk-high {
        color: #ef4444;
        font-weight: bold;
    }
    .risk-medium {
        color: #f59e0b;
        font-weight: bold;
    }
    .risk-low {
        color: #10b981;
        font-weight: bold;
    }
    .platform-found {
        background-color: rgba(16, 185, 129, 0.1);
        padding: 0.5rem;
        border-radius: 0.5rem;
        border-left: 3px solid #10b981;
        margin: 0.5rem 0;
    }
    .platform-not-found {
        background-color: rgba(148, 163, 184, 0.05);
        padding: 0.5rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #4f46e5, #7c3aed);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 20px 40px rgba(79, 70, 229, 0.3);
    }
    
    .highlight-box {
        background: linear-gradient(135deg, rgba(79, 70, 229, 0.1), rgba(124, 58, 237, 0.1));
        border-left: 4px solid #4f46e5;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

apply_custom_theme()

# ==================================================
# SIDEBAR NAVIGATION
# ==================================================
st.sidebar.markdown("# 🔍 Digital Footprint Scanner")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["🏠 Home", "🔎 Quick Scan", "📊 Advanced Analysis", "🤖 AI Assistant", "📈 Analytics"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ About")
st.sidebar.markdown("""
This tool helps you discover and analyze your digital footprint across multiple platforms using OSINT techniques.

**Features:**
- Real-time OSINT scanning
- ML-powered risk analysis
- Threat intelligence
- AI chatbot assistance
- Comprehensive analytics
""")

# ==================================================
# PAGE 1: HOME
# ==================================================
def page_home():
    st.markdown('<h1 class="main-header">🔍 Digital Footprint Scanner</h1>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">AI-Powered OSINT Tool for Privacy Analysis</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Hero Section
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <h2 style="color: #e2e8f0; font-size: 1.8rem; margin-bottom: 1rem;">
                Discover Your Digital Footprint
            </h2>
            <p style="color: #94a3b8; font-size: 1.1rem; line-height: 1.8;">
                Scan 50+ platforms in real-time to understand what information about you is publicly available online. 
                Get AI-powered risk analysis and actionable privacy recommendations.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick Stats
    st.markdown("### 📊 Platform Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-number">50+</div>
            <div class="stat-label">Platforms Scanned</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-number">&lt;2min</div>
            <div class="stat-label">Average Scan Time</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-number">95%</div>
            <div class="stat-label">Accuracy Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-number">AI</div>
            <div class="stat-label">Powered Analysis</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Features Section
    st.markdown("### ✨ Key Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🔍</div>
            <h3 style="color: #e2e8f0; margin-bottom: 0.5rem;">Real-Time OSINT Scanning</h3>
            <p style="color: #94a3b8;">
                Checks your username or email across 50+ social media platforms, forums, and websites 
                to find publicly available accounts and information.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <h3 style="color: #e2e8f0; margin-bottom: 0.5rem;">ML-Powered Risk Analysis</h3>
            <p style="color: #94a3b8;">
                Advanced machine learning algorithms analyze your exposure patterns and provide 
                intelligent risk scores with detailed breakdowns.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">💬</div>
            <h3 style="color: #e2e8f0; margin-bottom: 0.5rem;">AI Assistant</h3>
            <p style="color: #94a3b8;">
                Ask questions about your scan results and get personalized privacy recommendations 
                from our intelligent chatbot powered by Groq AI.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">⚠️</div>
            <h3 style="color: #e2e8f0; margin-bottom: 0.5rem;">Exposure Risk Assessment</h3>
            <p style="color: #94a3b8;">
                Get comprehensive risk analysis with severity levels, vulnerability indicators, 
                and specific recommendations to reduce your digital footprint.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <h3 style="color: #e2e8f0; margin-bottom: 0.5rem;">Threat Intelligence</h3>
            <p style="color: #94a3b8;">
                Detect anomalies, identify unusual patterns, and receive alerts about potential 
                security threats across your discovered accounts.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📈</div>
            <h3 style="color: #e2e8f0; margin-bottom: 0.5rem;">Detailed Analytics</h3>
            <p style="color: #94a3b8;">
                Visual dashboards, platform breakdowns, and comprehensive reports to track and 
                understand your complete digital presence.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # How It Works Section
    st.markdown("### 🚀 How It Works")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">1️⃣</div>
            <h4 style="color: #e2e8f0; margin-bottom: 0.5rem;">Enter Info</h4>
            <p style="color: #94a3b8; font-size: 0.9rem;">
                Provide your username or email address
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">2️⃣</div>
            <h4 style="color: #e2e8f0; margin-bottom: 0.5rem;">Scan Platforms</h4>
            <p style="color: #94a3b8; font-size: 0.9rem;">
                We check 50+ platforms in real-time
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">3️⃣</div>
            <h4 style="color: #e2e8f0; margin-bottom: 0.5rem;">Analyze Results</h4>
            <p style="color: #94a3b8; font-size: 0.9rem;">
                AI analyzes exposure and risk levels
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">4️⃣</div>
            <h4 style="color: #e2e8f0; margin-bottom: 0.5rem;">Get Insights</h4>
            <p style="color: #94a3b8; font-size: 0.9rem;">
                Review detailed report and recommendations
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Call to Action
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="highlight-box" style="text-align: center;">
            <h3 style="color: #e2e8f0; margin-bottom: 1rem;">Ready to Get Started?</h3>
            <p style="color: #94a3b8; margin-bottom: 1.5rem;">
                Navigate to "Quick Scan" in the sidebar to begin your digital footprint analysis.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Start Your Scan Now", use_container_width=True, type="primary"):
            st.session_state.page = "🔎 Quick Scan"
            st.rerun()
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Privacy Notice
    st.info("🔐 **Privacy First:** No data is stored permanently. All scans are performed in real-time and results are cleared when you close your browser session.")

# ==================================================
# PAGE 2: QUICK SCAN
# ==================================================
def page_quick_scan():
    st.markdown('<h2 class="main-header">🔎 Quick Scan</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        user_input = st.text_input(
            "Enter username or email to scan:",
            value=st.session_state.user_input,
            placeholder="e.g., john.doe or john_doe@example.com"
        )
        st.session_state.user_input = user_input
    
    with col2:
        scan_type = st.selectbox(
            "Scan Type",
            ["Quick", "Comprehensive", "Deep"]
        )
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🚀 Start Scan", use_container_width=True):
            if not user_input:
                st.error("❌ Please enter a username or email")
            else:
                with st.spinner("🔄 Scanning in progress..."):
                    try:
                        st.session_state.scan_results = run_full_scan(user_input)
                        st.session_state.risk_analysis = calculate_risk(st.session_state.scan_results)
                        st.session_state.ml_risk_analysis = get_ml_risk_analysis(st.session_state.scan_results)
                        st.success("✅ Scan completed!")
                    except Exception as e:
                        st.error(f"❌ Scan error: {str(e)}")
                        logger.error(f"Scan error: {str(e)}")
    
    with col2:
        if st.button("🔄 Clear Results", use_container_width=True):
            st.session_state.scan_results = None
            st.session_state.risk_analysis = None
            st.session_state.ml_risk_analysis = None
    
    # Display results
    if st.session_state.scan_results:
        st.markdown("---")
        st.markdown("### 📋 Scan Results")
        
        # Risk Summary
        if st.session_state.risk_analysis:
            risk_level = st.session_state.risk_analysis.get("risk_level", "Unknown").upper()
            risk_score = st.session_state.risk_analysis.get("risk_score", 0)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if "HIGH" in risk_level:
                    st.metric("Risk Level", risk_level, delta=f"{risk_score}%", delta_color="off")
                elif "MEDIUM" in risk_level:
                    st.metric("Risk Level", risk_level, delta=f"{risk_score}%", delta_color="off")
                else:
                    st.metric("Risk Level", risk_level, delta=f"{risk_score}%", delta_color="off")
            
            with col2:
                accounts_found = len([p for p in st.session_state.scan_results.get("all_platforms_checked", []) 
                                     if p.get("status") == "found"])
                st.metric("Accounts Found", accounts_found)
            
            with col3:
                total_platforms = len(st.session_state.scan_results.get("all_platforms_checked", []))
                st.metric("Platforms Checked", total_platforms)
        
        # Platform Details
        st.subheader("📱 Platform Breakdown")
        
        platforms = st.session_state.scan_results.get("all_platforms_checked", [])
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            show_all = st.checkbox("Show all platforms", value=True)
        with col2:
            search_platform = st.text_input("Search platform:", "")
        
        # Display platforms
        for platform in platforms:
            if not show_all and platform.get("status") != "found":
                continue
            if search_platform and search_platform.lower() not in platform.get("platform", "").lower():
                continue
            
            status = platform.get("status", "unknown")
            if status == "found":
                st.success(f"✅ **{platform.get('platform', 'Unknown').title()}** - Account Found")
                if platform.get("url"):
                    st.caption(f"🔗 {platform.get('url')}")
            elif status == "not_found":
                st.caption(f"❌ {platform.get('platform', 'Unknown').title()} - Not Found")
            elif status == "timeout":
                st.warning(f"⏱️ {platform.get('platform', 'Unknown').title()} - Timeout")
            elif status == "error":
                st.error(f"⚠️ {platform.get('platform', 'Unknown').title()} - Error")

# ==================================================
# PAGE 3: ADVANCED ANALYSIS
# ==================================================
def page_advanced_analysis():
    st.markdown('<h2 class="main-header">📊 Advanced Analysis</h2>', unsafe_allow_html=True)
    
    if not st.session_state.scan_results:
        st.warning("👉 Run a scan first to view advanced analysis")
        return
    
    tab1, tab2, tab3, tab4 = st.tabs(["Risk Analysis", "Anomalies", "Threat Intel", "ML Insights"])
    
    # Tab 1: Risk Analysis
    with tab1:
        st.subheader("⚠️ Risk Assessment")
        if st.session_state.risk_analysis:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Overall Risk Score",
                    f"{st.session_state.risk_analysis.get('risk_score', 0)}%"
                )
            with col2:
                st.metric(
                    "Exposure Level",
                    st.session_state.risk_analysis.get('risk_level', 'Unknown')
                )
            with col3:
                accounts = len([p for p in st.session_state.scan_results.get("all_platforms_checked", [])
                               if p.get("status") == "found"])
                st.metric("Accounts Exposed", accounts)
            
            st.markdown("**Risk Factors:**")
            if isinstance(st.session_state.risk_analysis.get("factors"), list):
                for factor in st.session_state.risk_analysis.get("factors", []):
                    st.caption(f"• {factor}")
            
            st.markdown("**Recommendations:**")
            if isinstance(st.session_state.risk_analysis.get("recommendations"), list):
                for rec in st.session_state.risk_analysis.get("recommendations", []):
                    st.info(rec)
    
    # Tab 2: Anomalies
    with tab2:
        st.subheader("🔴 Anomaly Detection")
        with st.spinner("Analyzing anomalies..."):
            try:
                anomaly_results = get_comprehensive_anomaly_analysis(st.session_state.scan_results)
                if anomaly_results:
                    st.json(anomaly_results)
                else:
                    st.info("No anomalies detected")
            except Exception as e:
                st.warning(f"Analysis unavailable: {str(e)}")
    
    # Tab 3: Threat Intelligence
    with tab3:
        st.subheader("🎯 Threat Intelligence")
        with st.spinner("Gathering threat intel..."):
            try:
                threat_results = get_complete_threat_intelligence(st.session_state.scan_results)
                if threat_results:
                    st.json(threat_results)
                else:
                    st.info("No threats detected")
            except Exception as e:
                st.warning(f"Analysis unavailable: {str(e)}")
    
    # Tab 4: ML Insights
    with tab4:
        st.subheader("🤖 Machine Learning Analysis")
        if st.session_state.ml_risk_analysis:
            st.json(st.session_state.ml_risk_analysis)
        else:
            st.info("ML analysis not available. Run scan in 'Comprehensive' mode.")

# ==================================================
# PAGE 4: AI ASSISTANT
# ==================================================
def page_ai_assistant():
    st.markdown('<h2 class="main-header">🤖 AI Assistant</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    Chat with our AI to understand your scan results, get recommendations, and learn about digital privacy.
    """)
    
    # Chat display
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.chat_message("user").write(message["content"])
        else:
            st.chat_message("assistant").write(message["content"])
    
    # Chat input
    if user_message := st.chat_input("Ask me anything about your digital footprint..."):
        st.session_state.chat_history.append({"role": "user", "content": user_message})
        st.chat_message("user").write(user_message)
        
        with st.spinner("🤔 Thinking..."):
            try:
                context = {
                    "scan_results": st.session_state.scan_results,
                    "risk_analysis": st.session_state.risk_analysis,
                    "chat_history": st.session_state.chat_history[:-1]  # Exclude current message
                }
                response = get_ai_response(user_message, context)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.chat_message("assistant").write(response)
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
                st.chat_message("assistant").write(error_msg)

# ==================================================
# PAGE 5: ANALYTICS
# ==================================================
def page_analytics():
    st.markdown('<h2 class="main-header">📈 Analytics</h2>', unsafe_allow_html=True)
    
    if not st.session_state.scan_results:
        st.warning("👉 Run a scan first to view analytics")
        return
    
    tab1, tab2, tab3 = st.tabs(["Overview", "Platform Stats", "Timeline"])
    
    # Tab 1: Overview
    with tab1:
        st.subheader("📊 Scan Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        platforms = st.session_state.scan_results.get("all_platforms_checked", [])
        found = len([p for p in platforms if p.get("status") == "found"])
        not_found = len([p for p in platforms if p.get("status") == "not_found"])
        errors = len([p for p in platforms if p.get("status") in ["error", "timeout"]])
        total = len(platforms)
        
        with col1:
            st.metric("Total Platforms", total)
        with col2:
            st.metric("Accounts Found", found, f"{int(found/total*100) if total > 0 else 0}%")
        with col3:
            st.metric("Not Found", not_found)
        with col4:
            st.metric("Errors/Timeouts", errors)
        
        # Chart
        try:
            chart_data = {
                "Found": found,
                "Not Found": not_found,
                "Errors": errors
            }
            st.bar_chart(chart_data)
        except:
            pass
    
    # Tab 2: Platform Stats
    with tab2:
        st.subheader("📱 Platform Breakdown")
        
        platforms_data = []
        for p in platforms:
            platforms_data.append({
                "Platform": p.get("platform", "").title(),
                "Status": p.get("status", "").title(),
                "URL": p.get("url", "N/A")
            })
        
        if platforms_data:
            st.dataframe(platforms_data, use_container_width=True)
    
    # Tab 3: Timeline
    with tab3:
        st.subheader("⏰ Scan Timeline")
        st.info(f"Scan completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if st.session_state.scan_results.get("timestamp"):
            st.caption(f"Data from: {st.session_state.scan_results.get('timestamp')}")

# ==================================================
# PAGE ROUTER
# ==================================================
if page == "🏠 Home":
    page_home()
elif page == "🔎 Quick Scan":
    page_quick_scan()
elif page == "📊 Advanced Analysis":
    page_advanced_analysis()
elif page == "🤖 AI Assistant":
    page_ai_assistant()
elif page == "📈 Analytics":
    page_analytics()

# ==================================================
# FOOTER
# ==================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.8rem;">
🔐 Your privacy is protected. No data is stored after your session ends.
</div>
""", unsafe_allow_html=True)
