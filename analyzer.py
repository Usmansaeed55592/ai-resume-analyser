"""
Core analysis chain: compares resume text against a job description
and produces a structured ATS-style report using Groq via LangChain.

Keyword/skill matching uses a HYBRID approach:
1. Literal substring match first (fast, exact, and correctly catches short
   acronyms like "OOP" or "CI" that embedding models handle poorly).
2. Falls back to embedding-based semantic similarity for paraphrases/
   synonyms (e.g. "K8s" vs "Kubernetes", "REST APIs" vs "API development")
   that literal matching would miss.
A stricter threshold is used for single-word phrases specifically, since
short phrases are noisier for embedding similarity and were previously
producing false-positive matches (e.g. "Pakistan", "Description" wrongly
matching resume text) as well as false negatives.
"""

import re
from typing import List

from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from sentence_transformers import SentenceTransformer, util

import config


# Loaded once and reused across calls - loading the model is the slow part,
# so we do it only the first time it's needed.
_embedder = None


def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder


class AnalysisResult(BaseModel):
    """Structured output schema for the analysis chain."""
    llm_score: int = Field(description="Overall ATS match score from 0 to 100 as judged by the LLM")
    keyword_match_score: int = Field(description="0-100 score for how well resume keywords match the JD")
    skills_match_score: int = Field(description="0-100 score for how well resume skills match the JD")
    experience_match_score: int = Field(description="0-100 score for how well resume experience matches the JD")
    matched_keywords: List[str] = Field(description="Important JD keywords that ARE present in the resume")
    missing_keywords: List[str] = Field(description="Important keywords from the JD missing in the resume")
    missing_skills: List[str] = Field(description="Skills required by the JD not evidenced in the resume")
    weak_sections: List[str] = Field(description="Resume sections that are weak or need improvement, with a short reason each")
    strengths: List[str] = Field(description="Aspects of the resume that already align well with the JD")
    job_match_summary: str = Field(description="A concise 2-3 sentence overall summary of how well the resume matches the job")


def get_llm():
    """Return a configured ChatGroq instance."""
    return ChatGroq(
        model=config.GROQ_MODEL,
        api_key=config.GROQ_API_KEY,
        temperature=0,
    )


def build_analysis_chain():
    """Build the structured-output analysis chain."""
    llm = get_llm()
    structured_llm = llm.with_structured_output(AnalysisResult)

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are an expert ATS (Applicant Tracking System) and technical recruiter. "
         "Compare the given resume against the given job description. "
         "Be strict and realistic about all scores - only give 90+ overall if the resume "
         "would genuinely pass an ATS filter and a recruiter's first-pass screen for this exact role."),
        ("human",
         "JOB DESCRIPTION:\n{job_description}\n\n"
         "RESUME:\n{resume_text}\n\n"
         "Analyze the match and return the structured result."),
    ])

    return prompt | structured_llm


# Generic job-posting boilerplate: section headers, leading verbs on bullet
# lines, and other structural/filler words. These show up capitalized only
# because they START a line or sentence in the JD - not because they're
# real skills/tools - so they must never be treated as keywords.
FILLER_WORDS = {
    "the", "and", "with", "for", "you", "your", "our", "will", "are", "this",
    "that", "have", "has", "job", "role", "team", "work", "years", "experience",
    "strong", "good", "ability", "abilities", "able", "skills", "skill",
    "knowledge", "using", "requirements", "requirement", "required", "require",
    "nice", "plus", "capable", "comfortable", "solid", "track", "record", "deep",
    "fluency", "familiarity", "exposure", "understanding", "understand",
    "grounding", "proven", "demonstrated", "hands-on", "working", "genuine",
    "genuinely", "title", "such", "as", "via", "of", "in", "on", "to", "a", "an",
    "or", "is", "be", "including", "etc", "into", "through", "between",
    "distinguishing", "structuring", "reasoning", "shipping", "persisting",
    "exposing", "constructing", "construct", "implementing", "about", "onto",
    "within", "across", "toward", "towards", "along",
    # section headers / structural words
    "responsibilities", "responsibility", "description", "overview", "summary",
    "location", "position", "level", "about", "qualifications", "qualification",
    # common bullet-leading verbs (capitalized only because they start a line)
    "develop", "set", "maintain", "collaborate", "apply", "solve", "write",
    "build", "create", "manage", "ensure", "perform", "participate", "join",
    "design", "deploy", "implement", "use", "support", "help", "assist",
    "contribute", "own", "drive", "lead", "define", "establish", "improve",
    "optimize", "monitor", "troubleshoot", "debug", "test", "review",
    "document", "communicate", "coordinate", "core", "based",
}


