import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import re
from datetime import datetime
import os
from config import BACKEND_DOCS_DIR

# Page configuration
st.set_page_config(
    page_title="AI Email Assistant",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Get API URL from environment variables (set in Streamlit Cloud secrets)
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Optional: Add a check to show which environment you're in
if "localhost" in API_BASE_URL or "ngrok" in API_BASE_URL:
    st.sidebar.info(f"🌐 Connected to LOCAL backend via tunnel")
else:
    st.sidebar.success(f"🌐 Connected to PRODUCTION backend")

# Custom CSS with better contrast and visibility
st.markdown("""
<style>
    /* Make placeholders more visible */
    input::placeholder, textarea::placeholder {
        color: #888888 !important;
        opacity: 1 !important;
        font-style: italic;
    }
    
    /* Style for the input fields themselves */
    .stTextInput input, .stTextArea textarea {
        color: #000000 !important;
        background-color: #ffffff !important;
    }
            
    /* Main header */
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    
    /* Success message box */
    .success-box {
        padding: 1rem;
        background-color: #D4EDDA;
        border: 1px solid #C3E6CB;
        border-radius: 5px;
        color: #155724;
        font-weight: 500;
    }
    
    /* Warning message box */
    .warning-box {
        padding: 1rem;
        background-color: #FFF3CD;
        border: 1px solid #FFEEBA;
        border-radius: 5px;
        color: #856404;
        font-weight: 500;
    }
    
    /* Email preview container */
    .email-preview {
        background-color: #F0F2F6;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #1E88E5;
        font-family: 'Courier New', monospace;
        white-space: pre-wrap;
        color: #000000;
        font-size: 0.95rem;
        line-height: 1.5;
        border: 1px solid #CCCCCC;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Style for bold text in preview */
    .email-preview strong {
        font-weight: bold;
        color: #000000;
        font-family: 'Courier New', monospace;
        background-color: #E8F0FE;
        padding: 0.1rem 0.2rem;
        border-radius: 3px;
    }
    
    /* Style for bullet points */
    .email-preview ul, .email-preview ol {
        margin: 0.5rem 0;
        padding-left: 1.5rem;
    }
    
    .email-preview li {
        color: #000000;
        margin: 0.25rem 0;
    }
    
    /* Quota exceeded specific styling */
    .quota-exceeded {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    .quota-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        animation: shake 0.5s ease-in-out;
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-10px); }
        75% { transform: translateX(10px); }
    }
    
    .quota-title {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .quota-message {
        font-size: 1.2rem;
        margin-bottom: 1.5rem;
        opacity: 0.95;
    }
    
    .quota-details {
        background-color: rgba(255,255,255,0.2);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-size: 1rem;
        backdrop-filter: blur(5px);
    }
    
    .quota-timer {
        font-size: 1.5rem;
        font-weight: bold;
        color: #ffd700;
        margin: 1rem 0;
    }
    
    .quota-footer {
        margin-top: 1.5rem;
        font-size: 0.9rem;
        opacity: 0.8;
    }
    
    .quota-button {
        background-color: white;
        color: #764ba2;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 25px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s;
        margin-top: 1rem;
    }
    
    .quota-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    
    /* Dark text for all email content */
    .email-preview p, .email-preview div, .email-preview span {
        color: #000000 !important;
    }
    
    /* Subject line styling */
    .email-subject {
        color: #1E88E5 !important;
        font-weight: bold;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    
    /* Button styling */
    .stButton button {
        background-color: #1E88E5;
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        transition: all 0.3s;
    }
    
    .stButton button:hover {
        background-color: #1565C0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    
    /* Sidebar header */
    .sidebar-header {
        font-size: 1.2rem;
        font-weight: bold;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        color: #1E88E5;
    }
    
    /* Category badges */
    .category-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 16px;
        font-weight: bold;
        font-size: 0.85rem;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    .badge-policy {
        background-color: #E3F2FD;
        color: #0D47A1;
        border: 1px solid #90CAF9;
    }
    
    .badge-sensitive {
        background-color: #FFEBEE;
        color: #B71C1C;
        border: 1px solid #EF9A9A;
    }
    
    .badge-general {
        background-color: #E8F5E8;
        color: #1B5E20;
        border: 1px solid #A5D6A7;
    }
    
    .badge-clarification {
        background-color: #FFF3E0;
        color: #BF360C;
        border: 1px solid #FFB74D;
    }
    
    /* Confidence meter */
    .confidence-high {
        color: #1B5E20;
        font-weight: bold;
    }
    
    .confidence-medium {
        color: #BF360C;
        font-weight: bold;
    }
    
    .confidence-low {
        color: #B71C1C;
        font-weight: bold;
    }
    
    /* Retrieved docs section */
    .retrieved-docs {
        background-color: #F5F5F5;
        padding: 1rem;
        border-radius: 5px;
        border-left: 3px solid #FFA000;
        margin: 0.5rem 0;
        color: #333333;
    }
    
    /* Form input styling */
    .stTextInput input, .stTextArea textarea {
        background-color: white;
        color: #333333;
        border: 1px solid #CCCCCC;
    }
    
    /* Success message */
    .success-message {
        background-color: #D4EDDA;
        color: #155724;
        padding: 0.75rem;
        border-radius: 4px;
        border-left: 4px solid #28A745;
    }
    
    /* Warning message */
    .warning-message {
        background-color: #FFF3CD;
        color: #856404;
        padding: 0.75rem;
        border-radius: 4px;
        border-left: 4px solid #FFC107;
    }
    
    /* Error message */
    .error-message {
        background-color: #F8D7DA;
        color: #721C24;
        padding: 0.75rem;
        border-radius: 4px;
        border-left: 4px solid #DC3545;
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
    
    # Handle bullet points (convert * at start of line to •)
    text = re.sub(r'^\* ', '• ', text, flags=re.MULTILINE)
    
    # Handle bold with ** (most common)
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    
    # Handle bold with single * (less common)
    text = re.sub(r'(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)', r'<strong>\1</strong>', text)
    
    # Handle numbered lists
    lines = text.split('\n')
    formatted_lines = []
    in_list = False
    
    for line in lines:
        # Check for numbered list items (1., 2., etc.)
        numbered_match = re.match(r'^(\d+\.)\s+(.*)', line)
        if numbered_match:
            if not in_list:
                formatted_lines.append('<ol>')
                in_list = True
            formatted_lines.append(f'<li>{numbered_match.group(2)}</li>')
        else:
            if in_list:
                formatted_lines.append('</ol>')
                in_list = False
            formatted_lines.append(line)
    
    if in_list:
        formatted_lines.append('</ol>')
    
    text = '\n'.join(formatted_lines)
    
    return text

def process_email(email_data):
    """Send email to API for processing with quota error handling"""
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
            # Quota exceeded error from backend
            error_data = response.json().get('detail', {})
            if isinstance(error_data, dict):
                show_quota_message(error_data)
            else:
                show_quota_message({"message": str(error_data)})
            return None
        else:
            st.error(f"Error: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        # Check if it might be a quota issue causing timeout
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
    """Display a beautiful quota exceeded message"""
    message = error_data.get('message', 'Daily API limit reached')
    limit = error_data.get('limit', 20)
    model = error_data.get('model', 'gemini-2.5-flash')
    
    # Calculate time until reset (midnight PST)
    from datetime import datetime, timedelta
    import pytz
    
    # Get current time in PST
    pst = pytz.timezone('US/Pacific')
    now_pst = datetime.now(pst)
    
    # Calculate next midnight PST
    midnight_pst = now_pst.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    time_until_reset = midnight_pst - now_pst
    hours = int(time_until_reset.total_seconds() // 3600)
    minutes = int((time_until_reset.total_seconds() % 3600) // 60)
    
    st.markdown(f"""
    <div class="quota-exceeded">
        <div class="quota-icon">⚠️</div>
        <div class="quota-title">API Quota Exceeded</div>
        <div class="quota-message">{message}</div>
        <div class="quota-details">
            <strong>Daily Limit:</strong> {limit} requests<br>
            <strong>Model:</strong> {model}<br>
            <strong>Status:</strong> You've used all {limit} requests for today
        </div>
        <div class="quota-timer">
            ⏰ Resets in {hours}h {minutes}m
        </div>
        <div class="quota-footer">
            Free tier limits reset at midnight Pacific Time<br>
            <a href="https://console.cloud.google.com" target="_blank" style="color: white; text-decoration: underline;">Upgrade to paid tier</a> for higher limits
        </div>
        <button class="quota-button" onclick="window.location.reload()">
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
        st.image("https://img.icons8.com/color/96/000000/email.png", width=80)
        st.title("AI Email Assistant")
        st.markdown("---")
        
        # API Status
        st.markdown('<p class="sidebar-header">🔌 API Status</p>', unsafe_allow_html=True)
        api_healthy = check_api_health()
        if api_healthy:
            st.success("✅ Connected")
        else:
            st.error("❌ Disconnected")
            st.warning("Make sure FastAPI server is running")
            if st.button("🔄 Retry Connection"):
                st.rerun()
        
        st.markdown("---")
        
        # Navigation
        st.markdown('<p class="sidebar-header">🧭 Navigation</p>', unsafe_allow_html=True)
        page = st.radio(
            "Go to",
            ["📧 Process Email", "📋 History", "ℹ️ About"],
            label_visibility="collapsed"
        )
    
    # Main content area
    if page == "📧 Process Email":
        st.markdown("<h1 class='main-header'>📧 AI Email Assistant</h1>", unsafe_allow_html=True)
        
        # Create two columns
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 📝 Compose Email")
            
            # Email input form
            with st.form("email_form"):
                subject = st.text_input(
                    "Subject*",
                    placeholder="e.g., Question about sick leave",
                    help="Required field"
                )
                
                sender = st.text_input(
                    "From (Sender)*",
                    placeholder="e.g., employee@company.com",
                    help="Required field"
                )
                
                recipient = st.text_input(
                    "To (Recipient)",
                    placeholder="e.g., hr@company.com",
                    help="Optional field"
                )
                
                body = st.text_area(
                    "Email Body*",
                    placeholder="e.g., How many sick days do I get per year? Do I need a doctor's note?",
                    height=200,
                    help="Required field"
                )
                
                submitted = st.form_submit_button(
                    "🚀 Process Email",
                    type="primary",
                    use_container_width=True
                )
            
            if submitted:
                if not subject or not body or not sender:
                    st.error("Please fill in all required fields (*)")
                elif not api_healthy:
                    st.error("API is not connected. Please start the FastAPI server.")
                else:
                    # Prepare email data
                    email_data = {
                        "subject": subject,
                        "body": body,
                        "sender": sender,
                        "recipient": recipient if recipient else None
                    }
                    
                    # Show processing
                    with st.spinner("🤔 Agent is thinking..."):
                        response = process_email(email_data)
                    
                    if response:
                        # Check if response contains fallback message
                        if "Agent stopped" in response.get('draft_reply', ''):
                            st.warning("⚠️ The agent stopped before completing. This sometimes happens with complex queries. Please try again with a more specific question.")
                        
                        # Store in history
                        st.session_state.email_history.append({
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "subject": subject,
                            "sender": sender,
                            "response": response
                        })
                        
                        # Show success
                        st.markdown('<div class="success-message">✅ Email processed successfully!</div>', unsafe_allow_html=True)
                        
                        # Display in col2
                        with col2:
                            st.markdown("### 📨 Generated Reply")
                            
                            # Category badge
                            category = response.get('category', 'general_inquiry')
                            confidence = response.get('confidence_score', 0)
                            
                            badge_class = get_category_badge(category)
                            display_name = get_category_display(category)
                            
                            st.markdown(
                                f'<span class="category-badge {badge_class}">{display_name}</span> '
                                f'<span class="{get_confidence_class(confidence)}">(Confidence: {confidence:.2%})</span>',
                                unsafe_allow_html=True
                            )
                            
                            # Show retrieved documents
                            if response.get('retrieved_docs'):
                                with st.expander("📚 Retrieved Documents"):
                                    for doc in response['retrieved_docs']:
                                        st.markdown(f'<div class="retrieved-docs">📄 {doc.get("result", "")[:200]}...</div>', unsafe_allow_html=True)
                            
                            # Show escalation warning
                            if response.get('requires_human_review'):
                                st.markdown('<div class="warning-message">🚨 This email requires human review!</div>', unsafe_allow_html=True)
                            
                            # Show clarification question
                            if response.get('clarification_needed') and response.get('clarification_question'):
                                st.markdown(f'<div class="warning-message">❓ {response["clarification_question"]}</div>', unsafe_allow_html=True)
                            
                            # Show draft reply with better visibility and formatting
                            st.markdown("#### Draft Reply:")
                            draft_reply = response.get('draft_reply', '')
                            
                            # Format the draft reply with markdown to HTML conversion
                            formatted_reply = format_email_text(draft_reply)
                            formatted_reply = formatted_reply.replace('\n', '<br>')
                            
                            st.markdown(
                                f'<div class="email-preview">{formatted_reply}</div>',
                                unsafe_allow_html=True
                            )
                            
                            # Copy button (simulated)
                            st.button(
                                "📋 Copy to Clipboard",
                                on_click=lambda: st.write("Select text and press Ctrl+C to copy"),
                                help="Select the text above and press Ctrl+C"
                            )
        
        with col2:
            if not submitted:
                st.markdown("### 📨 Generated Reply")
                st.info("👈 Fill out the form and click 'Process Email' to see the generated reply here")
    
    elif page == "📋 History":
        st.markdown("<h1 class='main-header'>📋 Email History</h1>", unsafe_allow_html=True)
        
        if not st.session_state.email_history:
            st.info("No emails processed yet. Go to 'Process Email' to get started!")
        else:
            for i, item in enumerate(reversed(st.session_state.email_history[-10:])):
                with st.expander(f"📧 {item['subject']} - {item['timestamp']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Original Email:**")
                        st.text(f"From: {item['sender']}")
                        st.text(f"Subject: {item['subject']}")
                        st.text(f"Time: {item['timestamp']}")
                    
                    with col2:
                        st.markdown("**Generated Response:**")
                        response = item['response']
                        category = response.get('category', 'general_inquiry')
                        confidence = response.get('confidence_score', 0)
                        
                        badge_class = get_category_badge(category)
                        display_name = get_category_display(category)
                        
                        st.markdown(
                            f'<span class="category-badge {badge_class}">{display_name}</span> '
                            f'<span class="{get_confidence_class(confidence)}">({confidence:.2%})</span>',
                            unsafe_allow_html=True
                        )
                        
                        if response.get('requires_human_review'):
                            st.markdown('<div class="warning-message">⚠️ Required Human Review</div>', unsafe_allow_html=True)
                    
                    st.markdown("**Draft Reply:**")
                    draft_reply = response.get('draft_reply', '')
                    
                    # Format the draft reply with markdown to HTML conversion
                    formatted_reply = format_email_text(draft_reply)
                    formatted_reply = formatted_reply.replace('\n', '<br>')
                    
                    st.markdown(
                        f'<div class="email-preview">{formatted_reply}</div>',
                        unsafe_allow_html=True
                    )
                    
                    if response.get('retrieved_docs'):
                        with st.expander("📚 Retrieved Documents"):
                            for doc in response['retrieved_docs']:
                                st.markdown(f'<div class="retrieved-docs">📄 {doc.get("result", "")[:200]}...</div>', unsafe_allow_html=True)
            
            if st.button("Clear History"):
                st.session_state.email_history = []
                st.rerun()
    
    else:  # About page
        st.markdown("<h1 class='main-header'>ℹ️ About</h1>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 🤖 AI Email Assistant
            
            This intelligent assistant helps automate email responses by:
            
            - **Understanding** email intent and category
            - **Searching** company policies using RAG
            - **Generating** professional, context-aware replies
            - **Escalating** sensitive matters to humans
            
            ### 🛠️ Technology Stack
            
            - **Frontend**: Streamlit
            - **Backend**: FastAPI
            - **LLM**: Google Gemini 2.5
            - **Vector DB**: FAISS
            - **Agent Framework**: LangChain
            """)
        
        with col2:
            st.markdown("""
            ### 📚 Features
            
            - ✅ Real-time processing
            - ✅ Document retrieval
            - ✅ Confidence scoring
            - ✅ Email history
            - ✅ Category classification
            - ✅ Human escalation
            - ✅ Quota exceeded notifications with countdown timer
            """)

if __name__ == "__main__":
    main()