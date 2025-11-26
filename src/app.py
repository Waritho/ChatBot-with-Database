import streamlit as st
import uuid
from langchain_core.messages import HumanMessage
import sys
import os

# Add the current directory to sys.path to ensure imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.chatbot import chatbot
from utils.database import (
    init_db, create_user, verify_user, link_thread_to_user, 
    get_user_threads, delete_thread, create_session, 
    get_user_from_session, delete_session, get_username
)

# Initialize Database
init_db()

# Page Config
st.set_page_config(
    page_title="NEXUS AI",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Custom CSS
def load_css():
    with open(os.path.join(os.path.dirname(__file__), 'styles', 'main.css'), 'r') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()

# Session State Initialization
if 'user' not in st.session_state:
    st.session_state['user'] = None

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = None

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

# Session Persistence Check
if st.session_state['user'] is None:
    # Check for session token in query params
    # st.query_params is a dict-like object in newer streamlit
    query_params = st.query_params
    session_token = query_params.get("session")
    
    if session_token:
        user_id = get_user_from_session(session_token)
        if user_id:
            username = get_username(user_id)
            st.session_state['user'] = {'id': user_id, 'username': username}
        else:
            # Invalid token, clear it
            if "session" in st.query_params:
                del st.query_params["session"]

# Authentication Functions
def login():
    st.markdown("### LOGIN TO NEXUS AI")
    username = st.text_input("USENAME", key="login_user")
    password = st.text_input("ACCESS CODE", type="password", key="login_pass")
    if st.button("LOGIN"):
        # Handle None values from Streamlit (shouldn't happen, but be safe)
        if username is None:
            username = ""
        if password is None:
            password = ""
            
        # Validate inputs
        if not username or not username.strip():
            st.error("PLEASE ENTER A USERNAME.")
            return
        if not password or not password.strip():
            st.error("PLEASE ENTER A PASSWORD.")
            return
        
        # Trim inputs before verification
        username = username.strip()
        password = password.strip()
        
        # Verify user with trimmed credentials
        user_id = verify_user(username, password)
        if user_id:
            # Get the actual username from database (trimmed version)
            actual_username = username
            st.session_state['user'] = {'id': user_id, 'username': actual_username}
            # Create persistent session
            token = create_session(user_id)
            st.query_params["session"] = token
            st.success(f"ACCESS GRANTED. WELCOME, {actual_username}.")
            st.rerun()
        else:
            # Additional debugging - check if user exists at all
            from utils.database import get_user_by_username
            user_info = get_user_by_username(username)
            if user_info:
                st.error("ACCESS DENIED. INVALID PASSWORD.")
            else:
                st.error("ACCESS DENIED. USER NOT FOUND.")

def signup():
    st.markdown("### NEW OPERATOR REGISTRATION")
    username = st.text_input("CHOOSE USERNAME", key="signup_user")
    password = st.text_input("PAASWORD", type="password", key="signup_pass")
    if st.button("REGISTER"):
        # Handle None values from Streamlit (shouldn't happen, but be safe)
        if username is None:
            username = ""
        if password is None:
            password = ""
            
        # Validate inputs
        if not username or not username.strip():
            st.error("PLEASE ENTER A USERNAME.")
            return
        if not password or not password.strip():
            st.error("PLEASE ENTER A PASSWORD.")
            return
        
        # Trim inputs before registration
        username = username.strip()
        password = password.strip()
        
        if create_user(username, password):
            st.success("REGISTRATION COMPLETE. PROCEED TO LOGIN.")
        else:
            st.error("USERNAME ALREADY EXISTS.")

# Chat Functions
def generate_thread_id():
    return str(uuid.uuid4())

def reset_chat():
    new_thread_id = generate_thread_id()
    st.session_state['thread_id'] = new_thread_id
    # Link new thread to user
    if st.session_state['user']:
        link_thread_to_user(st.session_state['user']['id'], new_thread_id)
    st.session_state['message_history'] = []
    st.rerun()

def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    messages = state.values.get('messages', [])
    formatted_messages = []
    for msg in messages:
        role = 'user' if isinstance(msg, HumanMessage) else 'assistant'
        formatted_messages.append({'role': role, 'content': msg.content})
    return formatted_messages

# Main App Logic
if st.session_state['user'] is None:
    # Auth Screen
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🧬 NEXUS AI")
        st.markdown("AUTHENTICATION REQUIRED FOR SYSTEM ACCESS.")
        
        tab1, tab2 = st.tabs(["LOGIN", "REGISTER"])
        with tab1:
            login()
        with tab2:
            signup()
else:
    # Main Chat Interface
    user_id = st.session_state['user']['id']
    username = st.session_state['user']['username']
    
    # Sidebar
    with st.sidebar:
        st.title(f"WELCOME: {username}")
        if st.button("NEW Chat"):
            reset_chat()
        
        st.markdown("### CHAT HISTORY")
        threads = get_user_threads(user_id)
        
        # If no thread selected yet, select the most recent one or create new
        if st.session_state['thread_id'] is None:
            if threads:
                st.session_state['thread_id'] = threads[0]
                st.session_state['message_history'] = load_conversation(threads[0])
            else:
                reset_chat()
        
        for tid in threads:
            col1, col2 = st.columns([4, 1])
            with col1:
                label = f"ID: {tid[:8]}"
                if st.button(label, key=f"btn_{tid}"):
                    st.session_state['thread_id'] = tid
                    st.session_state['message_history'] = load_conversation(tid)
                    st.rerun()
            with col2:
                if st.button("✖", key=f"del_{tid}", help="Terminate Protocol"):
                    delete_thread(user_id, tid)
                    # If we deleted the active thread, reset state
                    if st.session_state['thread_id'] == tid:
                        st.session_state['thread_id'] = None
                        st.session_state['message_history'] = []
                    st.rerun()
                
        st.markdown("---")
        if st.button("Logout"):
            # Clear session from DB and URL
            if "session" in st.query_params:
                delete_session(st.query_params["session"])
                del st.query_params["session"]
            
            st.session_state['user'] = None
            st.session_state['thread_id'] = None
            st.session_state['message_history'] = []
            st.rerun()

    # Chat Area
    st.header(F"HELLO, {username}")
    
    # Input
    user_input = st.chat_input("START CHATTING...")
    
    # Display Messages from history
    for message in st.session_state['message_history']:
        with st.chat_message(message['role']):
            st.markdown(message['content'])
    
    if user_input:
        # Add user message to history
        st.session_state['message_history'].append({'role': 'user', 'content': user_input})
        # Display user message
        with st.chat_message('user'):
            st.markdown(user_input)
            
        # Config for LangGraph
        config = {
            "configurable": {"thread_id": st.session_state["thread_id"]},
            "metadata": {
                "thread_id": st.session_state["thread_id"],
                "user_id": user_id
            },
            "run_name": "chat_turn",
        }
        
        # Get AI Response and stream it
        with st.chat_message('assistant'):
            def stream_generator():
                for message_chunk, metadata in chatbot.stream(
                    {'messages': [HumanMessage(content=user_input)]},
                    config=config,
                    stream_mode='messages'
                ):
                    if message_chunk.content:
                        yield message_chunk.content
            
            full_response = st.write_stream(stream_generator())
            
        # Add assistant response to history after streaming is complete
        st.session_state['message_history'].append({'role': 'assistant', 'content': full_response})
