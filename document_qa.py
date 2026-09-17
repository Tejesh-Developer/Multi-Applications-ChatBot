import os
import streamlit as st
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
import requests
import base64
import json
import re

load_dotenv()

# ── Try importing PDF libraries ───────────────────────────────────────────────
try:
    import fitz  # PyMuPDF
    PYMUPDF_OK = True
except ImportError:
    PYMUPDF_OK = False

try:
    import pdfplumber
    PDFPLUMBER_OK = True
except ImportError:
    PDFPLUMBER_OK = False


# ── PDF Text Extraction ───────────────────────────────────────────────────────

def extract_text_from_pdf(file_bytes):
    """Extract all text from PDF pages."""
    if PYMUPDF_OK:
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            pages_text = []
            for i, page in enumerate(doc, start=1):
                text = page.get_text().strip()
                if text:
                    pages_text.append({"page": i, "text": text})
            doc.close()
            return pages_text
        except Exception as e:
            pass

    if PDFPLUMBER_OK:
        try:
            pages_text = []
            with pdfplumber.open(BytesIO(file_bytes)) as pdf:
                for i, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text()
                    if text and text.strip():
                        pages_text.append({"page": i, "text": text.strip()})
            return pages_text
        except Exception as e:
            pass

    return []


def build_context(pages_text, max_chars=12000):
    """Combine page texts into a single context string."""
    full_text = ""
    for p in pages_text:
        full_text += f"\n--- Page {p['page']} ---\n{p['text']}\n"
    return full_text[:max_chars]


# ── AI Q&A ────────────────────────────────────────────────────────────────────

def ask_question(context, question, chat_history):
    """Send document context + question to AI."""

    # Build history string
    history_str = ""
    for msg in chat_history[-6:]:  # last 6 exchanges for context
        role = "User" if msg["role"] == "user" else "Assistant"
        history_str += f"{role}: {msg['content']}\n"

    prompt = f"""You are a helpful Document Q&A assistant. 
A user has uploaded a document. Answer questions ONLY based on the document content below.
If the answer is not found in the document, say "This information is not found in the document."
Be precise, structured, and cite page numbers when possible.

=== DOCUMENT CONTENT ===
{context}
=== END OF DOCUMENT ===

{f"=== CONVERSATION HISTORY ==={chr(10)}{history_str}=== END ===" if history_str else ""}

User's Question: {question}

Answer:"""

    try:
        # Try Groq first
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            from groq import Groq
            client = Groq(api_key=groq_key)
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="openai/gpt-oss-120b",
                max_tokens=1024,
            )
            return response.choices[0].message.content

        # Fallback: OpenRouter
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        if openrouter_key:
            resp = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openrouter_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "meta-llama/llama-3.2-11b-vision-instruct",
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            return resp.json()["choices"][0]["message"]["content"]

    except Exception as e:
        return f"⚠ Error: {str(e)}"

    return "⚠ No API key found. Please set GROQ_API_KEY or OPENROUTER_API_KEY."


def generate_summary(context):
    """Auto-generate document summary."""
    prompt = f"""Summarize this document in a clear, structured format:

1. Main Topic
2. Key Points (bullet points)
3. Important Data/Numbers
4. Conclusion

Document:
{context[:8000]}"""

    try:
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            from groq import Groq
            client = Groq(api_key=groq_key)
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                max_tokens=1024,
            )
            return response.choices[0].message.content

        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        if openrouter_key:
            resp = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openrouter_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "meta-llama/llama-3.2-11b-vision-instruct",
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠ Error: {str(e)}"


def generate_quiz(context):
    """Auto-generate quiz questions from document."""
    prompt = f"""Based on this document, generate 5 quiz questions with answers.
Format exactly like this:
Q1: [question]
A1: [answer]

Q2: [question]
A2: [answer]

(and so on...)

Document:
{context[:6000]}"""

    try:
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            from groq import Groq
            client = Groq(api_key=groq_key)
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                max_tokens=1024,
            )
            return response.choices[0].message.content
    except Exception as e:
        return f"⚠ Error: {str(e)}"


