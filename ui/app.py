"""
Streamlit UI for SupportPilot AI
"""
import streamlit as st
import requests
import json
from typing import Optional
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="SupportPilot AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Dark theme with white text
st.markdown("""
    <style>
    /* Main theme - Dark background */
    [data-testid="stAppViewContainer"] {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    
    [data-testid="stSidebar"] {
        background-color: #2d2d2d;
        color: #ffffff;
    }
    
    /* Text visibility */
    html, body {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    
    .main {
        background-color: #1e1e1e;
        color: #ffffff;
        padding: 2rem;
    }
    
    /* All text elements - white */
    div, p, span, h1, h2, h3, h4, h5, h6, label, button {
        color: #ffffff !important;
    }
    
    /* Chat messages */
    .stChatMessage {
        background-color: #2d2d2d;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        color: #ffffff;
    }
    
    .stChatMessage p {
        color: #ffffff !important;
    }
    
    /* User message container - Right alignment */
    .stChatMessage:has([data-testid="chatAvatarIcon-user"]) {
        margin-left: auto !important;
        margin-right: 0 !important;
        max-width: 75%;
        background-color: #123a5c !important;
    }
    
    .stChatMessage:has([data-testid="chatAvatarIcon-user"]) > div {
        flex-direction: row-reverse !important;
    }
    
    /* Assistant message container - Left alignment */
    .stChatMessage:has([data-testid="chatAvatarIcon-assistant"]) {
        margin-left: 0 !important;
        margin-right: auto !important;
        max-width: 75%;
        background-color: #14331f !important;
    }
    
    .stChatMessage:has([data-testid="chatAvatarIcon-assistant"]) > div {
        flex-direction: row !important;
    }
    
    /* Ticket information box */
    .ticket-info {
        background-color: #3d3d1f;
        border-left: 4px solid #f59e0b;
        padding: 1rem;
        border-radius: 0.25rem;
        margin: 1rem 0;
        color: #ffffff;
    }
    
    .ticket-info strong {
        color: #fbbf24;
    }
    
    /* Knowledge base sources */
    .kb-sources {
        background-color: #1a1a3e;
        border-left: 4px solid #818cf8;
        padding: 1rem;
        border-radius: 0.25rem;
        margin-top: 1rem;
        color: #ffffff;
    }
    
    .kb-sources strong {
        color: #a5b4fc;
    }
    
    /* Input box styling */
    .stChatInput {
        background-color: #2d2d2d !important;
        padding: 0.5rem !important;
        border-radius: 0.5rem !important;
    }
    
    .stChatInput textarea {
        background-color: #3d3d3d !important;
        color: #ffffff !important;
        border: 1px solid #4d4d4d !important;
        border-radius: 0.25rem !important;
    }
    
    .stChatInput textarea:focus {
        background-color: #3d3d3d !important;
        color: #ffffff !important;
        border: 1px solid #6366f1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
        outline: none !important;
    }
    
    .stChatInput textarea::placeholder {
        color: #888888 !important;
    }
    
    .stChatInput button {
        background-color: #4d4d4d !important;
        color: #ffffff !important;
        border: 1px solid #5d5d5d !important;
    }
    
    .stChatInput button:hover {
        background-color: #5d5d5d !important;
    }
    
    /* Sidebar text */
    [data-testid="stSidebar"] div, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background-color: #2d2d2d !important;
        color: #ffffff !important;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: #3d3d3d !important;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #4d4d4d;
        color: #ffffff;
        border-color: #5d5d5d;
    }
    
    .stButton > button:hover {
        background-color: #5d5d5d;
        color: #ffffff;
    }
    
    /* Metric boxes */
    .stMetric {
        background-color: #2d2d2d;
        color: #ffffff;
    }
    
    .stMetric > div {
        color: #ffffff !important;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ffffff !important;
    }
    
    /* Links */
    a {
        color: #818cf8 !important;
    }
    
    a:hover {
        color: #a5b4fc !important;
    }
    
    /* Divider */
    hr {
        border-color: #4d4d4d;
    }
    </style>
""", unsafe_allow_html=True)

# ==================== Configuration ====================

API_BASE_URL = "http://127.0.0.1:8000"

