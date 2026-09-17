import os
import streamlit as st
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
import requests
import base64
import database
database.log_usage(st.session_state.get("username", "unknown"), "Extract from File")

load_dotenv()

# ─── PDF Parsing Helpers ──────────────────────────────────────────────────────

def extract_pdf_text(file_bytes):
    """Extract all text from PDF using PyMuPDF (fitz)."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page_num, page in enumerate(doc, start=1):
            page_text = page.get_text()
            if page_text.strip():
                text += f"\n--- Page {page_num} ---\n{page_text}"
        doc.close()
        return text.strip() if text.strip() else None
    except ImportError:
        return None
    except Exception as e:
        return None


def extract_pdf_tables(file_bytes):
    """Extract tables from PDF using pdfplumber."""
    try:
        import pdfplumber
        import pandas as pd
        tables_found = []
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                page_tables = page.extract_tables()
                for t_idx, table in enumerate(page_tables, start=1):
                    if table and len(table) > 1:
                        # df = pd.DataFrame(table[1:], columns=table[0])
                        df = pd.DataFrame(table[1:])
                        df.columns = [f"Col_{i}" for i in range(len(df.columns))]
                        tables_found.append({
                            "page": page_num,
                            "table_num": t_idx,
                            "df": df,
                            "raw": table
                        })
        return tables_found
    except ImportError:
        return []
    except Exception:
        return []


def extract_pdf_images(file_bytes):
    """Extract embedded images from PDF using PyMuPDF."""
    try:
        import fitz
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        images = []
        for page_num, page in enumerate(doc, start=1):
            image_list = page.get_images(full=True)
            for img_idx, img_info in enumerate(image_list, start=1):
                xref = img_info[0]
                base_image = doc.extract_image(xref)
                img_bytes = base_image["image"]
                img_ext   = base_image["ext"]
                images.append({
                    "page": page_num,
                    "index": img_idx,
                    "ext": img_ext,
                    "bytes": img_bytes,
                })
        doc.close()
        return images
    except ImportError:
        return []
    except Exception:
        return []


def pdf_to_page_images(file_bytes):
    """Render each PDF page as an image (for vision AI analysis)."""
    try:
        import fitz
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        page_images = []
        for page_num, page in enumerate(doc, start=1):
            mat = fitz.Matrix(2.0, 2.0)   # 2x zoom for clarity
            pix = page.get_pixmap(matrix=mat)
            img_bytes = pix.tobytes("png")
            page_images.append({"page": page_num, "bytes": img_bytes})
        doc.close()
        return page_images
    except ImportError:
        return []
    except Exception:
        return []


def call_vision_ai(prompt, image_bytes, mime_type="image/png"):
    """Send image + prompt to LLaMA Vision via OpenRouter."""
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json"
        },
        json={
            "model": "meta-llama/llama-3.2-90b-vision-instruct",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{encoded}"
                            }
                        }
                    ]
                }
            ]
        }
    )
    result = response.json()
    if "choices" in result:
        return result["choices"][0]["message"]["content"]
    return f"API Error: {result}"


def call_text_ai(prompt, context_text):
    """Send extracted text + prompt to LLaMA via OpenRouter."""
    full_prompt = f"""{prompt}

--- DOCUMENT CONTENT ---
{context_text[:12000]}
--- END OF DOCUMENT ---

