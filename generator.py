"""
Handles the three 'improvement' modes:
 1. Suggestions-only: short actionable bullet list.
 2. Full regenerate (plain text): a rewritten ATS-optimized resume, ready for export.
 3. Paragraph regenerate (DOCX template-preserving): rewrites text per-paragraph,
    keeping the same paragraph indices so it can be written back into the
    original DOCX without disturbing its formatting.
"""

import json

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from analyzer import get_llm


def build_suggestions_chain():
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a resume coach. Based on the analysis provided, write a short, "
         "actionable list of concrete edits the candidate should make. "
         "Be specific (mention exact keywords/phrases to add and where)."),
        ("human",
         "JOB DESCRIPTION:\n{job_description}\n\n"
         "CURRENT RESUME:\n{resume_text}\n\n"
         "MISSING KEYWORDS: {missing_keywords}\n"
         "MISSING SKILLS: {missing_skills}\n"
         "WEAK SECTIONS: {weak_sections}\n\n"
         "Write the suggestions as a markdown bullet list."),
    ])
    return prompt | llm | StrOutputParser()


def build_regeneration_chain():
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are an expert resume writer specializing in ATS optimization. "
         "Rewrite the candidate's resume so it naturally incorporates the missing "
         "keywords and skills ONLY WHERE the candidate's own resume or their ADDITIONAL "
         "NOTES actually support it, and strengthens the weak sections through better "
         "wording - not by inventing new content. Keep the same overall structure "
         "(Summary, Experience, Skills, Education, etc.) but improve the wording and "
         "align terminology with the job description.\n\n"
         "TITLE/HEADLINE RULE: the resume's professional title/headline line (the line "
         "directly under the candidate's name, e.g. 'Python Developer') MUST be changed to "
         "match the job description's title (e.g. 'Backend Software Engineer') whenever the "
         "job description's role genuinely matches the candidate's real skillset - which it "
         "does whenever the required skills significantly overlap with the resume, even if the "
         "job title uses different words (e.g. Python + Flask + FastAPI + REST APIs + OOP IS "
         "backend engineering work, just described with different terminology than the resume "
         "uses). This is a required step, not optional - do not leave the old title in place "
         "when the job title differs from it and the role is a genuine match. Only keep the "
         "original title if the job description describes a genuinely different specialization "
         "the resume doesn't support (e.g. do not relabel a backend developer as a 'Machine "
         "Learning Engineer' or 'Frontend Developer').\n\n"
         "NO KEYWORD STUFFING: when you rewrite a term to match the job description's exact "
         "wording, REPLACE the resume's own phrase with the JD's phrase - do not keep both by "
         "appending the JD phrase in parentheses after the original term. Doing this for every "
         "skill (e.g. 'Python (deep fluency)', 'MySQL (relational database management system)', "
         "'OOP (class-based software design principles, encapsulation-driven architecture)') "
         "makes the resume unreadable and looks like spam to a human recruiter, even though the "
         "candidate's underlying experience is genuine. In a skills list, the exact JD term IS "
         "the entry - do not add a parenthetical gloss after it. In prose (e.g. the professional "
         "summary), you may use a JD phrase as a natural appositive ONCE per concept at most "
         "(e.g. 'Flask, a lightweight Python web framework') - never repeat this pattern for "
         "every single skill in the same paragraph or list.\n\n"
         "EXACT TERMINOLOGY RULE (this is how you genuinely raise the ATS keyword-match "
         "score without fabricating anything): for every skill, tool, or concept that "
         "ALREADY exists in the candidate's resume - even if worded differently there - "
         "rewrite it using the SAME exact word/phrase the job description uses. "
         "Example: if the resume says 'built APIs' and the job description says "
         "'RESTful API development', change the resume wording to 'RESTful API "
         "development' since the candidate genuinely has that experience, just worded "
         "differently. Do this for every ALREADY-MATCHED keyword listed below - this is "
         "rewording truthful content, not fabrication, and it is the single most "
         "effective thing you can do here.\n\n"
         "MISSING KEYWORDS RULE: the MISSING KEYWORDS list below uses the EXACT phrase "
         "wording that the ATS scoring system checks for. If the candidate's ADDITIONAL "
         "NOTES state they genuinely have one of these missing keywords/skills, add it "
         "to the resume using that SAME exact wording (not a paraphrase or synonym of "
         "it) so it is correctly recognized as a match. Do not reword or generalize a "
         "confirmed missing keyword when adding it - use it verbatim.\n\n"
         "STRICT GROUNDING RULE: Do not invent, assume, or add any project, employer, "
         "job title, skill, tool, certification, metric, number, or achievement that is "
         "not explicitly present in the CURRENT RESUME or the ADDITIONAL NOTES below. "
         "If a missing keyword/skill is not something the candidate has actually done, "
         "do NOT add it to the resume - only genuinely rephrase and better surface what "
         "is already there. Never fabricate quantified results (e.g. 'improved X by 40%') "
         "unless that number already exists in the source material.\n\n"
         "PLAIN TEXT ONLY: Do not use any Markdown syntax anywhere in the output - no "
         "'**bold**', no '## headers', no '| tables |', no '---' rules, no numbered/lettered "
         "list markers. Section header lines must be plain ALL CAPS text on their own line "
         "(e.g. PROFESSIONAL SUMMARY). Bullet lines must start with a plain '- '. "
         "Return only the final rewritten resume as plain text."),
        ("human",
         "JOB DESCRIPTION:\n{job_description}\n\n"
         "CURRENT RESUME:\n{resume_text}\n\n"
         "ADDITIONAL NOTES FROM CANDIDATE (only use these facts if provided; do not "
         "invent anything beyond them): {additional_notes}\n\n"
         "ALREADY-MATCHED KEYWORDS (genuinely present - reword to the JD's exact "
         "phrasing wherever it appears in the resume): {semantic_matched_keywords}\n"
         "MISSING KEYWORDS (exact phrasing the ATS scorer checks for): {missing_keywords}\n"
         "MISSING SKILLS: {missing_skills}\n"
         "WEAK SECTIONS: {weak_sections}\n\n"
         "Return only the final rewritten resume text, plainly formatted with clear section headers."),
    ])
    return prompt | llm | StrOutputParser()


