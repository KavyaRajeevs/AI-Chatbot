# 🤖 AI Chatbot

A modern, responsive AI-powered chatbot built with Streamlit and Groq API. Features real-time conversations, elegant UI, and persistent chat history.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.0%2B-red.svg)](https://streamlit.io/)
[![Groq](https://img.shields.io/badge/Groq-API-green.svg)](https://groq.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Overview

This AI chatbot provides an intuitive conversational interface powered by Groq's lightning-fast API. Built with Streamlit for rapid deployment and featuring a sleek, modern design with real-time interactions.

## ✨ Features

### 🔧 Current Features
- ✅ **Real-time chat interface** - Instant message delivery and responses
- ✅ **Typing indicators** - Visual feedback during response generation
- ✅ **Message timestamps** - Track conversation history with precise timing
- ✅ **Chat history persistence** - Conversations saved across sessions
- ✅ **Export functionality** - Download chat history in multiple formats
- ✅ **Responsive design** - Works seamlessly on desktop and mobile
- ✅ **Keyword-based responses** - Enhanced context understanding
- ✅ **Easy function modification** - Extensible architecture for customization

### 🚀 Powered By
- **Groq API** - Ultra-fast inference for real-time conversations
- **Streamlit** - Modern web framework for rapid deployment
- **Python** - Robust backend processing

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Groq API key ([Get yours here](https://console.groq.com/))

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/KavyaRajeevs/AIChatbot.git
cd AIChatbot
```

2. **Create virtual environment (recommended)**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
# Create a .env file in the root directory
echo "GROQ_API_KEY=your_groq_api_key_here" > .env
```

5. **Install system dependencies (for voice features)**
```bash
# On Ubuntu/Debian:
sudo apt-get install portaudio19-dev python3-pyaudio

# On macOS:
brew install portaudio

# On Windows:
# PyAudio will be installed via pip
```

6. **Run the application**
```bash
streamlit run app.py
```

7. **Open your browser** to `http://localhost:8501`

## 📦 Dependencies

```txt
streamlit>=1.28.0
groq>=0.4.0
python-dotenv>=1.0.0
pandas>=1.5.0
SpeechRecognition>=3.10.0
pyttsx3>=2.90
pyaudio>=0.2.11
weasyprint>=59.0
reportlab>=4.0.0
```

## 🎨 Configuration

### API Configuration
```python
# config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DEFAULT_MODEL = "deepseek-r1-distill-llama-70b"
MAX_TOKENS = 4096
TEMPERATURE = 0.7

# Available models
AVAILABLE_MODELS = [
    "deepseek-r1-distill-llama-70b",
    "llama-3.1-70b-versatile", 
    "mixtral-8x7b-32768",
    "gemma2-9b-it"
]

# Voice settings
VOICE_ENABLED = True
SPEECH_RATE = 150
SPEECH_VOLUME = 0.8
```

### UI Customization
The chatbot features a highly customizable UI. Modify the CSS in `styles/chat_styles.py` to change:
- Color schemes and gradients
- Message bubble styles and animations
- Typography and spacing
- Voice indicator animations
- Export dialog styling
- Dark/light theme variables
- Mobile responsive breakpoints

## 🔧 Usage

### Basic Usage
1. Start the application
2. Enter your message in the input field
3. Press Enter or click Send
4. Watch the typing indicator as the AI generates a response
5. View conversation history with timestamps

### Advanced Features

#### Export Chat History
```python
# Available export formats with enhanced features
from utils.export_handler import ExportHandler

export_handler = ExportHandler()

# Export options:
- TXT format (formatted conversation)
- JSON format (structured data with metadata)
- CSV format (spreadsheet-compatible)
- HTML format (styled web page)
- PDF format (printable document)

# Usage
file_data, mime_type = export_handler.export_chat(
    messages=conversation_messages,
    format_type="html",
    conversation_id="chat_001"
)
```

#### Voice Interaction
```python
# Voice input and output
from utils.voice_handler import VoiceHandler

voice_handler = VoiceHandler()

# Record voice input
voice_text = voice_handler.record_voice()

# Text-to-speech output
voice_handler.speak_text("Hello! How can I help you?")

# Voice settings
voice_handler.set_speech_rate(150)
voice_handler.set_volume(0.8)
```

#### Conversation Management
```python
# Save and load conversations
from utils.chat_persistence import ChatPersistence

persistence = ChatPersistence()

# Save current conversation
persistence.save_conversation("chat_001", messages)

# Load previous conversation
messages = persistence.load_conversation("chat_001")

# Get conversation list
conversations = persistence.get_conversation_list()
```

## 🏗️ Project Structure

```
ai-chatbot/
├── app.py                     # Main Streamlit application
├── Dockerfile                 # Docker configuration
├── requirements.txt           # Python dependencies
├── .env                      # Environment variables
├── .gitignore
├── README.md
├── config/
│   ├── __init__.py
│   └── settings.py           # Configuration settings
├── styles/
│   ├── __init__.py
│   └── chat_styles.py        # Enhanced CSS styling
├── utils/
│   ├── __init__.py
│   ├── export_handler.py     # Multi-format export functionality
│   ├── voice_handler.py      # Voice input/output handling
│   ├── chat_persistence.py   # Chat history management
│   └── response_handler.py   # AI response processing
└── data/
    └── conversations/        # Saved conversation files
```

## 🔌 API Integration

### Groq API Setup
```python
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_ai_response(message, history):
    response = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message}
        ],
        max_tokens=1024,
        temperature=0.7
    )
    return response.choices[0].message.content
```

## 🎯 Customization

### Adding New Features
1. **Custom Response Logic**: Modify `chat_handler.py`
2. **UI Components**: Update `app.py` with new Streamlit elements
3. **Styling**: Enhance `styles.py` with custom CSS
4. **Export Options**: Extend `utils/export.py`

### Example: Adding Voice Input
```python
# Add to app.py
import speech_recognition as sr

def voice_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening...")
        audio = r.listen(source)
    return r.recognize_google(audio)
```

## 🚀 Deployment

### Local Development
```bash
streamlit run app.py
```

### Production Deployment

#### Streamlit Cloud
1. Push code to GitHub
2. Connect to [Streamlit Cloud](https://streamlit.io/cloud)
3. Deploy with one click



## 🛡️ Security & Privacy

- **API Security**: API keys securely stored in environment variables
- **Data Privacy**: Conversations stored locally, no external data sharing
- **Input Validation**: Comprehensive input sanitization and validation
- **Rate Limiting**: Built-in API rate limiting and error handling
- **Voice Privacy**: Voice processing handled locally when possible
- **Export Security**: Secure file generation and download handling
- **HTTPS Support**: SSL/TLS encryption for production deployments

## 🙏 Acknowledgments

- [Groq](https://groq.com/) for the lightning-fast API
- [Streamlit](https://streamlit.io/) for the amazing framework
- [Python](https://python.org/) community for excellent libraries

## 🔄 Changelog

### v2.0.0 (Latest)
- ✅ **Enhanced UI/UX** - Modern gradient design and animations
- ✅ **Voice Integration** - Full voice input and output support
- ✅ **Multi-format Export** - TXT, JSON, CSV, HTML, PDF export options
- ✅ **Conversation Management** - Save, load, and manage chat history
- ✅ **Multiple AI Models** - Support for different Groq models
- ✅ **Advanced Statistics** - Detailed conversation analytics
- ✅ **Docker Support** - Containerized deployment
- ✅ **Enhanced Accessibility** - Screen reader support and keyboard navigation
- ✅ **Mobile Optimization** - Improved mobile responsive design

### Planned Features
- 🔄 **Multi-language support** - Support for multiple languages
- 🔄 **Plugin system** - Extensible plugin architecture
- 🔄 **Advanced analytics** - Detailed conversation insights
- 🔄 **Custom AI training** - Fine-tune responses for specific use cases
- 🔄 **Integration APIs** - Connect with external services
- 🔄 **Mobile app** - Native mobile application
- 🔄 **Real-time collaboration** - Multiple users in same conversation
- 🔄 **Message reactions** - Like/dislike message functionality

---

**⭐ Star this repository if you find it useful!**

Made with ❤️ by [Kavya Rajeev](https://github.com/KavyaRajeevs)