Please answer based on the document content above."""

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json"
        },
        json={
            "model": "meta-llama/llama-3.2-11b-vision-instruct",
            "messages": [{"role": "user", "content": full_prompt}]
        }
    )
    result = response.json()
    if "choices" in result:
        return result["choices"][0]["message"]["content"]
    return f"API Error: {result}"


# ─── Main Run Function ────────────────────────────────────────────────────────

def run():

    # ── Styles ──────────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    .hero-banner {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        padding: 40px;
        border-radius: 25px;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    }
    .hero-title {
        font-size: 42px;
        font-weight: 800;
        color: white;
        margin-bottom: 10px;
    }
    .hero-subtitle {
        font-size: 18px;
        color: #cbd5e1;
    }
    .extract-box {
        background-color: #161B22;
        padding: 20px;
        border-radius: 15px;
        margin-top: 20px;
    }
    .stat-pill {
        display: inline-block;
        background: #1f2937;
        color: #38bdf8;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 13px;
        margin: 4px;
        border: 1px solid #374151;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Hero ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">📄 Document / Image Data Extractor</div>
        <div class="hero-subtitle">
            Upload a PDF or Image — extract Text, Tables, Images and get AI-powered analysis.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── File Upload ─────────────────────────────────────────────────────────
    uploaded_file = st.file_uploader(
        "Upload a PDF or Image",
        type=["pdf", "png", "jpg", "jpeg"]
    )

    if not uploaded_file:
        st.info("📂 Upload a PDF or image file to get started.")
        return

    file_bytes = uploaded_file.read()
    file_type  = uploaded_file.type
    file_name  = uploaded_file.name

    # ── IMAGE FILE ──────────────────────────────────────────────────────────
    if file_type.startswith("image/"):
        image = Image.open(BytesIO(file_bytes))
        st.image(image, caption="Uploaded Image", use_container_width=True)

        prompt = st.text_input(
            "Enter your instruction:",
            placeholder="e.g. Extract all text, Describe this image, List all data"
        )

        if st.button("🚀 Analyze Image") and prompt:
            with st.spinner("Analyzing image with AI..."):
                try:
                    output = call_vision_ai(prompt, file_bytes, mime_type=file_type)
                    st.markdown('<div class="extract-box">', unsafe_allow_html=True)
                    st.markdown("### 📝 Extracted Information")
                    st.write(output)
                    st.markdown('</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error: {e}")
        return

    # ── PDF FILE ────────────────────────────────────────────────────────────
    st.success(f"✅ PDF Loaded: **{file_name}**")

    # ── Tabs for each extraction type ───────────────────────────────────────
    tab1, tab2, tab4 = st.tabs([
        "📝 Text Extraction",
        "📊 Table Extraction",
        "🤖 AI Analysis"
    ])

    # ════════════════════════════════════════════════════════════════════════
    # TAB 1 — TEXT EXTRACTION
    # ════════════════════════════════════════════════════════════════════════
    with tab1:
        st.markdown("### 📝 Extract Text from PDF")
        st.caption("Extracts all text content from every page of the PDF.")

        if st.button("📥 Extract Text", key="btn_text"):
            with st.spinner("Extracting text..."):
                text = extract_pdf_text(file_bytes)

            if text:
                word_count = len(text.split())
                char_count = len(text)
                page_count = text.count("--- Page ")

                col1, col2, col3 = st.columns(3)
                col1.metric("📄 Pages", page_count)
                col2.metric("📝 Words", f"{word_count:,}")
                col3.metric("🔤 Characters", f"{char_count:,}")

                st.markdown("---")
                st.markdown("#### Extracted Text")
                st.text_area("", value=text, height=400, key="text_output")

                st.download_button(
                    label="⬇ Download as .txt",
                    data=text,
                    file_name=f"{file_name.replace('.pdf', '')}_text.txt",
                    mime="text/plain"
                )
            else:
                st.warning("⚠ Could not extract text. Make sure PyMuPDF is installed: `pip install pymupdf`")

    # ════════════════════════════════════════════════════════════════════════
    # TAB 2 — TABLE EXTRACTION
    # ════════════════════════════════════════════════════════════════════════
    with tab2:
        st.markdown("### 📊 Extract Tables from PDF")
        st.caption("Detects and extracts structured tables from every page.")

        if st.button("📥 Extract Tables", key="btn_tables"):
            with st.spinner("Scanning for tables..."):
                tables = extract_pdf_tables(file_bytes)

            if tables:
                st.success(f"✅ Found **{len(tables)}** table(s) in the PDF!")
                st.markdown("---")

                for t in tables:
                    st.markdown(f"#### Table {t['table_num']} — Page {t['page']}")
                    st.dataframe(t["df"], use_container_width=True)

                    csv_data = t["df"].to_csv(index=False)
                    st.download_button(
                        label=f"⬇ Download Table {t['table_num']} as CSV",
                        data=csv_data,
                        file_name=f"{file_name.replace('.pdf','')}_table_p{t['page']}_{t['table_num']}.csv",
                        mime="text/csv",
                        key=f"dl_table_{t['page']}_{t['table_num']}"
                    )
                    st.markdown("---")
            else:
                st.info("ℹ No tables detected in this PDF, or pdfplumber is not installed.\n\nInstall with: `pip install pdfplumber pandas`")

    # ════════════════════════════════════════════════════════════════════════
    # TAB 4 — AI ANALYSIS
    # ════════════════════════════════════════════════════════════════════════
    with tab4:
        st.markdown("### 🤖 AI-Powered PDF Analysis")
        st.caption("Extracts real text from PDF and sends it to AI for intelligent analysis.")

        analysis_type = st.selectbox(
            "Choose analysis type:",
            [
                "📋 Summarize the document",
                "🔑 Extract key points / highlights",
                "📊 Extract all data and numbers",
                "📜 Extract names, dates, places",
                "🧾 Extract invoice / financial data",
                "❓ Custom instruction"
            ]
        )

        prompt_map = {
            "📋 Summarize the document":         "Please provide a comprehensive summary of this document.",
            "🔑 Extract key points / highlights": "Extract and list all key points, highlights, and important information from this document.",
            "📊 Extract all data and numbers":    "Extract all numerical data, statistics, percentages, and figures mentioned in this document.",
            "📜 Extract names, dates, places":    "Extract all names of people, organizations, dates, and locations mentioned in this document.",
            "🧾 Extract invoice / financial data":"Extract all invoice details, amounts, taxes, totals, and financial information from this document.",
            "❓ Custom instruction":              "",
        }

        auto_prompt = prompt_map[analysis_type]

        if analysis_type == "❓ Custom instruction":
            user_prompt = st.text_input("Enter your custom instruction:", placeholder="e.g. What are the terms and conditions?")
        else:
            user_prompt = auto_prompt
            st.info(f"📌 Prompt: *{auto_prompt}*")

        ai_method = st.radio(
            "Analysis method:",
            ["📝 Text-based (fast, accurate)", "🖼 Vision-based (reads page as image)"],
            horizontal=True
        )

        if st.button("🚀 Run AI Analysis", key="btn_ai") and user_prompt:
            with st.spinner("Running AI analysis..."):
                try:
                    if "Vision-based" in ai_method:
                        # Render first page as image and send to vision AI
                        page_imgs = pdf_to_page_images(file_bytes)
                        if page_imgs:
                            # Analyze first 3 pages max
                            all_outputs = []
                            for pg in page_imgs[:3]:
                                page_output = call_vision_ai(
                                    f"{user_prompt}\n(This is page {pg['page']} of the PDF)",
                                    pg["bytes"],
                                    mime_type="image/png"
                                )
                                all_outputs.append(f"**Page {pg['page']}:**\n{page_output}")
                            output = "\n\n---\n\n".join(all_outputs)
                        else:
                            st.warning("⚠ Vision method needs PyMuPDF. Falling back to text method.")
                            extracted_text = extract_pdf_text(file_bytes) or "Could not extract text from PDF."
                            output = call_text_ai(user_prompt, extracted_text)
                    else:
                        # Extract real text and send to AI
                        extracted_text = extract_pdf_text(file_bytes)
                        if extracted_text:
                            output = call_text_ai(user_prompt, extracted_text)
                        else:
                            st.warning("⚠ Text extraction failed. Trying vision method on first page...")
                            page_imgs = pdf_to_page_images(file_bytes)
                            if page_imgs:
                                output = call_vision_ai(user_prompt, page_imgs[0]["bytes"])
                            else:
                                output = "Could not process this PDF. Please install: pip install pymupdf pdfplumber"

                    st.markdown('<div class="extract-box">', unsafe_allow_html=True)
                    st.markdown("### 📝 AI Analysis Result")
                    st.markdown(output)
                    st.markdown('</div>', unsafe_allow_html=True)

                    # Download result
                    st.download_button(
                        label="⬇ Download Analysis as .txt",
                        data=output,
                        file_name=f"{file_name.replace('.pdf','')}_analysis.txt",
                        mime="text/plain"
                    )

                except Exception as e:
                    st.error(f"Error during AI analysis: {e}")