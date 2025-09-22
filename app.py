import streamlit as st
import os
from datetime import datetime
from groq import Groq
import json
import pandas as pd
from utils.export_handler import ExportHandler
from utils.voice_handler import VoiceHandler
from utils.chat_persistence import ChatPersistence
from utils.response_handler import ResponseHandler
from styles import get_chat_styles

from dotenv import load_dotenv
load_dotenv()
# Load environment variables
GROQ_API_KEY = os.getenv("groq_api_key")
UI_CONFIG = os.getenv("UI_CONFIG", "{}")

# Set page configuration
st.set_page_config(
    page_title="AI Chatbot Pro",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styles
st.markdown(get_chat_styles(), unsafe_allow_html=True)

# Initialize handlers
@st.cache_resource
def initialize_handlers():
    export_handler = ExportHandler()
    voice_handler = VoiceHandler()
    chat_persistence = ChatPersistence()
    response_handler = ResponseHandler()
    return export_handler, voice_handler, chat_persistence, response_handler

export_handler, voice_handler, chat_persistence, response_handler = initialize_handlers()

# Initialize session state
def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add welcome message
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Hello! I'm your AI assistant. How can I help you today?",
            "timestamp": datetime.now().strftime("%H:%M"),
            "message_id": "welcome_001"
        })
    
    if "is_typing" not in st.session_state:
        st.session_state.is_typing = False
    
    if "voice_enabled" not in st.session_state:
        st.session_state.voice_enabled = False
    
    if "auto_speak" not in st.session_state:
        st.session_state.auto_speak = False
    
    if "current_model" not in st.session_state:
        st.session_state.current_model = "deepseek-r1-distill-llama-70b"
    
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

initialize_session_state()

def get_bot_response(user_message):
    """Enhanced bot response with better error handling and model selection"""
    try:
        if not GROQ_API_KEY:
            return "⚠️ API key not configured. Please check your settings."
        
        client = Groq(api_key=GROQ_API_KEY)
        
        # Prepare messages for the API
        api_messages = []
        for msg in st.session_state.messages[-10:]:  # Keep last 10 messages for context
            if msg["role"] in ["user", "assistant"]:
                api_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Add the latest user message if not already present
        if not api_messages or api_messages[-1]["role"] != "user":
            api_messages.append({"role": "user", "content": user_message})

        # Call Groq API with selected model
        completion = client.chat.completions.create(
            model=st.session_state.current_model,
            messages=api_messages,
            temperature=0.7,
            max_completion_tokens=4096,
            top_p=0.95,
            stream=False,
            stop=None,
        )

        response = completion.choices[0].message.content.strip()
        
        # Clean response from thinking tags
        import re
        response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL).strip()
        
        return response
        
    except Exception as e:
        return f"❌ Error: {str(e)}"

# App header with enhanced styling
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h1 style="color: #667eea; margin-bottom: 0.5rem;">🤖 AI Chatbot Pro</h1>
        <p style="color: #666; font-size: 1.1rem;">Powered by Groq API</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Main chat interface
chat_container = st.container()

