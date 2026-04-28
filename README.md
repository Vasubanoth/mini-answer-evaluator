# 📝 Mini Answer Evaluator

A rubric-based AI answer evaluation system built with **Streamlit** and **Groq (LLaMA 3.3 70B)**.  
Evaluates student answers against subject-specific rubrics — similar to what's done at Evalvia.

---

## Live Demo

> The web app is Live at : https://mini-answer-evaluator-nwfcfmdwszozzal4sxke8q.streamlit.app/

---

## Approach

### 1. Rubric Retrieval (Keyword Matching)
When a question is submitted, the system scans it for subject-specific keywords using a simple but effective frequency-based matching algorithm.

- Each subject (Physics, Math, English, Chemistry, Biology, History) has a curated list of keywords.
- The subject with the **highest keyword hit count** wins.
- If no subject scores above zero, a **generic fallback rubric** is used automatically.

No embeddings or vector databases are needed — this keeps the system lightweight and fast.

### 2. LLM-Based Evaluation
The retrieved rubric, question, and student answer are passed to **Groq's LLaMA 3.3 70B** via a structured prompt.

The model is instructed to:
- Evaluate strictly against each rubric criterion
- Return a **pure JSON response** (no markdown, no preamble)
- Justify every mark awarded or deducted

### 3. Structured Output
The model always returns:

```json
{
  "marks_awarded": 3,
  "max_marks": 5,
  "feedback": "Definition is correct but formula is missing.",
  "justification": "[1] ✅ Definition present. [2] ❌ F=ma not stated. [3] ❌ No derivation."
}
```

---

## Project Structure

```
├── app.py            # entire application (single file)
├── requirements.txt  # dependencies
└── README.md
```

---

## Setup & Run Locally

### 1. Clone the repo
```bash
git clone https://github.com/your-username/mini-answer-evaluator.git
cd mini-answer-evaluator
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your Groq API key
Create a file at `.streamlit/secrets.toml`:
```toml
GROQ_API_KEY = "gsk_your_key_here"
```
Get a free key at [console.groq.com](https://console.groq.com).

### 4. Run the app
```bash
streamlit run app.py
```

---

## Deploy on Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Select your repo and set `app.py` as the main file
4. Go to **Settings → Secrets** and add:
```toml
GROQ_API_KEY = "gsk_your_key_here"
```
5. Click **Deploy**

---

## Rubrics Included

| Subject | Class | Criteria |
|---|---|---|
| Physics | 12 | Definition, Formula, Derivation, Units, Numerical Accuracy |
| Mathematics | 12 | Method, Intermediate Steps, Formula Application, Final Answer |
| English | 10 | Theme/Main Idea, Key Points, Clarity, Grammar & Language |
| Chemistry | 12 | Definition, Balanced Equation, Mechanism, Conditions, Example |
| Biology | 12 | Definition, Process Explanation, Diagram, Real-world Example |
| History / SST | 10 | Facts & Dates, Cause & Effect, Key Figures, Significance |
| **Fallback** | Any | Relevance, Coverage, Clarity, Logical Structure, Language |

---

## 🔍 Prompt Used

```
You are a strict but fair academic evaluator.

QUESTION:
{question}

STUDENT ANSWER:
{student_answer}

RUBRIC (use this to award marks):
{rubric}

Evaluate the student's answer strictly against the rubric above.
Return ONLY a valid JSON object — no markdown, no explanation outside JSON.

{
  "marks_awarded": <integer>,
  "max_marks": <integer from rubric>,
  "feedback": "<concise feedback pointing to what was good and what was missing>",
  "justification": "<criterion-by-criterion justification referencing rubric points>"
}
```

> When the **Compare Mode** bonus is active, the same question is evaluated a second time without the rubric, using only general academic quality criteria (correctness, coverage, clarity, language).

---

## 🔧 Improvements I Would Make

- **Semantic rubric retrieval** using embeddings (e.g. `sentence-transformers`) for better subject detection on ambiguous questions
- **Custom rubric upload** — let teachers paste their own rubric per question
- **Multi-question batch evaluation** — upload a CSV of Q&A pairs
- **Confidence score** — ask the model to rate how confident it is in the evaluation
- **Answer history** — store past evaluations in session state for review
- **Marks breakdown UI** — show per-criterion scores visually, not just total
- **Multilingual support** — evaluate answers in Hindi or other regional languages

---

## 🛠 Tech Stack

| Layer | Tool |
|---|---|
| UI | Streamlit |
| LLM | LLaMA 3.3 70B via Groq API |
| API Client | OpenAI Python SDK (OpenAI-compatible) |
| Rubric Retrieval | Keyword frequency matching |
| Styling | Custom CSS (dark theme, Sora + JetBrains Mono) |

---
