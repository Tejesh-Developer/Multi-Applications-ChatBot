import os
import re
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
import io

load_dotenv()

# ── Color Themes ──────────────────────────────────────────────────────────────
THEMES = {
    "🌊 Ocean Blue": {
        "bg_dark":    RGBColor(0x06, 0x5A, 0x82),
        "bg_light":   RGBColor(0xE8, 0xF4, 0xF8),
        "accent":     RGBColor(0x02, 0xC3, 0x9A),
        "title_text": RGBColor(0xFF, 0xFF, 0xFF),
        "body_text":  RGBColor(0x1E, 0x29, 0x3B),
        "card_bg":    RGBColor(0xFF, 0xFF, 0xFF),
        "bullet_dot": RGBColor(0x02, 0xC3, 0x9A),
    },
    "🌙 Midnight Executive": {
        "bg_dark":    RGBColor(0x1E, 0x27, 0x61),
        "bg_light":   RGBColor(0xF0, 0xF4, 0xFF),
        "accent":     RGBColor(0xCA, 0xDC, 0xFC),
        "title_text": RGBColor(0xFF, 0xFF, 0xFF),
        "body_text":  RGBColor(0x1E, 0x29, 0x3B),
        "card_bg":    RGBColor(0xFF, 0xFF, 0xFF),
        "bullet_dot": RGBColor(0x1E, 0x27, 0x61),
    },
    "🌿 Forest & Moss": {
        "bg_dark":    RGBColor(0x2C, 0x5F, 0x2D),
        "bg_light":   RGBColor(0xF0, 0xF7, 0xEE),
        "accent":     RGBColor(0x97, 0xBC, 0x62),
        "title_text": RGBColor(0xFF, 0xFF, 0xFF),
        "body_text":  RGBColor(0x1A, 0x2E, 0x1A),
        "card_bg":    RGBColor(0xFF, 0xFF, 0xFF),
        "bullet_dot": RGBColor(0x97, 0xBC, 0x62),
    },
    "🔥 Coral Energy": {
        "bg_dark":    RGBColor(0xF9, 0x61, 0x67),
        "bg_light":   RGBColor(0xFF, 0xF8, 0xF0),
        "accent":     RGBColor(0x2F, 0x3C, 0x7E),
        "title_text": RGBColor(0xFF, 0xFF, 0xFF),
        "body_text":  RGBColor(0x1A, 0x1A, 0x2E),
        "card_bg":    RGBColor(0xFF, 0xFF, 0xFF),
        "bullet_dot": RGBColor(0xF9, 0x61, 0x67),
    },
    "⚫ Charcoal Minimal": {
        "bg_dark":    RGBColor(0x36, 0x45, 0x4F),
        "bg_light":   RGBColor(0xF2, 0xF2, 0xF2),
        "accent":     RGBColor(0x21, 0x21, 0x21),
        "title_text": RGBColor(0xFF, 0xFF, 0xFF),
        "body_text":  RGBColor(0x2D, 0x2D, 0x2D),
        "card_bg":    RGBColor(0xFF, 0xFF, 0xFF),
        "bullet_dot": RGBColor(0x36, 0x45, 0x4F),
    },
    "🍒 Cherry Bold": {
        "bg_dark":    RGBColor(0x99, 0x00, 0x11),
        "bg_light":   RGBColor(0xFF, 0xF6, 0xF5),
        "accent":     RGBColor(0x2F, 0x3C, 0x7E),
        "title_text": RGBColor(0xFF, 0xFF, 0xFF),
        "body_text":  RGBColor(0x1A, 0x1A, 0x2E),
        "card_bg":    RGBColor(0xFF, 0xFF, 0xFF),
        "bullet_dot": RGBColor(0x99, 0x00, 0x11),
    },
}

# ── Slide Width/Height (Widescreen 16:9) ─────────────────────────────────────
SW = Inches(13.33)
SH = Inches(7.5)


# ── Helpers ───────────────────────────────────────────────────────────────────

def hex_to_rgb(h):
    h = h.lstrip("#")
    return RGBColor(int(h[0:2],16), int(h[2:4],16), int(h[4:6],16))

def add_rect(slide, x, y, w, h, fill_color, transparency=0):
    shape = slide.shapes.add_shape(1, x, y, w, h)  # MSO_SHAPE_TYPE.RECTANGLE=1
    shape.line.fill.background()
    shape.line.color.rgb = fill_color
    fill = shape.fill
    fill.solid()
    fill.fore_color.rgb = fill_color
    return shape