# ── Main Run ──────────────────────────────────────────────────────────────────

def run():

    # Styles
    st.markdown("""
    <style>
    .hero-banner {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        padding: 40px; border-radius: 25px; margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    }
    .hero-title { font-size: 42px; font-weight: 800; color: white; margin-bottom: 10px; }
    .hero-subtitle { font-size: 18px; color: #cbd5e1; }

    .doc-info-card {
        background: #111827; border: 1px solid #1f2937;
        border-radius: 14px; padding: 18px 22px; margin-bottom: 20px;
    }
    .doc-stat {
        display: inline-block; background: #1f2937; color: #38bdf8;
        padding: 4px 14px; border-radius: 20px; font-size: 13px;
        margin: 4px 4px 4px 0; border: 1px solid #374151;
    }
    .chat-user {
        background: #1e3a5f; border-radius: 14px 14px 4px 14px;
        padding: 12px 16px; margin: 8px 0; color: #e2e8f0;
        font-size: 14px; max-width: 85%; margin-left: auto;
        border: 1px solid #2563eb33;
    }
    .chat-ai {
        background: #111827; border-radius: 14px 14px 14px 4px;
        padding: 12px 16px; margin: 8px 0; color: #e2e8f0;
        font-size: 14px; max-width: 90%;
        border: 1px solid #1f2937;
    }
    .chat-label-user { font-size: 11px; color: #60a5fa; margin-bottom: 4px; text-align:right; }
    .chat-label-ai   { font-size: 11px; color: #4ade80; margin-bottom: 4px; }

    .suggestion-btn {
        background: #1f2937; border: 1px solid #374151;
        border-radius: 20px; padding: 6px 14px;
        font-size: 12px; color: #94a3b8; cursor: pointer;
        margin: 3px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Hero
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">📝 Document Q&A</div>
        <div class="hero-subtitle">
            Upload any PDF and chat with it — ask questions, get summaries, generate quizzes!
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Session state init ────────────────────────────────────────────────────
    if "doc_qa_history"  not in st.session_state: st.session_state.doc_qa_history  = []
    if "doc_context"     not in st.session_state: st.session_state.doc_context     = ""
    if "doc_pages"       not in st.session_state: st.session_state.doc_pages       = []
    if "doc_name"        not in st.session_state: st.session_state.doc_name        = ""
    if "doc_loaded"      not in st.session_state: st.session_state.doc_loaded      = False
    if "show_quiz"       not in st.session_state: st.session_state.show_quiz       = False

    # ── File Upload ───────────────────────────────────────────────────────────
    col_upload, col_clear = st.columns([4, 1])

    with col_upload:
        uploaded_file = st.file_uploader(
            "Upload PDF Document",
            type=["pdf"],
            help="Upload a PDF — text will be extracted and you can Q&A with it"
        )

    with col_clear:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑 Clear Chat", use_container_width=True):
            st.session_state.doc_qa_history = []
            st.session_state.show_quiz = False
            st.rerun()

    # ── Process uploaded file ─────────────────────────────────────────────────
    if uploaded_file:
        file_bytes = uploaded_file.read()
        file_name  = uploaded_file.name

        # Re-process only if new file uploaded
        if file_name != st.session_state.doc_name:
            with st.spinner("📖 Reading document..."):
                pages = extract_text_from_pdf(file_bytes)
                context = build_context(pages)

            if pages and context:
                st.session_state.doc_pages   = pages
                st.session_state.doc_context = context
                st.session_state.doc_name    = file_name
                st.session_state.doc_loaded  = True
                st.session_state.doc_qa_history = []
                st.session_state.show_quiz   = False
            else:
                st.error("⚠ Could not extract text from this PDF. Make sure it's a text-based PDF (not scanned image). Install: `pip install pymupdf`")
                st.session_state.doc_loaded = False

    # ── Document Info Card ────────────────────────────────────────────────────
    if st.session_state.doc_loaded:
        pages  = st.session_state.doc_pages
        ctx    = st.session_state.doc_context
        name   = st.session_state.doc_name
        words  = len(ctx.split())
        chars  = len(ctx)
        n_pages = len(pages)

        st.markdown(f"""
        <div class="doc-info-card">
            <b style="color:#e2e8f0;">📄 {name}</b><br><br>
            <span class="doc-stat">📄 {n_pages} pages</span>
            <span class="doc-stat">📝 {words:,} words</span>
            <span class="doc-stat">🔤 {chars:,} chars</span>
            <span class="doc-stat">✅ Ready to Q&A</span>
        </div>
        """, unsafe_allow_html=True)

        # ── Action Tabs ───────────────────────────────────────────────────────
        tab1, tab2, tab3 = st.tabs(["💬 Chat Q&A", "📋 Auto Summary", "🧠 Quiz Generator"])

        # ════════════════════════════════════════════════
        # TAB 1 — CHAT Q&A
        # ════════════════════════════════════════════════
        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)

            # Suggested questions
            st.markdown("**💡 Suggested Questions:**")
            suggestions = [
                "What is this document about?",
                "What are the key points?",
                "List all important numbers/data",
                "What is the conclusion?",
                "Who are the people mentioned?",
            ]
            cols = st.columns(len(suggestions))
            for i, sug in enumerate(suggestions):
                with cols[i]:
                    if st.button(sug, key=f"sug_{i}", use_container_width=True):
                        # Add to chat as user question
                        st.session_state.doc_qa_history.append({
                            "role": "user", "content": sug
                        })
                        with st.spinner("Thinking..."):
                            answer = ask_question(
                                st.session_state.doc_context,
                                sug,
                                st.session_state.doc_qa_history[:-1]
                            )
                        st.session_state.doc_qa_history.append({
                            "role": "assistant", "content": answer
                        })
                        st.rerun()

            st.markdown("---")

            # Chat history display
            if st.session_state.doc_qa_history:
                for msg in st.session_state.doc_qa_history:
                    if msg["role"] == "user":
                        st.markdown(f"""
                        <div style="display:flex;justify-content:flex-end;">
                            <div>
                                <div class="chat-label-user">You</div>
                                <div class="chat-user">{msg['content']}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div>
                            <div class="chat-label-ai">🤖 AI Assistant</div>
                            <div class="chat-ai">{msg['content']}</div>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # Download chat history
                chat_text = "\n\n".join([
                    f"{'You' if m['role']=='user' else 'AI'}: {m['content']}"
                    for m in st.session_state.doc_qa_history
                ])
                st.download_button(
                    "⬇ Download Chat History",
                    data=chat_text,
                    file_name=f"{name.replace('.pdf','')}_qa_chat.txt",
                    mime="text/plain"
                )
            else:
                st.info("👆 Click a suggested question above or type your own below to start!")

            # Chat input
            st.markdown("<br>", unsafe_allow_html=True)
            user_input = st.chat_input(
                f"Ask anything about '{name}'...",
                key="doc_qa_input"
            )

            if user_input:
                st.session_state.doc_qa_history.append({
                    "role": "user", "content": user_input
                })
                with st.spinner("🤖 Reading document and thinking..."):
                    answer = ask_question(
                        st.session_state.doc_context,
                        user_input,
                        st.session_state.doc_qa_history[:-1]
                    )
                st.session_state.doc_qa_history.append({
                    "role": "assistant", "content": answer
                })

                # Log usage
                try:
                    import database
                    database.log_usage(
                        st.session_state.get("username", "unknown"),
                        "Document Q&A"
                    )
                except:
                    pass

                st.rerun()

        # ════════════════════════════════════════════════
        # TAB 2 — AUTO SUMMARY
        # ════════════════════════════════════════════════
        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("##### 📋 AI will read the entire document and generate a structured summary.")

            if st.button("🚀 Generate Summary", key="gen_summary", use_container_width=False):
                with st.spinner("📖 Reading and summarizing document..."):
                    summary = generate_summary(st.session_state.doc_context)
                st.session_state["doc_summary"] = summary

                try:
                    import database
                    database.log_usage(
                        st.session_state.get("username", "unknown"),
                        "Document Q&A"
                    )
                except:
                    pass

            if "doc_summary" in st.session_state and st.session_state.doc_summary:
                st.markdown("""
                <div style="background:#111827;border:1px solid #1f2937;
                     border-radius:14px;padding:20px;margin-top:16px;">
                """, unsafe_allow_html=True)
                st.markdown(st.session_state.doc_summary)
                st.markdown("</div>", unsafe_allow_html=True)

                st.download_button(
                    "⬇ Download Summary",
                    data=st.session_state.doc_summary,
                    file_name=f"{name.replace('.pdf','')}_summary.txt",
                    mime="text/plain"
                )

        # ════════════════════════════════════════════════
        # TAB 3 — QUIZ GENERATOR
        # ════════════════════════════════════════════════
        with tab3:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("##### 🧠 AI will generate 5 quiz questions based on the document content.")

            if st.button("🎯 Generate Quiz", key="gen_quiz", use_container_width=False):
                with st.spinner("🧠 Generating quiz questions..."):
                    quiz_text = generate_quiz(st.session_state.doc_context)
                st.session_state["doc_quiz"] = quiz_text
                st.session_state.show_quiz = True

                try:
                    import database
                    database.log_usage(
                        st.session_state.get("username", "unknown"),
                        "Document Q&A"
                    )
                except:
                    pass

            if st.session_state.show_quiz and "doc_quiz" in st.session_state:
                quiz_raw = st.session_state.doc_quiz

                # Parse Q&A pairs
                pairs = re.findall(
                    r'Q(\d+)[:\.]?\s*(.+?)\s*A\1[:\.]?\s*(.+?)(?=Q\d|$)',
                    quiz_raw, re.DOTALL
                )

                if pairs:
                    for num, question, answer in pairs:
                        with st.expander(f"❓ Q{num}: {question.strip()}"):
                            st.markdown(f"✅ **Answer:** {answer.strip()}")
                else:
                    # Fallback: show raw text
                    st.markdown("""
                    <div style="background:#111827;border:1px solid #1f2937;
                         border-radius:14px;padding:20px;">
                    """, unsafe_allow_html=True)
                    st.markdown(quiz_raw)
                    st.markdown("</div>", unsafe_allow_html=True)

                st.download_button(
                    "⬇ Download Quiz",
                    data=quiz_raw,
                    file_name=f"{name.replace('.pdf','')}_quiz.txt",
                    mime="text/plain"
                )

    else:
        # No document uploaded yet — show instructions
        st.markdown("""
        <div style="background:#111827;border:1px dashed #374151;
             border-radius:16px;padding:40px;text-align:center;margin-top:20px;">
            <div style="font-size:48px;margin-bottom:16px;">📄</div>
            <div style="font-size:20px;font-weight:700;color:#e2e8f0;margin-bottom:12px;">
                Upload a PDF to get started
            </div>
            <div style="font-size:14px;color:#64748b;max-width:400px;margin:0 auto;">
                Supports text-based PDFs. After upload you can:<br><br>
                💬 <b>Chat Q&A</b> — Ask any question about the document<br>
                📋 <b>Auto Summary</b> — Get structured summary instantly<br>
                🧠 <b>Quiz Generator</b> — Generate quiz from document content
            </div>
        </div>
        """, unsafe_allow_html=True)

        if not PYMUPDF_OK and not PDFPLUMBER_OK:
            st.warning("⚠ PDF parsing libraries not installed. Run: `pip install pymupdf pdfplumber`")