def build_paragraph_regeneration_chain():
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are an expert resume writer specializing in ATS optimization. "
         "You will be given the resume as a JSON array of paragraphs, each with an "
         "'index' and its original 'text'. Rewrite ONLY the 'text' of each paragraph "
         "to naturally incorporate the missing keywords/skills ONLY WHERE the original "
         "text or the ADDITIONAL NOTES actually support it, and strengthen weak "
         "sections through better wording - not by inventing new content.\n\n"
         "EXACT TERMINOLOGY RULE: for every skill/tool/concept that ALREADY exists in a "
         "paragraph's original text - even if worded differently there - rewrite that "
         "paragraph using the SAME exact word/phrase the job description uses for it. "
         "This is rewording truthful content, not fabrication, and is the most "
         "effective legitimate way to raise the ATS keyword-match score.\n\n"
         "NO KEYWORD STUFFING: REPLACE the paragraph's own phrase with the JD's phrase - do "
         "not keep both by appending the JD phrase in parentheses after the original term "
         "(e.g. do not write 'Python (deep fluency)' or 'MySQL (relational database "
         "management system)'). Doing this for every skill makes the resume look like spam "
         "to a human recruiter. In a skills list, the exact JD term simply IS the entry.\n\n"
         "MISSING KEYWORDS RULE: the MISSING KEYWORDS list below uses the EXACT phrase "
         "wording that the ATS scoring system checks for. If the ADDITIONAL NOTES confirm "
         "the candidate genuinely has one of these missing keywords/skills, add it into the "
         "most relevant paragraph (e.g. a skills-list paragraph) using that SAME exact "
         "wording - not a paraphrase or synonym - so it is correctly recognized as a match. "
         "If no existing paragraph is a natural fit (e.g. there is no skills-list paragraph "
         "at all), append it as a new short clause to the paragraph that most sensibly can "
         "hold it rather than skipping it entirely, while still not creating a brand-new "
         "paragraph.\n\n"
         "TITLE/HEADLINE RULE: if one of the paragraphs is the candidate's professional "
         "title/headline (the short line under their name, e.g. 'Python Developer'), change "
         "it to match the job description's title whenever the job's required skills "
         "genuinely overlap with the resume - even if the job title uses different words. "
         "Only keep the original title if the job description is a genuinely different "
         "specialization the resume doesn't support.\n\n"
         "STRICT GROUNDING RULE: Do not invent, assume, or add any project, employer, "
         "job title, skill, tool, certification, metric, number, or achievement that is "
         "not explicitly present in that paragraph's original text or the ADDITIONAL "
         "NOTES. Never fabricate quantified results unless that number already exists "
         "in the source material.\n\n"
         "PLAIN TEXT ONLY: Do not use any Markdown syntax in any paragraph's text - no "
         "'**bold**', no '## headers', no '| tables |', no '---' rules.\n\n"
         "Do NOT merge, split, reorder, add, or remove paragraphs - the output must "
         "have exactly the same number of items with exactly the same 'index' values, "
         "in the same order. Return ONLY a raw JSON array, no markdown, no code fences, "
         "no commentary - JSON only."),
        ("human",
         "JOB DESCRIPTION:\n{job_description}\n\n"
         "RESUME PARAGRAPHS (JSON):\n{paragraphs_json}\n\n"
         "ADDITIONAL NOTES FROM CANDIDATE (only use these facts if provided; do not "
         "invent anything beyond them): {additional_notes}\n\n"
         "ALREADY-MATCHED KEYWORDS (genuinely present - reword to the JD's exact "
         "phrasing wherever it appears in a paragraph): {semantic_matched_keywords}\n"
         "MISSING KEYWORDS (exact phrasing the ATS scorer checks for): {missing_keywords}\n"
         "MISSING SKILLS: {missing_skills}\n"
         "WEAK SECTIONS: {weak_sections}\n\n"
         "Return the JSON array now."),
    ])
    return prompt | llm | StrOutputParser()


