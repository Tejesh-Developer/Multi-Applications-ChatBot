# 🚀 GenAI Multi-Functional Application Suite

A modular AI-powered web application that integrates multiple Generative AI capabilities into a single interactive dashboard.  
The platform provides AI chatbot interaction, text generation, speech processing, image summarization, document extraction, and automated PowerPoint generation.

Built using **Python, Streamlit, Grok API, and OpenRouter (LLaMA 3.3 70B)** with secure authentication and role-based access control.

---

# 📌 Features

### 🔐 Authentication System
- Secure login using SQLite database
- Session-based authentication
- Role-Based Access Control (Admin & User)

### 👥 Admin Role Access
- Separate Admin login
- Admin-only panel access
- Restricted feature visibility for normal users

### 🤖 AI Modules
- 💬 AI Chatbot (LLM-powered conversational AI)
- ✍ Text Generation
- 🎤 Speech to Text conversion
- 🔊 Text to Speech synthesis
- 🖼 Image Summarization
- 📄 Document Content Extraction
- 📊 Automated PPT Slide Generation

### 🎨 UI Features
- Professional SaaS-style dashboard
- Sidebar navigation
- User-selectable Dark/Light theme toggle
- Responsive and modular interface

---

# 🧠 Algorithms Used

- Transformer-based Language Model (LLM)
- Automatic Speech Recognition (ASR)
- Text-to-Speech Synthesis (TTS)
- Vision-Language Processing
- Natural Language Processing (NLP)
- Credential Verification Algorithm
- Role-Based Access Control (RBAC)

---

# 🛠 Tech Stack

**Frontend**
- Streamlit

**Backend**
- Python

**AI Integration**
- Grok API
- OpenRouter API
- Model: `llama-3.3-70b-versatile`

**Database**
- SQLite

**Libraries**
- streamlit
- streamlit-option-menu
- google-generativeai
- python-dotenv
- SpeechRecognition
- pyttsx3
- python-pptx
- Pillow
- reportlab

---

# 💻 System Requirements

### Software
- Python 3.9+
- Streamlit
- Internet connection for AI API calls

### Hardware
- Processor: Intel i3 / Ryzen 3 or higher
- RAM: Minimum 4GB (Recommended 8GB)
- Storage: 1GB free space
- GPU: Not required (cloud-based AI)

---

# ⚙ Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/genai-suite.git
cd genai-suite

## 📦 Setup
1. py -3.10 -m venv venv
2. venv\Script\activate
3. pip install -r requirements.txt
4. streamlit run app.py
