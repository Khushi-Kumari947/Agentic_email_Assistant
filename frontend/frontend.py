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
    
    /* Main header styling */
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5 !important;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 700;
    }
    
    /* Force ALL headers to be dark and visible */
    h1, h2, h3, h4, h5, h6 {
        color: #000000 !important;
        font-weight: 700 !important;
        margin-bottom: 0.8rem !important;
    }
    
    /* Specific targeting for Streamlit elements */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, 
    .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #000000 !important;
        font-weight: 700 !important;
    }
    
    /* Target the "Email Details" and similar headers */
    .element-container .stMarkdown h3 {
        color: #000000 !important;
        font-size: 1.3rem !important;
        border-bottom: 2px solid #1E88E5 !important;
        padding-bottom: 0.3rem !important;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        color: #000000 !important;
        margin-bottom: 1.2rem !important;
        padding-bottom: 0.5rem !important;
        border-bottom: 3px solid #1E88E5 !important;
    }
    
    /* Form labels - Now dark and visible */
    .stTextInput label, .stTextArea label {
        font-weight: 600 !important;
        color: #000000 !important;
        font-size: 1rem !important;
        margin-bottom: 0.3rem !important;
    }
    
    /* Input field styling */
    .stTextInput input, .stTextArea textarea {
        border-radius: 12px !important;
        border: 2px solid #E0E0E0 !important;
        padding: 0.75rem 1rem !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease !important;
        background-color: #FFFFFF !important;
        color: #1A1F36 !important;
        caret-color: #1E88E5 !important;
    }
    
    /* Input focus state */
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #1E88E5 !important;
        box-shadow: 0 0 0 4px rgba(30, 136, 229, 0.1) !important;
        background-color: #FFFFFF !important;
        outline: none !important;
    }
    
    /* Placeholder styling */
    input::placeholder, textarea::placeholder {
        color: #9E9E9E !important;
        font-size: 0.9rem !important;
        font-style: italic;
    }
    
    /* Required field indicator */
    .stTextInput label:after {
        content: " *";
        color: #E53E3E;
        font-weight: 600;
    }
    
    /* Optional field indicator */
    .stTextInput:has(input[placeholder*="Optional"]) label:after,
    .stTextArea:has(textarea[placeholder*="Optional"]) label:after {
        content: " (optional)";
        color: #757575;
        font-weight: 400;
        font-size: 0.85rem;
    }
    
    /* Button styling */
    .stButton button {
        background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-size: 1rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 12px rgba(30, 136, 229, 0.3) !important;
        width: 100%;
    }
    
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(30, 136, 229, 0.4) !important;
    }
    
    /* Email preview card */
    .email-preview {
        background-color: #F8F9FA;
        padding: 1.5rem;
        border-radius: 16px;
        border-left: 4px solid #1E88E5;
        font-family: 'Inter', sans-serif;
        white-space: pre-wrap;
        color: #1A1F36;
        font-size: 0.95rem;
        line-height: 1.6;
        border: 1px solid #E0E0E0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-top: 1rem;
    }
    
    /* Category badges */
    .category-badge {
        display: inline-block;
        padding: 0.4rem 1.2rem;
        border-radius: 30px;
        font-weight: 600;
        font-size: 0.9rem;
        margin-right: 0.75rem;
        margin-bottom: 0.75rem;
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
        padding: 0.4rem 1.2rem;
        border-radius: 30px;
        display: inline-block;
        border: 1px solid #A5D6A7;
    }
    
    .confidence-medium {
        color: #BF360C;
        font-weight: 600;
        background: #FFF3E0;
        padding: 0.4rem 1.2rem;
        border-radius: 30px;
        display: inline-block;
        border: 1px solid #FFB74D;
    }
    
    .confidence-low {
        color: #B71C1C;
        font-weight: 600;
        background: #FFEBEE;
        padding: 0.4rem 1.2rem;
        border-radius: 30px;
        display: inline-block;
        border: 1px solid #EF9A9A;
    }
    
    /* Retrieved docs section */
    .retrieved-docs {
        background-color: #F5F5F5;
        padding: 1rem;
        border-radius: 12px;
        border-left: 4px solid #FFA000;
        margin: 0.75rem 0;
        color: #1A1F36;
        font-size: 0.9rem;
        border: 1px solid #E0E0E0;
    }
    
    /* Success message */
    .success-message {
        background-color: #D4EDDA;
        color: #155724;
        padding: 1rem;
        border-radius: 12px;
        font-weight: 500;
        margin: 1rem 0;
        border: 1px solid #C3E6CB;
    }
    
    /* Warning message */
    .warning-message {
        background-color: #FFF3CD;
        color: #856404;
        padding: 1rem;
        border-radius: 12px;
        font-weight: 500;
        margin: 1rem 0;
        border: 1px solid #FFEEBA;
    }
    
    /* Error message */
    .error-message {
        background-color: #F8D7DA;
        color: #721C24;
        padding: 1rem;
        border-radius: 12px;
        font-weight: 500;
        margin: 1rem 0;
        border: 1px solid #F5C6CB;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #F8F9FA;
    }
    
    .sidebar-header {
        font-size: 1rem;
        font-weight: 700;
        color: #1E88E5 !important;
        margin: 1.5rem 0 0.75rem 0;
        letter-spacing: 0.02em;
        text-transform: uppercase;
    }
    
    /* Info box for tips */
    .info-box {
        background-color: #F0F7FF;
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid #BBDEFB;
        margin-top: 1.5rem;
    }
    
    .info-box-title {
        font-weight: 700;
        color: #0D47A1 !important;
        margin-bottom: 0.75rem;
        font-size: 1.1rem;
    }
    
    .info-box-item {
        color: #1A1F36 !important;
        margin: 0.5rem 0;
        padding-left: 1.5rem;
        position: relative;
    }
    
    .info-box-item:before {
        content: "•";
        color: #1E88E5;
        font-weight: bold;
        position: absolute;
        left: 0.5rem;
    }
    
    /* Make all text in info box dark */
    .info-box p, .info-box div, .info-box span {
        color: #1A1F36 !important;
    }
    
    /* Force "Quick Tips" header to be dark */
    .info-box h1, .info-box h2, .info-box h3, .info-box h4 {
        color: #0D47A1 !important;
        font-weight: 700 !important;
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
    
    # Handle bullet points
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
        st.markdown("### ✉️ AI Email Assistant")
        st.markdown("---")
        
        # API Status
        st.markdown("🔌 **CONNECTION**")
        api_healthy = check_api_health()
        if api_healthy:
            st.success("✅ Connected to backend")
        else:
            st.error("❌ Disconnected")
            st.caption("Make sure FastAPI server is running")
            if st.button("🔄 Retry Connection", use_container_width=True):
                st.rerun()
        
        st.markdown("---")
        
        # Navigation
        st.markdown("🧭 **NAVIGATION**")
        page = st.radio(
            "Go to",
            ["📧 Compose Email", "📋 History", "ℹ️ About"],
            label_visibility="collapsed"
        )

    # Main content area
    if page == "📧 Compose Email":
        st.markdown("<h1 class='main-header'>AI Email Assistant</h1>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            st.markdown("## 📝 Compose Email")  # Using markdown directly
            
            with st.form("email_form"):
                st.markdown("### Email Details")
                
                subject = st.text_input(
                    "Subject",
                    placeholder="e.g., Question about sick leave policy",
                    help="Enter the email subject line"
                )
                
                sender = st.text_input(
                    "From",
                    placeholder="e.g., john.doe@company.com",
                    help="Your email address"
                )
                
                recipient = st.text_input(
                    "To",
                    placeholder="e.g., hr@company.com",
                    help="Recipient email address (optional)"
                )
                
                body = st.text_area(
                    "Message",
                    placeholder="e.g., How many sick days do I get per year? Do I need a doctor's note?",
                    height=200,
                    help="Type your email content here"
                )
                
                submitted = st.form_submit_button(
                    "📨 Get Assistance",
                    use_container_width=True
                )
            
            if submitted:
                if not subject or not body or not sender:
                    st.error("Please fill in all required fields")
                elif not api_healthy:
                    st.error("API is not connected. Please check the backend server.")
                else:
                    email_data = {
                        "subject": subject,
                        "body": body,
                        "sender": sender,
                        "recipient": recipient if recipient else None
                    }
                    
                    with st.spinner("🤔 Assistant is analyzing your email..."):
                        response = process_email(email_data)
                    
                    if response:
                        st.session_state.email_history.append({
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "subject": subject,
                            "sender": sender,
                            "response": response
                        })
                        
                        st.success("✅ Email processed successfully!")
                        
                        with col2:
                            st.markdown("## 📨 AI Response")
                            
                            # Category and confidence
                            category = response.get('category', 'general_inquiry')
                            confidence = response.get('confidence_score', 0)
                            
                            badge_class = get_category_badge(category)
                            display_name = get_category_display(category)
                            
                            col_badge, col_conf = st.columns([1, 1])
                            with col_badge:
                                st.markdown(f'<span class="category-badge {badge_class}">{display_name}</span>', unsafe_allow_html=True)
                            with col_conf:
                                st.markdown(f'<span class="{get_confidence_class(confidence)}">Confidence: {confidence:.1%}</span>', unsafe_allow_html=True)
                            
                            # Retrieved documents
                            if response.get('retrieved_docs'):
                                with st.expander("📚 Retrieved Documents"):
                                    for doc in response['retrieved_docs']:
                                        st.markdown(f'<div class="retrieved-docs">📄 {doc.get("result", "")[:200]}...</div>', unsafe_allow_html=True)
                            
                            # Escalation warning
                            if response.get('requires_human_review'):
                                st.warning("🚨 This email requires human review")
                            
                            # Clarification question
                            if response.get('clarification_needed') and response.get('clarification_question'):
                                st.info(f"❓ {response['clarification_question']}")
                            
                            # Draft reply
                            draft_reply = response.get('draft_reply', '')
                            formatted_reply = format_email_text(draft_reply)
                            formatted_reply = formatted_reply.replace('\n', '<br>')
                            
                            st.markdown("**Draft Reply:**")
                            st.markdown(
                                f'<div class="email-preview">{formatted_reply}</div>',
                                unsafe_allow_html=True
                            )
        
        with col2:
            if not submitted:
                st.markdown("## 📨 AI Response")
                st.info("👈 Fill out the form and click 'Get Assistance' to see the AI-generated response here")
                
                # Quick tips box
                st.markdown("""
                <div class="info-box">
                    <h3 style="color: #0D47A1; font-weight: 700; margin-bottom: 0.75rem;">💡 Quick Tips</h3>
                    <div class="info-box-item">Ask about policies like leave, WFH, benefits</div>
                    <div class="info-box-item">Include specific details for better answers</div>
                    <div class="info-box-item">Sensitive matters are automatically escalated</div>
                    <div class="info-box-item">Check history for past conversations</div>
                </div>
                """, unsafe_allow_html=True)
    
    elif page == "📋 History":
        st.markdown("<h1 class='main-header'>Email History</h1>", unsafe_allow_html=True)
        
        if not st.session_state.email_history:
            st.info("No emails processed yet. Go to 'Compose Email' to get started!")
        else:
            for i, item in enumerate(reversed(st.session_state.email_history[-10:])):
                with st.expander(f"📧 {item['subject']} - {item['timestamp']}"):
                    st.markdown(f"**From:** {item['sender']}")
                    
                    response = item['response']
                    category = response.get('category', 'general_inquiry')
                    confidence = response.get('confidence_score', 0)
                    
                    badge_class = get_category_badge(category)
                    display_name = get_category_display(category)
                    
                    st.markdown(f'<span class="category-badge {badge_class}">{display_name}</span>', unsafe_allow_html=True)
                    
                    if response.get('requires_human_review'):
                        st.warning("⚠️ Required Human Review")
                    
                    draft_reply = response.get('draft_reply', '')
                    formatted_reply = format_email_text(draft_reply)
                    
                    st.markdown("**Draft Reply:**")
                    st.markdown(f'<div class="email-preview">{formatted_reply}</div>', unsafe_allow_html=True)
            
            if st.button("Clear History", use_container_width=True):
                st.session_state.email_history = []
                st.rerun()
    
    else:  # About page
        st.markdown("<h1 class='main-header'>About</h1>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🤖 AI Email Assistant")
            st.markdown("""
            This intelligent assistant helps automate email responses by:
            
            - **Understanding** email intent and category
            - **Searching** company policies using RAG
            - **Generating** professional, context-aware replies
            - **Escalating** sensitive matters to humans
            """)
        
        with col2:
            st.markdown("### ✨ Features")
            st.markdown("""
            - ✅ Real-time processing
            - ✅ Document retrieval
            - ✅ Confidence scoring
            - ✅ Email history
            - ✅ Category classification
            - ✅ Human escalation
            """)

if __name__ == "__main__":
    main()