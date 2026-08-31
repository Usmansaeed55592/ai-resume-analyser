"""
AI Resume Analyser - Streamlit app entry point.
"""

import streamlit as st

import config
from parser import extract_resume_text, clean_text, extract_docx_paragraphs
from analyzer import analyze_resume
from generator import get_suggestions, regenerate_resume, regenerate_resume_paragraphs
from exporter import text_to_docx_bytes, text_to_pdf_bytes, edit_docx_paragraphs
from styles import (
    CUSTOM_CSS, render_score_ring, render_metric_card, render_pills,
    render_step_progress, render_history_item,
)

st.set_page_config(page_title="AI Resume Analyser", page_icon="📄", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def _jd_label(jd: str) -> str:
    """Short, readable label for a job description, used in the session
    history list (e.g. its title line, trimmed)."""
    first_line = jd.strip().splitlines()[0].strip() if jd and jd.strip() else "Job Description"
    if first_line.lower().startswith("job title:"):
        first_line = first_line.split(":", 1)[1].strip()
    return (first_line[:55] + "…") if len(first_line) > 55 else first_line


# ---------- Session state ----------
for key in [
    "analysis", "resume_text", "job_description", "generated_resume",
    "uploaded_file_ext", "original_file_bytes", "rewritten_paragraphs",
]:
    if key not in st.session_state:
        st.session_state[key] = None
if st.session_state.get("history") is None:
    st.session_state.history = []
if st.session_state.get("exported") is None:
    st.session_state.exported = False


# ---------- Navbar ----------
st.markdown("""
<div class="navbar">
    <div class="navbar-logo">📄 Resume Analyser</div>
    <div class="navbar-links">
        <a href="#home">Home</a><a href="#analyse-section">Analyse Resume</a><a href="#how-it-works">How It Works</a>
    </div>
    <div class="navbar-badge">AI Powered</div>
</div>
""", unsafe_allow_html=True)

# ---------- Hero ----------
st.markdown("""
<div class="hero" id="home">
    <div class="hero-badge">AI-Powered ATS Analysis</div>
    <h1>Optimize Your Resume for ATS</h1>
    <p>Upload your resume and compare it with any job description to discover your
    ATS match score, missing keywords, and improvement opportunities.</p>
</div>
""", unsafe_allow_html=True)

# ---------- Step progress ----------
current_step = 1
if st.session_state.analysis:
    current_step = 3
if st.session_state.generated_resume:
    current_step = 4
if st.session_state.exported:
    current_step = 5
st.markdown(f'<div id="how-it-works">{render_step_progress(current_step)}</div>', unsafe_allow_html=True)

# ---------- Upload + JD Card ----------
st.markdown('<div class="card" id="analyse-section">', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Upload Your Resume")
    uploaded_file = st.file_uploader(
        "PDF or DOCX • Max 200MB",
        type=["pdf", "docx"],
        label_visibility="visible",
    )
    if uploaded_file:
        size_kb = round(len(uploaded_file.getvalue()) / 1024, 1)
        st.caption(f"📎 {uploaded_file.name} • {size_kb} KB")

with col2:
    st.markdown("#### Job Description")
    job_description = st.text_area(
        "Paste the job description here...",
        height=180,
        label_visibility="collapsed",
        placeholder="Paste the job description here...",
    )
    st.caption(f"{len(job_description) if job_description else 0} characters")

analyze_clicked = st.button("🔍 Analyse Resume", type="primary", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ---------- Run analysis ----------
if analyze_clicked:
    if not config.GROQ_API_KEY:
        st.error("GROQ_API_KEY not found. Please set it in your .env file.")
    elif not uploaded_file:
        st.warning("Please upload a resume file.")
    elif not job_description or not job_description.strip():
        st.warning("Please paste the job description.")
    else:
        with st.spinner("Extracting resume text..."):
            raw_text = extract_resume_text(uploaded_file)
            resume_text = clean_text(raw_text)

        with st.spinner("Analyzing against job description..."):
            analysis = analyze_resume(resume_text, job_description)

        # Remember the original file's extension AND raw bytes so we can
        # (a) offer the download in the same format the user uploaded, and
        # (b) for DOCX, edit the original file in-place to preserve its template.
        st.session_state.uploaded_file_ext = uploaded_file.name.rsplit(".", 1)[-1].lower()
        st.session_state.original_file_bytes = uploaded_file.getvalue()

        st.session_state.resume_text = resume_text
        st.session_state.job_description = job_description
        st.session_state.analysis = analysis
        st.session_state.generated_resume = None
        st.session_state.rewritten_paragraphs = None
        st.session_state.exported = False

        st.session_state.history.insert(0, {
            "jd_label": _jd_label(job_description),
            "score": analysis["final_score"],
        })
        st.session_state.history = st.session_state.history[:8]

# ---------- Empty state ----------
if not st.session_state.analysis:
    st.markdown("""
    <div class="empty-state">
        <h4>Ready to analyse your resume?</h4>
        <p>Upload your resume and add a job description to get your ATS compatibility score.</p>
        <div>
            <span class="feature-mini">✓ ATS Compatibility Score</span>
            <span class="feature-mini">✓ Missing Keywords</span>
            <span class="feature-mini">✓ Actionable Improvements</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---------- Results dashboard ----------
if st.session_state.analysis:
    analysis = st.session_state.analysis
    score = analysis["final_score"]

    st.markdown("## Your ATS Analysis")

    # ---- Verdict: score seal + summary, merged into one card ----
    st.markdown('<div class="card">', unsafe_allow_html=True)
    v_col1, v_col2 = st.columns([1, 2.4])
    with v_col1:
        st.markdown(render_score_ring(score), unsafe_allow_html=True)
    with v_col2:
        st.markdown('<div class="verdict-summary">', unsafe_allow_html=True)
        st.markdown('<div class="eyebrow">Job Match Summary</div>', unsafe_allow_html=True)
        st.markdown(f"<p>{analysis['job_match_summary']}</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(render_metric_card("ATS Score", score), unsafe_allow_html=True)
    with m2:
        st.markdown(render_metric_card("Keyword Match", analysis["keyword_match_score"]), unsafe_allow_html=True)
    with m3:
        st.markdown(render_metric_card("Skills Match", analysis["skills_match_score"]), unsafe_allow_html=True)
    with m4:
        st.markdown(render_metric_card("Experience Match", analysis["experience_match_score"]), unsafe_allow_html=True)

    st.write("")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="eyebrow">✓ Matched Keywords</div>', unsafe_allow_html=True)
        st.markdown(render_pills(analysis["matched_keywords"], "good"), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col_b:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="eyebrow">⚠ Missing Keywords</div>', unsafe_allow_html=True)
        st.markdown(render_pills(analysis["missing_keywords"], "bad"), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="eyebrow">💡 Recommended Improvements</div>', unsafe_allow_html=True)
    for i, item in enumerate(analysis["missing_skills"] + analysis["weak_sections"], start=1):
        st.markdown(f"{i}. {item}")
    st.markdown('</div>', unsafe_allow_html=True)

    col_c, col_d = st.columns(2)
    with col_c:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="eyebrow">📄 Resume Strengths</div>', unsafe_allow_html=True)
        for item in analysis["strengths"]:
            st.markdown(f"- {item}")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_d:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="eyebrow">⚠ Resume Weaknesses</div>', unsafe_allow_html=True)
        for item in analysis["weak_sections"]:
            st.markdown(f"- {item}")
        st.markdown('</div>', unsafe_allow_html=True)

    # ---------- Improvement options ----------
    if score < config.SCORE_THRESHOLD:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Optimize Your Resume")
        st.write("Based on the gaps above, you can get quick suggestions or let AI rewrite your resume for this job.")

        st.markdown("**Anything real to add before we rewrite it?** (optional)")
        additional_notes = st.text_area(
            "e.g. a skill, tool, certification, or project you actually have that isn't on the resume yet. "
            "The AI will ONLY use what's already in your resume plus what you write here — it will not invent anything else.",
            key="additional_notes_input",
            height=90,
            placeholder="Leave blank if there's nothing to add.",
        )

        opt_col1, opt_col2 = st.columns(2)
        with opt_col1:
            if st.button("💡 Get Suggestions Only"):
                with st.spinner("Generating suggestions..."):
                    suggestions = get_suggestions(
                        st.session_state.resume_text,
                        st.session_state.job_description,
                        analysis,
                    )
                st.markdown(suggestions)

        with opt_col2:
            if st.button("✨ Generate Optimized Resume"):
                if st.session_state.uploaded_file_ext == "docx":
                    with st.spinner("Rewriting your resume (keeping your original template)..."):
                        original_paragraphs = extract_docx_paragraphs(st.session_state.original_file_bytes)
                        rewritten = regenerate_resume_paragraphs(
                            original_paragraphs,
                            st.session_state.job_description,
                            analysis,
                            additional_notes,
                        )
                    st.session_state.rewritten_paragraphs = rewritten
                    st.session_state.generated_resume = "\n\n".join(
                        item["text"] for item in sorted(rewritten, key=lambda x: x["index"])
                    )
                else:
                    with st.spinner("Rewriting your resume..."):
                        new_resume = regenerate_resume(
                            st.session_state.resume_text,
                            st.session_state.job_description,
                            analysis,
                            additional_notes,
                        )
                    st.session_state.rewritten_paragraphs = None
                    st.session_state.generated_resume = new_resume
        st.markdown('</div>', unsafe_allow_html=True)

    # ---------- Download section ----------
    if st.session_state.generated_resume:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Your ATS-Optimized Resume is Ready")
        st.text_area("Preview", st.session_state.generated_resume, height=350, label_visibility="collapsed")

        original_ext = st.session_state.uploaded_file_ext  # "pdf" or "docx"

        if original_ext == "docx" and st.session_state.rewritten_paragraphs:
            # Template-preserving path: edit the ORIGINAL docx in place,
            # so fonts/colors/bullets/spacing all stay exactly as uploaded.
            docx_bytes = edit_docx_paragraphs(
                st.session_state.original_file_bytes,
                st.session_state.rewritten_paragraphs,
            )
            if st.download_button(
                "⬇ Download DOCX (original template)",
                data=docx_bytes,
                file_name="improved_resume.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            ):
                st.session_state.exported = True
        elif original_ext == "docx":
            docx_bytes = text_to_docx_bytes(st.session_state.generated_resume)
            if st.download_button(
                "⬇ Download DOCX",
                data=docx_bytes,
                file_name="improved_resume.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            ):
                st.session_state.exported = True
        elif original_ext == "pdf":
            pdf_bytes = text_to_pdf_bytes(st.session_state.generated_resume)
            if st.download_button(
                "⬇ Download PDF",
                data=pdf_bytes,
                file_name="improved_resume.pdf",
                mime="application/pdf",
                use_container_width=True,
            ):
                st.session_state.exported = True
        else:
            # Fallback: offer both if the original extension wasn't captured
            docx_bytes = text_to_docx_bytes(st.session_state.generated_resume)
            pdf_bytes = text_to_pdf_bytes(st.session_state.generated_resume)
            dl_col1, dl_col2 = st.columns(2)
            with dl_col1:
                if st.download_button(
                    "⬇ Download DOCX",
                    data=docx_bytes,
                    file_name="improved_resume.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                ):
                    st.session_state.exported = True
            with dl_col2:
                if st.download_button(
                    "⬇ Download PDF",
                    data=pdf_bytes,
                    file_name="improved_resume.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                ):
                    st.session_state.exported = True
        st.markdown('</div>', unsafe_allow_html=True)

    # ---------- Session history ----------
    if len(st.session_state.history) > 1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="eyebrow">🕘 Previous Scans (this session)</div>', unsafe_allow_html=True)
        for item in st.session_state.history:
            st.markdown(render_history_item(item["jd_label"], item["score"]), unsafe_allow_html=True)
        st.caption("Cleared when you close or refresh this tab. Saved history across sessions is coming soon.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ---------- Debug breakdown (tucked away, not part of the main flow) ----------
    with st.expander("🔍 Detailed Score Breakdown (debug)"):
        st.write(f"**LLM holistic score:** {analysis.get('llm_score')}")
        st.write(f"**Semantic keyword-match score:** {analysis.get('semantic_match_score')}")
        st.write(f"**Final blended score:** {analysis.get('final_score')}")
        st.write("**Semantically matched keywords:**", analysis.get("semantic_matched_keywords", []))
        st.write("**Semantically missing keywords:**", analysis.get("semantic_missing_keywords", []))
        st.json(analysis)

# ---------- Footer ----------
st.markdown("""
<div class="app-footer">
    <b>AI Resume Analyser</b> — Build a resume that gets noticed.<br>
    AI-powered ATS resume analysis
</div>
""", unsafe_allow_html=True)