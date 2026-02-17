import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import re
from datetime import datetime
import os

# Page configuration
st.set_page_config(
    page_title="AI Email Assistant",
    page_icon="✉️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Get API URL from environment variables
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Custom CSS for better UX and visibility
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Force ALL headers to be BLACK and VISIBLE */
    h1, h2, h3, h4, h5, h6,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, 
    .stMarkdown h4, .stMarkdown h5, .stMarkdown h6,
    .css-10trblm, .css-1v0mbdj, .e16nr0p30 {
        color: #0761DB !important;
        font-weight: 600 !important;
    }
    
    /* Main header styling */
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5 !important;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 700;
    }
    
    /* Sidebar headers - FIXED */
    .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3,
    .css-1d391kg .stMarkdown h3 {
        color: #000000 !important;
        font-weight: 700 !important;
    }
    
    /* Sidebar text */
    .css-1d391kg, .css-1d391kg p, .css-1d391kg span {
        color: #1A1F36 !important;
    }
    
    /* Sidebar success/error messages */
    .css-1d391kg .stAlert {
        color: inherit !important;
    }
    
    /* Form labels - BLACK */
    .stTextInput label, .stTextArea label {
        font-weight: 600 !important;
        color: #C3BFDE !important;
        font-size: 1rem !important;
        margin-bottom: 0.3rem !important;
    }
    
    /* Input fields */
    .stTextInput input, .stTextArea textarea {
        border-radius: 8px !important;
        border: 1px solid #CCCCCC !important;
        padding: 0.6rem !important;
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    
    /* Input focus */
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #1E88E5 !important;
        box-shadow: 0 0 0 2px rgba(30, 136, 229, 0.2) !important;
    }
    
    /* Placeholder styling */
    input::placeholder, textarea::placeholder {
        color: #888888 !important;
        font-style: italic;
    }
    
    /* Button */
    .stButton button {
        background: #1E88E5 !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        width: 100%;
    }
    
    .stButton button:hover {
        background: #1565C0 !important;
    }
    
    /* Email preview card */
    .email-preview {
        background-color: #F5F5F5;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #1E88E5;
        color: #000000;
        font-size: 0.95rem;
        line-height: 1.5;
        border: 1px solid #E0E0E0;
        margin-top: 1rem;
    }
    
    /* Category badges */
    .category-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 16px;
        font-weight: 600;
        font-size: 0.85rem;
        margin-right: 0.5rem;
        border: 1px solid;
    }
    
    .badge-policy {
        background: #E3F2FD;
        color: #0D47A1;
        border-color: #90CAF9;
    }
    
    .badge-sensitive {
        background: #FFEBEE;
        color: #B71C1C;
        border-color: #EF9A9A;
    }
    
    .badge-general {
        background: #E8F5E9;
        color: #1B5E20;
        border-color: #A5D6A7;
    }
    
    .badge-clarification {
        background: #FFF3E0;
        color: #BF360C;
        border-color: #FFB74D;
    }
    
    /* Confidence meter */
    .confidence-high {
        color: #1B5E20;
        font-weight: 600;
        background: #E8F5E9;
        padding: 0.25rem 0.75rem;
        border-radius: 16px;
        display: inline-block;
        border: 1px solid #A5D6A7;
    }
    
    .confidence-medium {
        color: #BF360C;
        font-weight: 600;
        background: #FFF3E0;
        padding: 0.25rem 0.75rem;
        border-radius: 16px;
        display: inline-block;
        border: 1px solid #FFB74D;
    }
    
    .confidence-low {
        color: #B71C1C;
        font-weight: 600;
        background: #FFEBEE;
        padding: 0.25rem 0.75rem;
        border-radius: 16px;
        display: inline-block;
        border: 1px solid #EF9A9A;
    }
    
    /* Retrieved docs */
    .retrieved-docs {
        background: #F5F5F5;
        padding: 0.75rem;
        border-radius: 6px;
        border-left: 3px solid #FFA000;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
    
    /* Info box */
    .info-box {
        background: #F8F9FA;
        padding: 1.2rem;
        border-radius: 8px;
        border: 1px solid #E0E0E0;
        margin-top: 1rem;
    }
    
    .info-box-title {
        font-weight: 700;
        color: #000000 !important;
        margin-bottom: 0.5rem;
        font-size: 1rem;
    }
    
    .info-box-item {
        color: #333333 !important;
        margin: 0.4rem 0;
        padding-left: 1.2rem;
        position: relative;
    }
    
    .info-box-item:before {
        content: "•";
        color: #1E88E5;
        font-weight: bold;
        position: absolute;
        left: 0.2rem;
    }
    
    /* Success message */
    .success-message {
        background: #D4EDDA;
        color: #155724;
        padding: 0.75rem;
        border-radius: 6px;
        border-left: 4px solid #28A745;
        margin: 1rem 0;
    }
    
    /* Warning message */
    .warning-message {
        background: #FFF3CD;
        color: #856404;
        padding: 0.75rem;
        border-radius: 6px;
        border-left: 4px solid #FFC107;
        margin: 1rem 0;
    }
    
    /* Error message */
    .error-message {
        background: #F8D7DA;
        color: #721C24;
        padding: 0.75rem;
        border-radius: 6px;
        border-left: 4px solid #DC3545;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'email_history' not in st.session_state:
    st.session_state.email_history = []

# Helper functions
def check_api_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def format_email_text(text):
    """Convert markdown formatting to HTML for better display"""
    if not text:
        return text
    
    text = re.sub(r'^\* ', '• ', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    
    return text

def process_email(email_data):
    """Send email to API for processing"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/process-email",
            json=email_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            st.error("API quota exceeded. Please try again later.")
            return None
        else:
            st.error(f"Error: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        st.error("Request timed out. Please try again.")
        return None
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None

def get_confidence_class(score):
    """Get CSS class for confidence score"""
    if score >= 0.8:
        return "confidence-high"
    elif score >= 0.5:
        return "confidence-medium"
    else:
        return "confidence-low"

def get_category_badge(category):
    """Get CSS class for category badge"""
    badges = {
        "policy_query": "badge-policy",
        "sensitive_matter": "badge-sensitive",
        "general_inquiry": "badge-general",
        "clarification_needed": "badge-clarification"
    }
    return badges.get(category, "badge-general")

def get_category_display(category):
    """Get display name for category"""
    display_names = {
        "policy_query": "📋 Policy Query",
        "sensitive_matter": "⚠️ Sensitive Matter",
        "general_inquiry": "📧 General Inquiry",
        "clarification_needed": "❓ Clarification Needed"
    }
    return display_names.get(category, "📧 General Inquiry")

# Main app
def main():
    # Sidebar
    with st.sidebar:
        st.markdown("### AI Email Assistant")
        st.markdown("---")
        
        st.markdown("**🔌 CONNECTION**")
        api_healthy = check_api_health()
        if api_healthy:
            st.success("✅ Connected")
        else:
            st.error("❌ Disconnected")
            st.caption("Make sure backend is running")
            if st.button("🔄 Retry"):
                st.rerun()
        
        st.markdown("---")
        st.markdown("**🧭 NAVIGATION**")
        page = st.radio(
            "Go to",
            ["📧 Compose", "📋 History", "ℹ️ About"],
            label_visibility="collapsed"
        )

    # Main content
    if page == "📧 Compose":
        st.markdown("<h1 class='main-header'>AI Email Assistant</h1>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            st.markdown("### 📝 Compose Email")
            
            with st.form("email_form"):
                subject = st.text_input(
                    "Subject",
                    placeholder="e.g., Question about sick leave"
                )
                
                sender = st.text_input(
                    "From",
                    placeholder="e.g., employee@company.com"
                )
                
                recipient = st.text_input(
                    "To",
                    placeholder="e.g., hr@company.com (optional)"
                )
                
                body = st.text_area(
                    "Message",
                    placeholder="e.g., How many sick days do I get?",
                    height=200
                )
                
                submitted = st.form_submit_button(
                    "📨 Get Assistance",
                    use_container_width=True
                )
            
            if submitted:
                if not subject or not body or not sender:
                    st.error("Please fill all required fields")
                elif not api_healthy:
                    st.error("Backend not connected")
                else:
                    email_data = {
                        "subject": subject,
                        "body": body,
                        "sender": sender,
                        "recipient": recipient if recipient else None
                    }
                    
                    with st.spinner("Analyzing..."):
                        response = process_email(email_data)
                    
                    if response:
                        st.session_state.email_history.append({
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "subject": subject,
                            "sender": sender,
                            "response": response
                        })
                        
                        st.success("✅ Success!")
                        
                        with col2:
                            # Category and confidence
                            category = response.get('category', 'general_inquiry')
                            confidence = response.get('confidence_score', 0)
                            
                            badge_class = get_category_badge(category)
                            display_name = get_category_display(category)
                            
                            st.markdown(f'<span class="category-badge {badge_class}">{display_name}</span>', unsafe_allow_html=True)
                            st.markdown(f'<span class="{get_confidence_class(confidence)}">Confidence: {confidence:.1%}</span>', unsafe_allow_html=True)
                            
                            if response.get('retrieved_docs'):
                                with st.expander("📚 Retrieved Documents"):
                                    for doc in response['retrieved_docs']:
                                        st.markdown(f'<div class="retrieved-docs">📄 {doc.get("result", "")[:150]}...</div>', unsafe_allow_html=True)
                            
                            if response.get('requires_human_review'):
                                st.warning("🚨 Requires human review")
                            
                            if response.get('clarification_needed') and response.get('clarification_question'):
                                st.info(f"❓ {response['clarification_question']}")
                            
                            draft_reply = response.get('draft_reply', '')
                            formatted_reply = format_email_text(draft_reply).replace('\n', '<br>')
                            
                            st.markdown("**Draft Reply:**")
                            st.markdown(f'<div class="email-preview">{formatted_reply}</div>', unsafe_allow_html=True)
        
        with col2:
            if not submitted:
                st.info("👈 Fill form and click 'Get Assistance'")
                
                st.markdown("""
                <div class="info-box">
                    <div class="info-box-title">💡 Tips</div>
                    <div class="info-box-item">Ask about leave, WFH, benefits</div>
                    <div class="info-box-item">Be specific for better answers</div>
                    <div class="info-box-item">Sensitive matters auto-escalate</div>
                    <div class="info-box-item">Check history for past chats</div>
                </div>
                """, unsafe_allow_html=True)
    
    elif page == "📋 History":
        st.markdown("<h1 class='main-header'>Email History</h1>", unsafe_allow_html=True)
        
        if not st.session_state.email_history:
            st.info("No emails processed yet.")
        else:
            for item in reversed(st.session_state.email_history[-10:]):
                with st.expander(f"📧 {item['subject']}"):
                    st.write(f"**From:** {item['sender']}")
                    st.write(f"**Time:** {item['timestamp']}")
                    
                    response = item['response']
                    category = response.get('category', 'general_inquiry')
                    confidence = response.get('confidence_score', 0)
                    
                    badge_class = get_category_badge(category)
                    display_name = get_category_display(category)
                    
                    st.markdown(f'<span class="category-badge {badge_class}">{display_name}</span>', unsafe_allow_html=True)
                    
                    draft_reply = response.get('draft_reply', '')
                    formatted_reply = format_email_text(draft_reply)
                    
                    st.markdown("**Draft Reply:**")
                    st.markdown(f'<div class="email-preview">{formatted_reply}</div>', unsafe_allow_html=True)
            
            if st.button("Clear History"):
                st.session_state.email_history = []
                st.rerun()
    
    else:  # About
        st.markdown("<h1 class='main-header'>About</h1>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🤖 AI Email Assistant")
            st.markdown("""
            Automates email responses by:
            - Understanding intent
            - Searching policies (RAG)
            - Generating replies
            - Escalating sensitive matters
            """)
        
        with col2:
            st.markdown("### ✨ Features")
            st.markdown("""
            - Real-time processing
            - Document retrieval
            - Confidence scoring
            - Email history
            - Category classification
            - Human escalation
            """)

if __name__ == "__main__":
    main()