def get_suggestions(resume_text: str, job_description: str, analysis: dict) -> str:
    chain = build_suggestions_chain()
    return chain.invoke({
        "resume_text": resume_text,
        "job_description": job_description,
        "missing_keywords": ", ".join(analysis.get("semantic_missing_keywords") or analysis.get("missing_keywords", [])),
        "missing_skills": ", ".join(analysis.get("missing_skills", [])),
        "weak_sections": ", ".join(analysis.get("weak_sections", [])),
    })


def regenerate_resume(resume_text: str, job_description: str, analysis: dict, additional_notes: str = "") -> str:
    chain = build_regeneration_chain()
    return chain.invoke({
        "resume_text": resume_text,
        "job_description": job_description,
        "additional_notes": additional_notes.strip() if additional_notes else "(none provided)",
        "semantic_matched_keywords": ", ".join(analysis.get("semantic_matched_keywords") or analysis.get("matched_keywords", [])),
        # Use the SAME missing-keyword list the scorer checks against
        # (semantic_missing_keywords), not the LLM's own separately-worded
        # missing_keywords field - otherwise the model can add a genuine,
        # correctly-worded skill that still doesn't match what the scorer
        # is looking for, and the score won't move even though the fix was real.
        "missing_keywords": ", ".join(analysis.get("semantic_missing_keywords") or analysis.get("missing_keywords", [])),
        "missing_skills": ", ".join(analysis.get("missing_skills", [])),
        "weak_sections": ", ".join(analysis.get("weak_sections", [])),
    })


def _parse_json_array(raw: str) -> list:
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("[")
        end = cleaned.rfind("]")
        if start != -1 and end != -1:
            return json.loads(cleaned[start:end + 1])
        raise ValueError("Could not parse AI response as a JSON paragraph array.")


def regenerate_resume_paragraphs(paragraphs: list, job_description: str, analysis: dict, additional_notes: str = "") -> list:
    """
    paragraphs: list of {"index": int, "text": str} (from parser.extract_docx_paragraphs)
    Returns: list of {"index": int, "text": str} with rewritten text,
             same indices and order as the input.
    """
    chain = build_paragraph_regeneration_chain()
    raw = chain.invoke({
        "paragraphs_json": json.dumps(paragraphs, ensure_ascii=False),
        "job_description": job_description,
        "additional_notes": additional_notes.strip() if additional_notes else "(none provided)",
        "semantic_matched_keywords": ", ".join(analysis.get("semantic_matched_keywords") or analysis.get("matched_keywords", [])),
        # Same fix as regenerate_resume(): align with what the scorer actually checks.
        "missing_keywords": ", ".join(analysis.get("semantic_missing_keywords") or analysis.get("missing_keywords", [])),
        "missing_skills": ", ".join(analysis.get("missing_skills", [])),
        "weak_sections": ", ".join(analysis.get("weak_sections", [])),
    })

    result = _parse_json_array(raw)

    # Safety net: if the model dropped/reordered items, fall back to
    # matching by index and keep the original text for anything missing.
    by_index = {item.get("index"): item.get("text", "") for item in result if "index" in item}
    fixed = []
    for original in paragraphs:
        idx = original["index"]
        fixed.append({"index": idx, "text": by_index.get(idx, original["text"])})
    return fixed