def add_textbox(slide, x, y, w, h, text, font_size, bold=False,
                color=RGBColor(0,0,0), align=PP_ALIGN.LEFT, italic=False, wrap=True):
    txb = slide.shapes.add_textbox(x, y, w, h)
    txb.word_wrap = wrap
    tf  = txb.text_frame
    tf.word_wrap = wrap
    tf.auto_size = None
    p   = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size    = Pt(font_size)
    run.font.bold    = bold
    run.font.italic  = italic
    run.font.color.rgb = color
    run.font.name    = "Calibri"
    return txb

def add_bullet_para(tf, text, font_size, color, dot_color, level=0):
    """Add one bullet point paragraph to existing text frame."""
    p = tf.add_paragraph()
    p.level = level
    p.alignment = PP_ALIGN.LEFT
    # bullet dot
    run_dot = p.add_run()
    run_dot.text = "▪  "
    run_dot.font.size  = Pt(font_size - 2)
    run_dot.font.color.rgb = dot_color
    run_dot.font.name  = "Calibri"
    # bullet text
    run_txt = p.add_run()
    run_txt.text = text
    run_txt.font.size  = Pt(font_size)
    run_txt.font.color.rgb = color
    run_txt.font.name  = "Calibri"
    return p


# ── Parse AI Output ───────────────────────────────────────────────────────────

def parse_ai_slides(ai_text):
    """Parse ### Slide Title + bullets from AI output."""
    slides = []
    blocks = re.split(r'###\s*', ai_text)
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        lines = [l.strip() for l in block.split('\n') if l.strip()]
        if not lines:
            continue
        title = re.sub(r'^(Slide\s*\d+[:\-]?\s*)', '', lines[0], flags=re.IGNORECASE).strip()
        bullets = []
        for line in lines[1:]:
            # Strip markdown bullets/numbers
            clean = re.sub(r'^[\-\*\•\d]+[\.\)]\s*', '', line).strip()
            clean = re.sub(r'^\*\*(.*)\*\*$', r'\1', clean)  # remove bold **
            if clean and len(clean) > 2:
                bullets.append(clean)
        if title:
            slides.append({"title": title, "bullets": bullets[:7]})  # max 7 bullets
    return slides


# ── Slide Builders ────────────────────────────────────────────────────────────

def build_cover_slide(prs, title, subtitle, theme):
    """Slide 1 — full dark cover with title + subtitle."""
    slide  = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    t      = theme

    # Full background
    add_rect(slide, 0, 0, SW, SH, t["bg_dark"])

    # Accent strip left
    add_rect(slide, 0, 0, Inches(0.18), SH, t["accent"])

    # Title
    add_textbox(
        slide, Inches(0.6), Inches(2.2), Inches(12.0), Inches(1.8),
        title, font_size=44, bold=True,
        color=t["title_text"], align=PP_ALIGN.LEFT
    )

    # Subtitle
    add_textbox(
        slide, Inches(0.6), Inches(4.1), Inches(11.0), Inches(0.8),
        subtitle, font_size=18, bold=False,
        color=t["accent"], align=PP_ALIGN.LEFT, italic=True
    )

    # Bottom bar
    add_rect(slide, 0, SH - Inches(0.18), SW, Inches(0.18), t["accent"])

    return slide


