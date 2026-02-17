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

# Custom CSS for better UX
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main header styling */
    .main-header {
        font-size: 2.2rem;
        color: #1A1F36;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 600;
        letter-spacing: -0.02em;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #1A1F36;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #f0f0f0;
    }
    
    /* Form container styling */
    .form-container {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02);
        border: 1px solid #f0f0f0;
    }
    
    /* Input field styling */
    .stTextInput input, .stTextArea textarea {
        border-radius: 12px !important;
        border: 1.5px solid #e0e0e0 !important;
        padding: 0.75rem 1rem !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease !important;
        background-color: #fafafa !important;
        color: #1A1F36 !important;
        caret-color: #1E88E5 !important;  /* Makes cursor blue and visible */
    }
    
    /* Input focus state */
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #1E88E5 !important;
        box-shadow: 0 0 0 3px rgba(30, 136, 229, 0.1) !important;
        background-color: #ffffff !important;
        outline: none !important;
    }
    
    /* Input hover state */
    .stTextInput input:hover, .stTextArea textarea:hover {
        border-color: #b0b0b0 !important;
        background-color: #ffffff !important;
    }
    
    /* Placeholder styling */
    input::placeholder, textarea::placeholder {
        color: #9e9e9e !important;
        font-size: 0.9rem !important;
        font-style: normal !important;
        opacity: 0.8 !important;
    }
    
    /* Label styling */
    .stTextInput label, .stTextArea label {
        font-weight: 500 !important;
        color: #4a4a4a !important;
        font-size: 0.9rem !important;
        margin-bottom: 0.25rem !important;
    }
    
    /* Required field indicator */
    .stTextInput label:after, .stTextArea label:after {
        content: " *";
        color: #e53e3e;
        font-weight: 600;
    }
    
    /* Optional field indicator */
    .stTextInput:has(input[placeholder*="Optional"]) label:after,
    .stTextArea:has(textarea[placeholder*="Optional"]) label:after {
        content: " (optional)";
        color: #9e9e9e;
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
        box-shadow: 0 4px 12px rgba(30, 136, 229, 0.2) !important;
        width: 100%;
    }
    
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(30, 136, 229, 0.3) !important;
    }
    
    .stButton button:active {
        transform: translateY(0) !important;
    }
    
    /* Email preview card */
    .email-preview {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 16px;
        border-left: 4px solid #1E88E5;
        font-family: 'Inter', sans-serif;
        white-space: pre-wrap;
        color: #1A1F36;
        font-size: 0.95rem;
        line-height: 1.6;
        border: 1px solid #f0f0f0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.02);
        margin-top: 1rem;
    }
    
    /* Category badges */
    .category-badge {
        display: inline-block;
        padding: 0.35rem 1rem;
        border-radius: 30px;
        font-weight: 500;
        font-size: 0.85rem;
        margin-right: 0.75rem;
        margin-bottom: 0.75rem;
        letter-spacing: 0.02em;
    }
    
    .badge-policy {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
        color: #0D47A1;
        border: none;
    }
    
    .badge-sensitive {
        background: linear-gradient(135deg, #FFEBEE 0%, #FFCDD2 100%);
        color: #B71C1C;
        border: none;
    }
    
    .badge-general {
        background: linear-gradient(135deg, #E8F5E8 0%, #C8E6C9 100%);
        color: #1B5E20;
        border: none;
    }
    
    .badge-clarification {
        background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%);
        color: #BF360C;
        border: none;
    }
    
    /* Confidence meter */
    .confidence-high {
        color: #1B5E20;
        font-weight: 600;
        background: #E8F5E8;
        padding: 0.35rem 1rem;
        border-radius: 30px;
        display: inline-block;
    }
    
    .confidence-medium {
        color: #BF360C;
        font-weight: 600;
        background: #FFF3E0;
        padding: 0.35rem 1rem;
        border-radius: 30px;
        display: inline-block;
    }
    
    .confidence-low {
        color: #B71C1C;
        font-weight: 600;
        background: #FFEBEE;
        padding: 0.35rem 1rem;
        border-radius: 30px;
        display: inline-block;
    }
    
    /* Retrieved docs section */
    .retrieved-docs {
        background-color: #F8F9FA;
        padding: 1rem;
        border-radius: 12px;
        border-left: 3px solid #FFA000;
        margin: 0.75rem 0;
        color: #1A1F36;
        font-size: 0.9rem;
        border: 1px solid #f0f0f0;
    }
    
    /* Success message */
    .success-message {
        background: linear-gradient(135deg, #D4EDDA 0%, #C3E6CB 100%);
        color: #155724;
        padding: 1rem;
        border-radius: 12px;
        font-weight: 500;
        margin: 1rem 0;
        border: none;
    }
    
    /* Warning message */
    .warning-message {
        background: linear-gradient(135deg, #FFF3CD 0%, #FFE69C 100%);
        color: #856404;
        padding: 1rem;
        border-radius: 12px;
        font-weight: 500;
        margin: 1rem 0;
        border: none;
    }
    
    /* Error message */
    .error-message {
        background: linear-gradient(135deg, #F8D7DA 0%, #F5C6CB 100%);
        color: #721C24;
        padding: 1rem;
        border-radius: 12px;
        font-weight: 500;
        margin: 1rem 0;
        border: none;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #F8F9FA;
    }
    
    .sidebar-header {
        font-size: 1rem;
        font-weight: 600;
        color: #1A1F36;
        margin: 1.5rem 0 0.75rem 0;
        letter-spacing: 0.02em;
        text-transform: uppercase;
    }
    
    /* Quota exceeded message */
    .quota-exceeded {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        margin: 1rem 0;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    /* Copy button */
    .copy-button {
        background-color: #f0f0f0 !important;
        color: #1A1F36 !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-size: 0.9rem !important;
        margin-top: 1rem !important;
    }
    
    .copy-button:hover {
        background-color: #e0e0e0 !important;
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
    text = re.sub(r'(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)', r'<strong>\1</strong>', text)
    
    # Handle numbered lists
    lines = text.split('\n')
    formatted_lines = []
    in_list = False
    
    for line in lines:
        numbered_match = re.match(r'^(\d+\.)\s+(.*)', line)
        if numbered_match:
            if not in_list:
                formatted_lines.append('<ol style="margin-top: 0.5rem; margin-bottom: 0.5rem;">')
                in_list = True
            formatted_lines.append(f'<li style="margin-bottom: 0.25rem;">{numbered_match.group(2)}</li>')
        else:
            if in_list:
                formatted_lines.append('</ol>')
                in_list = False
            formatted_lines.append(line)
    
    if in_list:
        formatted_lines.append('</ol>')
    
    return '\n'.join(formatted_lines)

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
            error_data = response.json().get('detail', {})
            show_quota_message(error_data)
            return None
        else:
            st.error(f"Error: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        show_quota_message({
            "error": "quota_exceeded",
            "message": "Request timed out - likely due to API quota limits",
            "limit": 20,
            "model": "gemini-2.5-flash"
        })
        return None
    except Exception as e:
        error_str = str(e).lower()
        if "429" in error_str or "quota" in error_str or "limit" in error_str:
            show_quota_message({
                "error": "quota_exceeded",
                "message": "API quota exceeded",
                "limit": 20,
                "model": "gemini-2.5-flash"
            })
        else:
            st.error(f"Connection error: {str(e)}")
        return None

def show_quota_message(error_data):
    """Display quota exceeded message"""
    message = error_data.get('message', 'Daily API limit reached')
    limit = error_data.get('limit', 20)
    model = error_data.get('model', 'gemini-2.5-flash')
    
    from datetime import datetime, timedelta
    import pytz
    
    pst = pytz.timezone('US/Pacific')
    now_pst = datetime.now(pst)
    midnight_pst = now_pst.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    time_until_reset = midnight_pst - now_pst
    hours = int(time_until_reset.total_seconds() // 3600)
    minutes = int((time_until_reset.total_seconds() % 3600) // 60)
    
    st.markdown(f"""
    <div class="quota-exceeded">
        <div style="font-size: 3rem; margin-bottom: 1rem;">⚠️</div>
        <h3 style="margin-bottom: 1rem;">API Quota Exceeded</h3>
        <p style="margin-bottom: 1.5rem;">{message}</p>
        <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 12px; margin-bottom: 1rem;">
            <strong>Daily Limit:</strong> {limit} requests<br>
            <strong>Model:</strong> {model}
        </div>
        <div style="font-size: 1.5rem; font-weight: bold; margin: 1rem 0;">
            ⏰ Resets in {hours}h {minutes}m
        </div>
        <button onclick="window.location.reload()" style="background: white; color: #764ba2; border: none; padding: 0.75rem 2rem; border-radius: 30px; font-weight: bold; cursor: pointer; margin-top: 1rem;">
            🔄 Check Again
        </button>
    </div>
    """, unsafe_allow_html=True)

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
        st.markdown('<p class="sidebar-header">🔌 Connection</p>', unsafe_allow_html=True)
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
        st.markdown('<p class="sidebar-header">🧭 Navigation</p>', unsafe_allow_html=True)
        page = st.radio(
            "Go to",
            ["📧 Compose Email", "📋 History", "ℹ️ About"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.caption(f"Connected to: {API_BASE_URL.split('//')[1].split('.')[0] if '//' in API_BASE_URL else 'local'}")

    # Main content area
    if page == "📧 Compose Email":
        st.markdown("<h1 class='main-header'>AI Email Assistant</h1>", unsafe_allow_html=True)
        
        # Create two columns
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            st.markdown('<p class="section-header">📝 Compose Email</p>', unsafe_allow_html=True)
            
            with st.form("email_form"):
                subject = st.text_input(
                    "Subject",
                    placeholder="Question about sick leave policy",
                    help="Enter the email subject line"
                )
                
                sender = st.text_input(
                    "From",
                    placeholder="john.doe@company.com",
                    help="Your email address"
                )
                
                recipient = st.text_input(
                    "To",
                    placeholder="hr@company.com",
                    help="Recipient email address (optional)"
                )
                
                body = st.text_area(
                    "Message",
                    placeholder="How many sick days do I get per year? Do I need a doctor's note for a single day?",
                    height=250,
                    help="Type your email content here"
                )
                
                submitted = st.form_submit_button(
                    "🚀 Generate Reply",
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
                    
                    with st.spinner("🤔 Agent is analyzing your email..."):
                        response = process_email(email_data)
                    
                    if response:
                        st.session_state.email_history.append({
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "subject": subject,
                            "sender": sender,
                            "response": response
                        })
                        
                        st.markdown('<div class="success-message">✅ Email processed successfully!</div>', unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown('<p class="section-header">📨 Generated Reply</p>', unsafe_allow_html=True)
                            
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
                                st.markdown('<div class="warning-message">🚨 This email requires human review</div>', unsafe_allow_html=True)
                            
                            # Clarification question
                            if response.get('clarification_needed') and response.get('clarification_question'):
                                st.markdown(f'<div class="warning-message">❓ {response["clarification_question"]}</div>', unsafe_allow_html=True)
                            
                            # Draft reply
                            draft_reply = response.get('draft_reply', '')
                            formatted_reply = format_email_text(draft_reply)
                            formatted_reply = formatted_reply.replace('\n', '<br>')
                            
                            st.markdown(
                                f'<div class="email-preview">{formatted_reply}</div>',
                                unsafe_allow_html=True
                            )
                            
                            st.button(
                                "📋 Copy to Clipboard",
                                key="copy_button",
                                help="Select the text above and press Ctrl+C to copy"
                            )
        
        with col2:
            if not submitted:
                st.markdown('<p class="section-header">📨 Generated Reply</p>', unsafe_allow_html=True)
                st.info("👈 Fill out the form and click 'Generate Reply' to see the response here")
                
                # Quick tips
                st.markdown("""
                <div style="background-color: #F8F9FA; padding: 1.5rem; border-radius: 12px; margin-top: 1rem;">
                    <p style="font-weight: 600; margin-bottom: 0.5rem;">💡 Quick Tips</p>
                    <ul style="color: #4a4a4a; font-size: 0.9rem;">
                        <li>Ask about policies like leave, WFH, benefits</li>
                        <li>Include specific details for better answers</li>
                        <li>Sensitive matters are automatically escalated</li>
                        <li>Check history for past conversations</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
    
    elif page == "📋 History":
        st.markdown("<h1 class='main-header'>Email History</h1>", unsafe_allow_html=True)
        
        if not st.session_state.email_history:
            st.info("No emails processed yet. Go to 'Compose Email' to get started!")
        else:
            for i, item in enumerate(reversed(st.session_state.email_history[-10:])):
                with st.expander(f"📧 {item['subject']} - {item['timestamp']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Original Email:**")
                        st.caption(f"From: {item['sender']}")
                        st.caption(f"Subject: {item['subject']}")
                        st.caption(f"Time: {item['timestamp']}")
                    
                    with col2:
                        response = item['response']
                        category = response.get('category', 'general_inquiry')
                        confidence = response.get('confidence_score', 0)
                        
                        badge_class = get_category_badge(category)
                        display_name = get_category_display(category)
                        
                        st.markdown(
                            f'<span class="category-badge {badge_class}">{display_name}</span>',
                            unsafe_allow_html=True
                        )
                        
                        if response.get('requires_human_review'):
                            st.markdown('<div class="warning-message">⚠️ Required Human Review</div>', unsafe_allow_html=True)
                    
                    draft_reply = response.get('draft_reply', '')
                    formatted_reply = format_email_text(draft_reply)
                    formatted_reply = formatted_reply.replace('\n', '<br>')
                    
                    st.markdown("**Draft Reply:**")
                    st.markdown(
                        f'<div class="email-preview">{formatted_reply}</div>',
                        unsafe_allow_html=True
                    )
            
            if st.button("Clear History", use_container_width=True):
                st.session_state.email_history = []
                st.rerun()
    
    else:  # About page
        st.markdown("<h1 class='main-header'>About</h1>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 🤖 AI Email Assistant
            
            This intelligent assistant helps automate email responses by:
            
            - **Understanding** email intent and category
            - **Searching** company policies using RAG
            - **Generating** professional, context-aware replies
            - **Escalating** sensitive matters to humans
            """)
            
            st.markdown("### 🛠️ Technology Stack")
            st.markdown("""
            - **Frontend**: Streamlit
            - **Backend**: FastAPI
            - **LLM**: Google Gemini 2.5
            - **Vector DB**: FAISS
            - **Agent Framework**: LangChain
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
            - ✅ Quota exceeded notifications
            """)
            
            st.markdown("### 🚀 Getting Started")
            st.markdown("""
            1. Go to **Compose Email**
            2. Fill in the email details
            3. Click **Generate Reply**
            4. View the AI-generated response
            """)

if __name__ == "__main__":
    main()