# Check if backend is running
def check_backend_health():
    """Check if backend API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False


# ==================== Main Page ====================

st.title("🤖 SupportPilot AI")
st.markdown("*Personal AI help-desk assistant (RAG + ticket lookup) with knowledge base and ticket integration*")

# Check backend status
if not check_backend_health():
    st.error(
        "⚠️ Backend API is not running. Please start the FastAPI server:\n"
        "`python -m uvicorn main:app --reload` from the backend directory"
    )
    st.stop()

# ==================== Sidebar ====================

with st.sidebar:
    st.header("ℹ️ About SupportPilot")
    st.caption("Personal Edition — owned by Aryan")
    
    st.markdown("""
    This AI agent can:
    - Answer questions from the knowledge base
    - Access ticket information (use ticket ID like HELP-001)
    - Combine context to provide better support
    
    **Example queries:**
    - "How do I reset my password?"
    - "I'm having issues with HELP-001"
    - "Tell me about billing"
    """)
    
    st.divider()
    
    # Debug info
    with st.expander("🔧 Debug Info"):
        try:
            info = requests.get(f"{API_BASE_URL}/info").json()
            st.json(info)
        except:
            st.error("Could not fetch system info")
    
    # Clear chat
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()


# ==================== Session State ====================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_count" not in st.session_state:
    st.session_state.chat_count = 0


# ==================== Chat Interface ====================

# Display chat history
for i, message in enumerate(st.session_state.messages):
    if message["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            st.write(message["content"])
    else:
        with st.chat_message("assistant", avatar="🤖"):
            st.write(message["response"])
            
            # Display ticket info if available
            if message.get("ticket_id"):
                st.markdown(f"""
                <div class="ticket-info">
                <strong>🎫 Ticket Found:</strong> {message['ticket_id']}
                </div>
                """, unsafe_allow_html=True)
            
            # Display knowledge base sources
            if message.get("kb_docs_used", 0) > 0:
                with st.expander(f"📚 Knowledge Base Sources ({message['kb_docs_used']})"):
                    if message.get("sources"):
                        for source in message["sources"]:
                            st.write(f"**{source['title']}** ({source['category']})")
                    else:
                        st.write("Sources used in response")


# ==================== Input Handler ====================

user_input = st.chat_input(
    "Type your question or describe your issue...",
    key="user_input"
)

if user_input:
    # Add user message to chat history
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    
    # Display user message
    with st.chat_message("user", avatar="👤"):
        st.write(user_input)
    
    # Get AI response
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🤔 Thinking..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/api/chat",
                    json={"message": user_input},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Display response
                    st.write(data["response"])
                    
                    # Display ticket info if found
                    if data.get("ticket_id"):
                        st.markdown(f"""
                        <div class="ticket-info">
                        <strong>🎫 Ticket Found:</strong> {data['ticket_id']}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Display knowledge base sources
                    if data.get("kb_docs_used", 0) > 0:
                        with st.expander(f"📚 Knowledge Base Sources ({data['kb_docs_used']})"):
                            if data.get("sources"):
                                for source in data["sources"]:
                                    st.write(f"**{source['title']}** ({source['category']})")
                    
                    # Add to chat history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "response": data["response"],
                        "ticket_id": data.get("ticket_id"),
                        "kb_docs_used": data.get("kb_docs_used", 0),
                        "sources": data.get("sources")
                    })
                    
                    st.session_state.chat_count += 1
                
                else:
                    error_msg = f"Error: {response.status_code} - {response.text}"
                    st.error(error_msg)
            
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out. Backend server may be slow or unresponsive.")
            except requests.exceptions.ConnectionError:
                st.error("🔌 Cannot connect to backend. Is the API running?")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")


# ==================== Feedback (SupportPilot addition) ====================

if st.session_state.messages:
    last = st.session_state.messages[-1]
    if last.get("role") == "assistant":
        fb_col1, fb_col2, fb_col3 = st.columns([1, 1, 6])
        with fb_col1:
            if st.button("👍 Helpful", key=f"up_{len(st.session_state.messages)}"):
                st.toast("Thanks for the feedback!")
        with fb_col2:
            if st.button("👎 Not helpful", key=f"down_{len(st.session_state.messages)}"):
                st.toast("Noted — will improve sources.")

# ==================== Footer ====================

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Messages", st.session_state.chat_count)

with col2:
    st.metric("Chat Sessions", len(st.session_state.messages) // 2 if st.session_state.messages else 0)

with col3:
    st.write(f"*SupportPilot Personal Edition | Updated: {datetime.now().strftime('%H:%M:%S')}*")