with chat_container:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Display messages with enhanced formatting
    for i, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message" id="msg_{i}">
                <div class="message-avatar user-avatar">👤</div>
                <div class="message-content">
                    <div>{message["content"]}</div>
                    <div class="message-time">{message["timestamp"]}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message bot-message" id="msg_{i}">
                <div class="message-avatar bot-avatar">🤖</div>
                <div class="message-content">
                    <div>{message["content"]}</div>
                    <div class="message-time">{message["timestamp"]}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Show typing indicator
    if st.session_state.is_typing:
        st.markdown("""
        <div class="chat-message bot-message typing-message">
            <div class="message-avatar bot-avatar">🤖</div>
            <div class="message-content">
                <div class="typing-indicator">
                    Bot is typing<span class="typing-dots"><span></span><span></span><span></span></span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Enhanced input section
st.markdown("### 💬 Send a message")

# Voice input section
if st.session_state.voice_enabled:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("🎤 Voice input is enabled. Click 'Start Recording' to speak.")
    with col2:
        if st.button("🎤 Start Recording", key="voice_record"):
            with st.spinner("Listening..."):
                voice_text = voice_handler.record_voice()
                if voice_text:
                    st.session_state.voice_input = voice_text
                    st.success(f"Recorded: {voice_text[:50]}...")

# Create input form with enhanced features
with st.form(key="chat_form", clear_on_submit=True):
    col1, col2, col3 = st.columns([4, 1, 1])
    
    with col1:
        user_input = st.text_input(
            "Type your message here...",
            placeholder="Ask me anything! 🚀",
            label_visibility="collapsed",
            value=st.session_state.get("voice_input", "")
        )
    
    with col2:
        send_button = st.form_submit_button("Send 📤", type="primary", use_container_width=True)
    
    with col3:
        if st.form_submit_button("🎤 Voice", use_container_width=True):
            st.session_state.voice_enabled = not st.session_state.voice_enabled
            st.rerun()

# Handle message sending
if send_button and user_input.strip():
    # Clear voice input
    if "voice_input" in st.session_state:
        del st.session_state.voice_input
    
    # Add user message
    current_time = datetime.now().strftime("%H:%M")
    message_id = f"msg_{len(st.session_state.messages)}"
    
    st.session_state.messages.append({
        "role": "user",
        "content": user_input.strip(),
        "timestamp": current_time,
        "message_id": message_id
    })
    
    # Set typing indicator
    st.session_state.is_typing = True
    st.rerun()

# Process bot response
if st.session_state.is_typing:
    # Get bot response
    bot_response = get_bot_response(st.session_state.messages[-1]["content"])
    
    # Add bot response
    current_time = datetime.now().strftime("%H:%M")
    message_id = f"msg_{len(st.session_state.messages)}"
    
    st.session_state.messages.append({
        "role": "assistant",
        "content": bot_response,
        "timestamp": current_time,
        "message_id": message_id
    })
    
    # Auto-speak if enabled
    if st.session_state.auto_speak:
        voice_handler.speak_text(bot_response)
    
    # Remove typing indicator
    st.session_state.is_typing = False
    
    # Save conversation
    chat_persistence.save_conversation(st.session_state.conversation_id, st.session_state.messages)
    
    st.rerun()

# Enhanced sidebar with more features
with st.sidebar:
    st.header("🛠️ Chat Controls")
    
    # Model selection
    st.subheader("🧠 AI Model")
    models = [
        "deepseek-r1-distill-llama-70b",
        "llama-3.1-70b-versatile",
        "mixtral-8x7b-32768",
        "gemma2-9b-it"
    ]
    
    selected_model = st.selectbox(
        "Choose AI Model:",
        models,
        index=models.index(st.session_state.current_model)
    )
    
    if selected_model != st.session_state.current_model:
        st.session_state.current_model = selected_model
        st.success(f"Model changed to: {selected_model}")
    
    st.markdown("---")
    
    # Voice settings
    st.subheader("🎤 Voice Settings")
    st.session_state.voice_enabled = st.checkbox("Enable Voice Input", st.session_state.voice_enabled)
    st.session_state.auto_speak = st.checkbox("Auto-speak Bot Responses", st.session_state.auto_speak)
    
    if st.button("🔊 Test Voice", use_container_width=True):
        voice_handler.speak_text("Hello! Voice output is working correctly.")
    
    st.markdown("---")
    
    # Chat actions
    st.subheader("🔧 Chat Actions")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Hello! I'm your AI assistant. How can I help you today?",
                "timestamp": datetime.now().strftime("%H:%M"),
                "message_id": "welcome_001"
            })
            st.session_state.is_typing = False
            st.rerun()
    
    with col2:
        if st.button("💾 Save Chat", use_container_width=True):
            chat_persistence.save_conversation(st.session_state.conversation_id, st.session_state.messages)
            st.success("Chat saved!")
    
    st.markdown("---")
    
    # Chat statistics
    st.subheader("📊 Chat Statistics")
    total_messages = len(st.session_state.messages)
    user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
    bot_messages = len([m for m in st.session_state.messages if m["role"] == "assistant"])
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total", total_messages)
        st.metric("Your Messages", user_messages)
    with col2:
        st.metric("Bot Messages", bot_messages)
        if total_messages > 0:
            st.metric("Response Rate", f"{(bot_messages/max(user_messages, 1)):.1f}x")
    
    st.markdown("---")
    
    # Enhanced export options
    st.subheader("💾 Export Options")
    
    if st.session_state.messages:
        export_format = st.selectbox(
            "Export Format:",
            ["TXT", "JSON", "CSV", "HTML", "PDF"]
        )
        
        if st.button(f"📄 Export as {export_format}", use_container_width=True):
            try:
                file_data, mime_type = export_handler.export_chat(
                    st.session_state.messages,
                    export_format.lower(),
                    st.session_state.conversation_id
                )
                
                st.download_button(
                    label=f"💾 Download {export_format} File",
                    data=file_data,
                    file_name=f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{export_format.lower()}",
                    mime=mime_type,
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Export failed: {str(e)}")
    
    st.markdown("---")
    
    # Load previous conversations
    st.subheader("📚 Previous Conversations")
    saved_conversations = chat_persistence.get_conversation_list()
    
    if saved_conversations:
        selected_conv = st.selectbox(
            "Load Conversation:",
            ["Select..."] + saved_conversations
        )
        
        if selected_conv != "Select..." and st.button("📂 Load", use_container_width=True):
            loaded_messages = chat_persistence.load_conversation(selected_conv)
            if loaded_messages:
                st.session_state.messages = loaded_messages
                st.session_state.conversation_id = selected_conv
                st.success(f"Loaded: {selected_conv}")
                st.rerun()
    else:
        st.info("No saved conversations found.")
    
    st.markdown("---")
    
    # System information
    with st.expander("ℹ️ System Information"):
        st.write(f"**Model:** {st.session_state.current_model}")
        st.write(f"**Conversation ID:** {st.session_state.conversation_id}")
        st.write(f"**Voice Enabled:** {'Yes' if st.session_state.voice_enabled else 'No'}")
        st.write(f"**Auto-speak:** {'Yes' if st.session_state.auto_speak else 'No'}")
    
    # Features list
    with st.expander("✨ Features"):
        features = [
            "✅ Real-time chat interface",
            "✅ Multiple AI models",
            "✅ Voice input & output",
            "✅ Typing indicators",
            "✅ Message timestamps",
            "✅ Chat persistence",
            "✅ Multiple export formats",
            "✅ Conversation history",
            "✅ Responsive design",
            "✅ Dark mode support"
        ]
        for feature in features:
            st.write(feature)
    
    st.markdown("---")
    
    # Links and info
    st.markdown("🔗 **Links:**")
    st.markdown("[![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat&logo=github&logoColor=white)](https://github.com/KavyaRajeevs/AIChatbot)")
    st.markdown("[![Groq](https://img.shields.io/badge/Groq-API-green.svg)](https://groq.com/)")

# Enhanced footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 1rem;">
    <p style="color: #888; margin-bottom: 0.5rem;">
        Made with ❤️ by <strong>Kavya Rajeev</strong>
    </p>
    <p style="color: #aaa; font-size: 0.9rem;">
        Powered by Groq API | Enhanced with Voice & Export Features
    </p>
</div>
""", unsafe_allow_html=True)

# Auto-scroll to bottom (JavaScript)
st.markdown("""
<script>
    function scrollToBottom() {
        var chatContainer = document.querySelector('.chat-container');
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    }
    
    // Auto-scroll when new messages are added
    setTimeout(scrollToBottom, 100);
</script>
""", unsafe_allow_html=True)