def _is_section_header(line: str) -> bool:
    """A short line ending in ':' (e.g. 'Required Skills:', 'Responsibilities:')
    is a section header, not a bullet with real content - skip it entirely."""
    stripped = line.strip(" -*\u2022\t")
    if not stripped:
        return False
    return stripped.endswith(":") and len(stripped.split()) <= 4


def _extract_jd_key_phrases(job_description: str, max_phrases: int = 40) -> List[str]:
    """
    Pull candidate keyword/skill phrases out of the JD. Two sources:
    (1) short comma/slash-separated items (works well when the JD lists
    skills like "Python, Django, REST APIs"), with generic filler words
    trimmed off both ends so a prose sentence split on commas doesn't
    leave junk fragments like "Ability to construct lightweight".
    (2) standalone tech-looking tokens (proper-noun-style or containing a
    digit/symbol, e.g. "Python", "MySQL", "CI/CD", "C++") - plain lowercase
    English words are excluded here so descriptive prose ("comfortable",
    "solid", "asynchronous") doesn't get treated as a skill.
    Section-header lines are skipped entirely so header words like
    "Required Skills:" or "Responsibilities:" never become keywords.
    Doesn't need to be perfect - the similarity scoring below (not exact
    string match) does the real work.
    """
    phrases = set()

    for line in job_description.splitlines():
        if _is_section_header(line):
            continue
        line = line.strip(" -*\u2022\t")
        if not line:
            continue
        for part in re.split(r"[,/]| and ", line):
            words = part.strip(" .()[]").split()
            # trim filler words off both ends of the fragment
            while words and words[0].lower().strip(",.():;[]") in FILLER_WORDS:
                words.pop(0)
            while words and words[-1].lower().strip(",.():;[]") in FILLER_WORDS:
                words.pop()
            if not (2 <= len(words) <= 6):
                continue
            # require at least one word that looks like a real content word
            # (capitalized/tech-looking, or a plain word of decent length that
            # isn't itself filler) so we don't keep phrases that are entirely
            # generic English
            if not any(
                (w[0].isupper() or any(ch.isdigit() for ch in w) or w.lower() not in FILLER_WORDS)
                and len(w.strip(",.():;[]")) > 3
                for w in words
            ):
                continue
            # strip stray unmatched brackets/parens left at the edges from
            # a comma-split cutting a JD phrase like "(AWS, Azure)" in half
            cleaned = " ".join(words).strip("()[] .")
            if cleaned:
                phrases.add(cleaned)

    # Standalone tokens: only proper-noun-like words or tokens containing a
    # digit/symbol (Python, MySQL, FastAPI, CI, CD, C++, Node.js) - excludes
    # plain lowercase English descriptive words entirely, AND excludes any
    # word that's simply the first word of its line (which is capitalized
    # only due to sentence position, not because it's a real proper noun).
    for line in job_description.splitlines():
        if _is_section_header(line):
            continue
        stripped_line = line.strip(" -*\u2022\t")
        if not stripped_line:
            continue
        line_tokens = re.findall(r"[A-Za-z][A-Za-z0-9+#.]{2,}", stripped_line)
        for i, raw_t in enumerate(line_tokens):
            t = raw_t.strip(".()[]")  # trailing punctuation isn't a real symbol
            if not t or t.lower() in FILLER_WORDS:
                continue
            if i == 0:
                # first token on the line - skip unless it's clearly technical
                # (contains a digit/symbol; plain capitalized words this
                # early are almost always sentence-starting verbs/headers)
                if not any(ch.isdigit() or ch in "+#." for ch in t):
                    continue
            looks_technical = t[0].isupper() or any(ch.isdigit() or ch in "+#." for ch in t)
            if looks_technical and len(t) > 2:
                phrases.add(t)

    # Drop single-word phrases that are just a piece of a longer phrase we
    # already extracted (e.g. "Web"/"Application" when "Python Web
    # Application Developer" is already in the set, or "REST" when "REST
    # APIs" already is) - otherwise the same concept gets counted as both
    # matched (via the long phrase) and missing (via the leftover word),
    # unfairly dragging the score down.
    multi_word = [p for p in phrases if len(p.split()) > 1]
    deduped = set()
    for p in phrases:
        if len(p.split()) == 1:
            covered = any(
                re.search(r"\b" + re.escape(p.lower()) + r"\b", mp.lower())
                for mp in multi_word
            )
            if covered:
                continue
        deduped.add(p)

    return list(deduped)[:max_phrases]