def build_content_slide(prs, slide_data, slide_num, theme):
    """Content slides — header bar + bullet cards."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    t     = theme
    title   = slide_data["title"]
    bullets = slide_data["bullets"]

    # Light background
    add_rect(slide, 0, 0, SW, SH, t["bg_light"])

    # Top header bar (dark)
    add_rect(slide, 0, 0, SW, Inches(1.35), t["bg_dark"])

    # Left accent strip
    add_rect(slide, 0, 0, Inches(0.18), SH, t["accent"])

    # Slide number circle (top-right)
    num_box = slide.shapes.add_shape(9, SW - Inches(1.05), Inches(0.18),
                                     Inches(0.72), Inches(0.72))
    num_box.fill.solid()
    num_box.fill.fore_color.rgb = t["accent"]
    num_box.line.fill.background()
    tf_num = num_box.text_frame
    tf_num.paragraphs[0].alignment = PP_ALIGN.CENTER
    r = tf_num.paragraphs[0].add_run()
    r.text = str(slide_num)
    r.font.size  = Pt(14)
    r.font.bold  = True
    r.font.color.rgb = t["bg_dark"]
    r.font.name  = "Calibri"

    # Title in header bar
    add_textbox(
        slide, Inches(0.45), Inches(0.18), Inches(11.8), Inches(1.0),
        title, font_size=28, bold=True,
        color=t["title_text"], align=PP_ALIGN.LEFT
    )

    # ── Bullets layout ────────────────────────────────────────────────────
    content_top  = Inches(1.55)
    content_h    = SH - content_top - Inches(0.3)
    content_left = Inches(0.45)
    content_w    = SW - Inches(0.65)

    if not bullets:
        add_textbox(slide, content_left, content_top, content_w, content_h,
                    "No content generated.", 16, color=t["body_text"])
        return slide

    n = len(bullets)

    if n <= 4:
        # Single column — big cards
        card_h   = min(Inches(1.1), (content_h - Inches(0.15)*(n-1)) / n)
        card_gap = Inches(0.18)

        for i, bullet in enumerate(bullets):
            cy = content_top + i * (card_h + card_gap)

            # Card background
            card = slide.shapes.add_shape(
                1, content_left, cy, content_w, card_h)
            card.fill.solid()
            card.fill.fore_color.rgb = t["card_bg"]
            card.line.color.rgb = t["accent"]
            card.line.width  = Pt(1.2)

            # Accent left bar inside card
            add_rect(slide, content_left, cy, Inches(0.08), card_h, t["accent"])

            # Bullet text inside card
            txb = slide.shapes.add_textbox(
                content_left + Inches(0.22), cy + Inches(0.12),
                content_w - Inches(0.35), card_h - Inches(0.22)
            )
            txb.word_wrap = True
            tf = txb.text_frame
            tf.word_wrap = True
            p  = tf.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT
            run = p.add_run()
            run.text = bullet
            run.font.size  = Pt(15)
            run.font.color.rgb = t["body_text"]
            run.font.name  = "Calibri"

    else:
        # Two columns for 5-7 bullets
        col_w   = (content_w - Inches(0.25)) / 2
        card_h  = min(Inches(0.98), (content_h - Inches(0.15)*3) / 4)
        card_gap= Inches(0.16)

        for i, bullet in enumerate(bullets):
            col   = i % 2
            row   = i // 2
            cx    = content_left + col * (col_w + Inches(0.25))
            cy    = content_top  + row * (card_h + card_gap)

            card = slide.shapes.add_shape(1, cx, cy, col_w, card_h)
            card.fill.solid()
            card.fill.fore_color.rgb = t["card_bg"]
            card.line.color.rgb = t["accent"]
            card.line.width = Pt(1.0)

            add_rect(slide, cx, cy, Inches(0.07), card_h, t["accent"])

            txb = slide.shapes.add_textbox(
                cx + Inches(0.18), cy + Inches(0.1),
                col_w - Inches(0.28), card_h - Inches(0.18)
            )
            txb.word_wrap = True
            tf = txb.text_frame
            tf.word_wrap = True
            p  = tf.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT
            run = p.add_run()
            run.text = bullet
            run.font.size  = Pt(13)
            run.font.color.rgb = t["body_text"]
            run.font.name  = "Calibri"

    return slide


def build_closing_slide(prs, topic, theme):
    """Last slide — Thank You / Conclusion."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    t     = theme

    add_rect(slide, 0, 0, SW, SH, t["bg_dark"])
    add_rect(slide, 0, 0, Inches(0.18), SH, t["accent"])
    add_rect(slide, 0, SH - Inches(0.18), SW, Inches(0.18), t["accent"])

    add_textbox(
        slide, Inches(0.6), Inches(2.6), Inches(12.0), Inches(1.2),
        "Thank You!", font_size=52, bold=True,
        color=t["title_text"], align=PP_ALIGN.LEFT
    )
    add_textbox(
        slide, Inches(0.6), Inches(3.9), Inches(11.0), Inches(0.7),
        topic, font_size=20, bold=False,
        color=t["accent"], align=PP_ALIGN.LEFT, italic=True
    )
    add_textbox(
        slide, Inches(0.6), Inches(4.7), Inches(11.0), Inches(0.5),
        "Generated by GenAI Suite", font_size=12, bold=False,
        color=RGBColor(0xAA, 0xBB, 0xCC), align=PP_ALIGN.LEFT
    )
    return slide


# ── Main PPT Builder ──────────────────────────────────────────────────────────

def generate_ppt(topic, ai_text, theme_name):
    theme  = THEMES[theme_name]
    slides = parse_ai_slides(ai_text)

    prs = Presentation()
    prs.slide_width  = SW
    prs.slide_height = SH

    # Cover
    build_cover_slide(prs, topic, "AI-Generated Presentation", theme)

    # Content slides
    for i, slide_data in enumerate(slides, start=1):
        build_content_slide(prs, slide_data, i, theme)

    # Closing
    build_closing_slide(prs, topic, theme)

    buf = io.BytesIO()
    prs.save(buf)
    buf.seek(0)
    return buf


# ── Streamlit UI ──────────────────────────────────────────────────────────────

