"""
Central configuration for the AI Resume Analyser.
Loads environment variables and holds shared constants.

Works in two environments:
- Locally: reads from a .env file via python-dotenv.
- Deployed on Streamlit Community Cloud: reads from st.secrets, which is
  populated from the "Secrets" box in the app's dashboard settings (since
  .env is gitignored and never uploaded).
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Explicit path load (works reliably regardless of working directory)
load_dotenv(dotenv_path=Path(__file__).parent / ".env")


def _get_secret(key: str):
    """Check the environment (.env locally) first, then fall back to
    Streamlit's secrets store (used on Streamlit Community Cloud)."""
    value = os.getenv(key)
    if value:
        return value
    try:
        import streamlit as st
        return st.secrets.get(key)
    except Exception:
        return None


GROQ_API_KEY = _get_secret("GROQ_API_KEY")

# Groq model to use for all chains.
# llama-3.3-70b-versatile is deprecated -> use openai/gpt-oss-120b
GROQ_MODEL = "openai/gpt-oss-120b"

# Score threshold above which the resume is considered "good enough"
SCORE_THRESHOLD = 90

# Weighting between LLM-judged score and semantic keyword-match score
# final_score = (LLM_WEIGHT * llm_score) + (KEYWORD_WEIGHT * semantic_match_score)
LLM_WEIGHT = 0.4
KEYWORD_WEIGHT = 0.6

# Minimum cosine-similarity for a JD phrase to count as "matched" against
# the resume (analyzer.semantic_keyword_match). Lower = more lenient
# matching (catches looser paraphrases, but risks false positives).
SEMANTIC_MATCH_THRESHOLD = 0.5
