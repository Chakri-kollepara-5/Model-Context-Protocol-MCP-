import streamlit as st
from utils import run_agent_sync

# Basic page setup
st.set_page_config(
    page_title="Learning Path Generator",
    page_icon="📚",
    layout="centered"
)

# Simple CSS for better spacing
st.markdown("""
    <style>
        .stTextInput input, .stTextArea textarea {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 10px;
        }
        .stButton button {
            width: 100%;
            border-radius: 8px;
            padding: 12px;
            background-color: #4CAF50;
            color: white;
            border: none;
        }
        .stButton button:hover {
            background-color: #45a049;
        }
        .stButton button:disabled {
            background-color: #cccccc;
        }
        .stProgress > div > div > div {
            background-color: #4CAF50;
        }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("Learning Path Generator")
st.write("Create personalized learning paths from your goals")

# Initialize session state (unchanged)
if 'current_step' not in st.session_state:
    st.session_state.current_step = ""
if 'progress' not in st.session_state:
    st.session_state.progress = 0
if 'last_section' not in st.session_state:
    st.session_state.last_section = ""
if 'is_generating' not in st.session_state:
    st.session_state.is_generating = False

# Configuration sidebar
with st.sidebar:
    st.header("Settings")
    
    google_api_key = st.text_input("Google API Key", type="password")
    
    st.subheader("Integration URLs")
    youtube_pipedream_url = st.text_input("YouTube URL (Required)")
    
    secondary_tool = st.radio(
        "Secondary Tool:",
        ["Drive", "Notion"]
    )

    if secondary_tool == "Drive":
        drive_pipedream_url = st.text_input("Drive URL")
        notion_pipedream_url = None
    else:
        notion_pipedream_url = st.text_input("Notion URL")
        drive_pipedream_url = None

# Main content
st.header("Your Learning Goal")
user_goal = st.text_area(
    "Describe what you want to learn:",
    placeholder="Example: 'Learn Python basics in 1 week'",
    height=100
)

# Progress display
progress_bar = st.progress(0)
status_text = st.empty()

def update_progress(message: str):
    """Simplified progress update function"""
    st.session_state.current_step = message
    
    # Progress logic (unchanged)
    if "Setting up agent with tools" in message:
        st.session_state.progress = 0.1
    elif "Added Google Drive integration" in message or "Added Notion integration" in message:
        st.session_state.progress = 0.3
    elif "Creating AI agent" in message:
        st.session_state.progress = 0.5
    elif "Generating your learning path" in message:
        st.session_state.progress = 0.7
    elif "Learning path generation complete" in message:
        st.session_state.progress = 1.0
        st.session_state.is_generating = False
    
    progress_bar.progress(st.session_state.progress)
    status_text.write(f"Status: {message}")

# Generate button
if st.button("Generate Learning Path", disabled=st.session_state.is_generating):
    if not google_api_key:
        st.error("Please enter your Google API key")
    elif not youtube_pipedream_url:
        st.error("YouTube URL is required")
    elif (secondary_tool == "Drive" and not drive_pipedream_url) or (secondary_tool == "Notion" and not notion_pipedream_url):
        st.error(f"Please enter your {secondary_tool} URL")
    elif not user_goal:
        st.warning("Please enter your learning goal")
    else:
        try:
            st.session_state.is_generating = True
            st.session_state.progress = 0
            
            result = run_agent_sync(
                google_api_key=google_api_key,
                youtube_pipedream_url=youtube_pipedream_url,
                drive_pipedream_url=drive_pipedream_url,
                notion_pipedream_url=notion_pipedream_url,
                user_goal=user_goal,
                progress_callback=update_progress
            )
            
            if result and "messages" in result:
                st.success("Your learning path is ready!")
                for msg in result["messages"]:
                    st.markdown(f"• {msg.content}")
            else:
                st.error("No results were generated")
                st.session_state.is_generating = False
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.session_state.is_generating = False