def run():

    # Usage tracking
    try:
        import database
        database.log_usage(st.session_state.get("username", "unknown"), "PPT Slide Preparation")
    except:
        pass

    st.markdown("""
    <style>
    .hero-banner {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        padding: 40px; border-radius: 25px; margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    }
    .hero-title   { font-size: 42px; font-weight: 800; color: white; margin-bottom: 10px; }
    .hero-subtitle{ font-size: 18px; color: #cbd5e1; }
    .ppt-box {
        background-color: #111827; padding: 24px;
        border-radius: 15px; margin-top: 20px;
        border: 1px solid #1f2937;
    }
    .theme-preview {
        display: inline-block; width: 16px; height: 16px;
        border-radius: 50%; margin-right: 6px; vertical-align: middle;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">📊 PPT Slide Preparation</div>
        <div class="hero-subtitle">
            Generate professional PowerPoint presentations using AI — with proper layouts, themes & formatting.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Inputs ────────────────────────────────────────────────────────────────
    col1, col2 = st.columns([3, 2])

    with col1:
        topic = st.text_input(
            "📌 Presentation Topic",
            placeholder="e.g. Machine Learning in Healthcare, Climate Change, Python Programming"
        )

    with col2:
        theme_name = st.selectbox("🎨 Color Theme", list(THEMES.keys()))

    col3, col4 = st.columns([2, 3])
    with col3:
        slide_count = st.slider("📄 Number of Content Slides", 3, 10, 5)
    with col4:
        style_choice = st.radio(
            "📝 Content Style",
            ["Informative & Detailed", "Short & Crisp", "Academic / Research"],
            horizontal=True
        )

    # Theme preview
    th = THEMES[theme_name]
    r1, g1, b1 = th["bg_dark"]
    r2, g2, b2 = th["accent"]
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
        <span style="background:rgb({r1},{g1},{b1});width:22px;height:22px;border-radius:4px;display:inline-block;"></span>
        <span style="background:rgb({r2},{g2},{b2});width:22px;height:22px;border-radius:4px;display:inline-block;"></span>
        <span style="color:#94a3b8;font-size:13px;">Theme preview</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Generate Button ───────────────────────────────────────────────────────
    if st.button("🚀 Generate Presentation", use_container_width=True) and topic:

        style_map = {
            "Informative & Detailed": "detailed explanations with key facts and examples",
            "Short & Crisp":          "short, punchy bullet points — max 8 words each",
            "Academic / Research":    "academic tone with data, references and formal language",
        }

        prompt = f"""Create a {slide_count}-slide presentation on: {topic}

Style: {style_map[style_choice]}

IMPORTANT FORMAT RULES — follow exactly:
- Each slide MUST start with ### (three hash symbols)
- Slide title after ### should be clear and specific (no "Slide 1:" prefix)
- Each slide should have 4-6 bullet points
- Each bullet point on its own line, starting with - 
- No markdown bold (**text**), no sub-bullets
- Keep each bullet point to 1 sentence max

Example format:
### Introduction to the Topic
- First key point about this topic
- Second important concept to understand
- Third relevant fact or statistic
- Fourth supporting idea

### Main Concept One
- Explanation of this concept
- Why it matters in context
- Real world application
- Key takeaway

Now create {slide_count} slides for: {topic}"""

        with st.spinner("🤖 AI is generating your presentation content..."):
            try:
                client = Groq(api_key=os.getenv("GROQ_API_KEY"))
                resp   = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    max_tokens=2048,
                )
                ai_text = resp.choices[0].message.content
            except Exception as e:
                st.error(f"AI Error: {e}")
                return

        with st.spinner("🎨 Building professional slides..."):
            try:
                ppt_buf = generate_ppt(topic, ai_text, theme_name)
            except Exception as e:
                st.error(f"PPT Build Error: {e}")
                st.code(ai_text)
                return

        # ── Preview parsed slides ──────────────────────────────────────────
        parsed = parse_ai_slides(ai_text)

        st.markdown('<div class="ppt-box">', unsafe_allow_html=True)
        st.success(f"✅ Presentation ready! {len(parsed)} content slides + Cover + Thank You = {len(parsed)+2} total slides")

        # Slide preview cards
        st.markdown("#### 📋 Slide Preview")
        for i, s in enumerate(parsed, 1):
            with st.expander(f"Slide {i}: {s['title']}"):
                for b in s["bullets"]:
                    st.markdown(f"▪ {b}")

        st.markdown("---")
        st.download_button(
            label="⬇ Download PowerPoint (.pptx)",
            data=ppt_buf,
            file_name=f"{topic[:40].replace(' ','_')}_presentation.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            use_container_width=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

    elif not topic and st.session_state.get("_ppt_clicked"):
        st.warning("Please enter a presentation topic first.")