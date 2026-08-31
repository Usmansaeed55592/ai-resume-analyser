# 📄 AI Resume Analyser

AI-powered ATS (Applicant Tracking System) resume analyser and optimizer. Upload a resume, paste a job description, and get a realistic match score, a breakdown of matched vs. missing keywords, and an AI-rewritten version of the resume — without ever inventing skills or experience the candidate doesn't actually have.

Built with **Streamlit**, **LangChain**, **Groq**, and **sentence-transformers**.

---

## ✨ Features

- **ATS Match Scoring** — a blended score combining an LLM's holistic judgment with embedding-based semantic keyword matching (not just exact string matching, so "K8s" correctly matches "Kubernetes").
- **Keyword Breakdown** — clear matched vs. missing keyword lists, missing skills, weak sections, and resume strengths.
- **Anti-Fabrication Resume Rewriting** — regenerates the resume to use the job description's exact terminology wherever the candidate's real experience already supports it (honest wording improvements), but **never invents** a skill, project, employer, or metric that isn't genuinely there.
- **Human-in-the-loop notes** — an optional field where the candidate can add real skills/projects the AI should incorporate, keeping every rewrite grounded in truth.
- **Template-preserving DOCX export** — edits the original uploaded `.docx` in place, keeping its exact fonts, colors, and layout.
- **Styled PDF export** — renders a clean, ATS-friendly PDF layout (header, section headings, bullets) when the original upload was a PDF.
- **In-session scan history** — quickly compare scores across multiple job descriptions.

## 🧠 How It Works

1. **Extract** — resume text is pulled from the uploaded PDF/DOCX.
2. **Analyze** — the resume and job description are compared two ways: an LLM (via Groq) gives a holistic ATS judgment, while a local embedding model (`sentence-transformers`) does semantic keyword matching between the two texts.
3. **Report** — the two scores are blended into a final score, alongside matched/missing keywords, missing skills, and specific weak sections.
4. **Optimize** — if requested, the resume is rewritten to align wording with the job description's exact phrasing for skills that genuinely exist — gaps that aren't genuinely present are only ever *suggested*, never fabricated.
5. **Export** — download the optimized resume as a PDF or DOCX.

## 🛠 Tech Stack

| Layer | Tool |
|---|---|
| UI | [Streamlit](https://streamlit.io) |
| LLM orchestration | [LangChain](https://www.langchain.com/) + [Groq](https://groq.com/) |
| Semantic matching | [sentence-transformers](https://www.sbert.net/) (`all-MiniLM-L6-v2`) |
| PDF export | [fpdf2](https://pyfpdf.github.io/fpdf2/) |
| DOCX handling | [python-docx](https://python-docx.readthedocs.io/) |
| Structured LLM output | [Pydantic](https://docs.pydantic.dev/) |

## 📁 Project Structure

```
ai_resume_analyser/
├── app.py            # Streamlit UI and orchestration
├── analyzer.py        # LLM analysis chain + semantic keyword matching
├── generator.py       # Resume rewriting chains (full-text and paragraph-level)
├── exporter.py         # PDF/DOCX export and formatting
├── parser.py           # Resume text/paragraph extraction from PDF/DOCX
├── styles.py            # Custom CSS and UI component renderers
├── config.py             # Environment/config loading (local .env or Streamlit secrets)
├── requirements.txt
└── .streamlit/
    └── config.toml
```

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- A free [Groq API key](https://console.groq.com/keys)

### Installation

```bash
git clone https://github.com/<your-username>/ai-resume-analyser.git
cd ai-resume-analyser
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
```

### Run

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## ☁️ Deployment

This app is deployed on [Streamlit Community Cloud](https://share.streamlit.io). To deploy your own copy:

1. Push this repository to GitHub.
2. On Streamlit Community Cloud, create a new app pointing at `app.py`.
3. Under **Advanced settings → Secrets**, add:
   ```
   GROQ_API_KEY = "your_groq_api_key_here"
   ```

**Live demo:** _[add your deployed URL here]_

## 🗺 Roadmap

- [ ] Persistent analysis history (SQLite)
- [ ] In-app chat assistant for manual resume tweaks
- [ ] Multi-resume comparison

## 📝 License

This project is available under the MIT License — update this section if you'd prefer a different license.

## 🙏 Acknowledgments

Built using [Groq](https://groq.com/) for fast LLM inference and [sentence-transformers](https://www.sbert.net/) for semantic matching.