def _literal_match(phrase: str, resume_text_lower: str) -> bool:
    """Exact (case-insensitive, word-boundary) substring match. Checked
    before falling back to embeddings - this is what a real ATS keyword
    scanner does, and it correctly catches short acronyms (OOP, CI, CD)
    that sentence-embedding models handle unreliably at this length."""
    pattern = r"\b" + re.escape(phrase.lower()) + r"\b"
    return re.search(pattern, resume_text_lower) is not None


def semantic_keyword_match(resume_text: str, job_description: str, threshold: float = None) -> dict:
    """
    Hybrid matching: a JD phrase counts as matched if it's found as a
    literal substring in the resume (handles exact terms and short
    acronyms reliably), OR if any resume sentence is semantically close to
    it via embeddings (catches synonyms/paraphrases that literal matching
    misses). Single-word phrases use a stricter embedding threshold than
    multi-word phrases, since short phrases produce noisier similarity
    scores and were previously causing false-positive matches.
    """
    threshold = threshold if threshold is not None else getattr(config, "SEMANTIC_MATCH_THRESHOLD", 0.55)
    single_word_threshold = threshold + 0.12

    phrases = _extract_jd_key_phrases(job_description)
    if not phrases:
        return {"matched": [], "missing": [], "score": 0.0}

    resume_text_lower = resume_text.lower()
    resume_chunks = [c.strip() for c in re.split(r"[\n.]", resume_text) if len(c.strip()) > 3]
    if not resume_chunks:
        return {"matched": [], "missing": phrases, "score": 0.0}

    # First pass: literal matches, resolved without needing the embedder.
    matched, still_unresolved = [], []
    for phrase in phrases:
        if _literal_match(phrase, resume_text_lower):
            matched.append(phrase)
        else:
            still_unresolved.append(phrase)

    # Second pass: embedding similarity for whatever literal matching missed.
    if still_unresolved:
        model = get_embedder()
        phrase_embeddings = model.encode(still_unresolved, convert_to_tensor=True)
        chunk_embeddings = model.encode(resume_chunks, convert_to_tensor=True)
        similarity_matrix = util.cos_sim(phrase_embeddings, chunk_embeddings)

        missing = []
        for i, phrase in enumerate(still_unresolved):
            best_score = float(similarity_matrix[i].max())
            phrase_threshold = single_word_threshold if len(phrase.split()) == 1 else threshold
            if best_score >= phrase_threshold:
                matched.append(phrase)
            else:
                missing.append(phrase)
    else:
        missing = []

    score = round((len(matched) / len(phrases)) * 100, 2) if phrases else 0.0
    return {"matched": matched, "missing": missing, "score": score}


def compute_final_score(llm_score: int, semantic_score: float) -> int:
    """Blend the LLM score and the semantic keyword-match score into one final score."""
    final = (config.LLM_WEIGHT * llm_score) + (config.KEYWORD_WEIGHT * semantic_score)
    return round(final)


def analyze_resume(resume_text: str, job_description: str) -> dict:
    """
    Run the full analysis: LLM structured analysis + semantic keyword match,
    returns a dict ready to be used by the UI layer.
    """
    chain = build_analysis_chain()
    result: AnalysisResult = chain.invoke({
        "resume_text": resume_text,
        "job_description": job_description,
    })

    sem = semantic_keyword_match(resume_text, job_description)
    final_score = compute_final_score(result.llm_score, sem["score"])

    return {
        "final_score": final_score,
        "llm_score": result.llm_score,
        "semantic_match_score": sem["score"],
        "semantic_matched_keywords": sem["matched"],
        "semantic_missing_keywords": sem["missing"],
        "keyword_match_score": result.keyword_match_score,
        "skills_match_score": result.skills_match_score,
        "experience_match_score": result.experience_match_score,
        "matched_keywords": result.matched_keywords,
        "missing_keywords": result.missing_keywords,
        "missing_skills": result.missing_skills,
        "weak_sections": result.weak_sections,
        "strengths": result.strengths,
        "job_match_summary": result.job_match_summary,
    }