# AI Resume Analyser

Upload a resume (PDF/DOCX) + paste a job description → get an ATS match score,
missing keywords/skills, and either quick suggestions or a fully regenerated,
downloadable resume.

## Project Structure

```
ai_resume_analyser/
├── app.py            # Streamlit UI (entry point)
├── config.py         # Env vars + model/scoring config
├── parser.py         # PDF/DOCX text extraction
├── analyzer.py        # LangChain + Groq analysis chain, scoring
├── generator.py       # Suggestions + full resume regeneration chains
├── exporter.py         # Convert regenerated resume text -> DOCX/PDF
├── styles.py          # Custom CSS for the UI
├── requirements.txt
└── .env.example
```

## Setup

1. Create a virtual environment and activate it.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add your Groq API key:
   ```
   GROQ_API_KEY=your_key_here
   ```
4. Run the app:
   ```
   streamlit run app.py
   ```

## How it works

1. `parser.py` extracts raw text from the uploaded resume.
2. `analyzer.py` sends the resume text + job description to Groq via LangChain,
   gets back a structured score, missing keywords/skills, weak sections, and
   strengths. This is blended with a simple keyword-overlap metric for a more
   grounded final score.
3. If the score is below the threshold (default 90), the user can choose:
   - **Suggestions only** - a bullet list of specific edits to make.
   - **Full regenerate** - `generator.py` rewrites the resume, and
     `exporter.py` converts it into a downloadable DOCX or PDF.

## Next steps / TODO

- Add streaming output for the analysis step (like the agentic chatbot project).
- Improve DOCX/PDF export formatting (better section detection).
- Add a history/session sidebar if needed.
- Deploy to Streamlit Community Cloud.
