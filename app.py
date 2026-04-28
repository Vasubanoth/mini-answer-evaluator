import streamlit as st
import json
import re
from openai import OpenAI

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Mini Answer Evaluator",
    page_icon="📝",
    layout="centered",
)

# ─────────────────────────────────────────────
#  CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Sora', sans-serif;
}

.stApp {
    background: #0e1117;
    color: #e8eaf0;
}

h1, h2, h3 {
    font-family: 'Sora', sans-serif;
    font-weight: 700;
}

.hero-title {
    font-size: 2.4rem;
    font-weight: 700;
    background: linear-gradient(135deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.2rem;
}

.hero-sub {
    color: #6b7280;
    font-size: 0.95rem;
    margin-bottom: 2rem;
}

.rubric-card {
    background: #1a1f2e;
    border: 1px solid #2d3748;
    border-left: 3px solid #a78bfa;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    color: #cbd5e1;
    white-space: pre-wrap;
    margin-bottom: 1rem;
}

.result-card {
    background: #1a1f2e;
    border: 1px solid #2d3748;
    border-radius: 10px;
    padding: 1.4rem;
    margin-top: 1rem;
}

.score-big {
    font-size: 3rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
}

.score-green  { color: #34d399; }
.score-yellow { color: #fbbf24; }
.score-red    { color: #f87171; }

.label-tag {
    display: inline-block;
    background: #2d3748;
    color: #a78bfa;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 2px 10px;
    border-radius: 20px;
    margin-bottom: 0.4rem;
}

.feedback-box {
    background: #111827;
    border-radius: 6px;
    padding: 0.9rem 1rem;
    margin-top: 0.5rem;
    color: #d1d5db;
    font-size: 0.92rem;
    line-height: 1.6;
}

.compare-col {
    background: #1a1f2e;
    border: 1px solid #2d3748;
    border-radius: 8px;
    padding: 1rem;
}

.divider {
    height: 1px;
    background: linear-gradient(to right, transparent, #2d3748, transparent);
    margin: 1.5rem 0;
}

section[data-testid="stSidebar"] {
    background: #111827;
    border-right: 1px solid #1f2937;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  RUBRIC DEFINITIONS
# ─────────────────────────────────────────────
RUBRICS = {
    "physics": {
        "keywords": ["force", "velocity", "acceleration", "mass", "energy", "momentum",
                     "newton", "gravity", "wave", "current", "voltage", "resistance",
                     "ohm", "joule", "work", "power", "light", "optics", "lens",
                     "magnetic", "electric", "charge", "motion", "circuit", "inertia",
                     "pressure", "thermodynamics", "heat", "temperature"],
        "rubric": """PHYSICS RUBRIC (Class 12)
─────────────────────────────
[1] Correct Definition / Concept Statement      → 1 mark
[2] Relevant Formula(s) stated correctly        → 1 mark
[3] Derivation / Steps (if applicable)          → 1 mark
[4] Correct Units and Dimensional Analysis      → 1 mark
[5] Numerical Accuracy / Final Answer           → 1 mark
─────────────────────────────
Total: 5 marks
Note: Deduct marks for wrong units, missing formula, or incomplete derivation."""
    },
    "mathematics": {
        "keywords": ["equation", "differentiate", "integrate", "matrix", "determinant",
                     "vector", "limit", "function", "graph", "solve", "theorem",
                     "proof", "angle", "triangle", "circle", "polynomial", "roots",
                     "probability", "permutation", "combination", "sequence", "series",
                     "coordinate", "slope", "tangent", "derivative", "calculus"],
        "rubric": """MATHEMATICS RUBRIC (Class 12)
─────────────────────────────
[1] Correct Setup / Method chosen               → 1 mark
[2] Key Intermediate Steps shown clearly        → 2 marks
[3] Correct Application of Formula/Theorem      → 1 mark
[4] Final Answer (correct value + simplification) → 1 mark
─────────────────────────────
Total: 5 marks
Note: Method marks awarded even if final answer is wrong but steps are correct."""
    },
    "english": {
        "keywords": ["poem", "poet", "character", "theme", "essay", "paragraph",
                     "author", "story", "narrator", "metaphor", "simile", "tone",
                     "prose", "figure of speech", "summary", "comprehension",
                     "passage", "explain", "describe", "language", "meaning",
                     "symbolic", "alliteration", "imagery", "novel", "chapter"],
        "rubric": """ENGLISH RUBRIC (Class 10)
─────────────────────────────
[1] Accurate identification of theme / main idea  → 1 mark
[2] Coverage of key points / evidence from text   → 2 marks
[3] Clarity and coherence of explanation          → 1 mark
[4] Grammar, vocabulary, and language quality     → 1 mark
─────────────────────────────
Total: 5 marks
Note: Penalise severely off-topic or irrelevant content."""
    },
    "chemistry": {
        "keywords": ["element", "compound", "reaction", "bond", "molecule", "atom",
                     "acid", "base", "oxidation", "reduction", "valence", "periodic",
                     "organic", "inorganic", "catalyst", "electrolysis", "solution",
                     "concentration", "mole", "ion", "isotope", "polymer", "alkane"],
        "rubric": """CHEMISTRY RUBRIC (Class 12)
─────────────────────────────
[1] Correct definition / concept                → 1 mark
[2] Balanced chemical equation (if applicable)  → 1 mark
[3] Mechanism / explanation of steps            → 1 mark
[4] Conditions / reagents stated                → 1 mark
[5] Application / example given                 → 1 mark
─────────────────────────────
Total: 5 marks
Note: Equations must be balanced; unbalanced = 0 for that criterion."""
    },
    "biology": {
        "keywords": ["cell", "organism", "dna", "gene", "protein", "enzyme", "tissue",
                     "organ", "photosynthesis", "respiration", "evolution", "mitosis",
                     "meiosis", "hormone", "nervous", "digestion", "ecosystem",
                     "chromosome", "mutation", "heredity", "species", "bacteria"],
        "rubric": """BIOLOGY RUBRIC (Class 12)
─────────────────────────────
[1] Correct definition / identification         → 1 mark
[2] Accurate biological process explained       → 2 marks
[3] Diagram / labelled parts (if applicable)    → 1 mark
[4] Real-world example or significance given    → 1 mark
─────────────────────────────
Total: 5 marks
Note: Award diagram mark only if description implies correct structure."""
    },
    "history": {
        "keywords": ["war", "empire", "revolution", "king", "queen", "century",
                     "independence", "colony", "treaty", "battle", "civilization",
                     "ancient", "medieval", "modern", "political", "social", "cultural",
                     "nationalism", "movement", "leader", "reign", "dynasty"],
        "rubric": """HISTORY / SOCIAL SCIENCE RUBRIC (Class 10)
─────────────────────────────
[1] Accurate historical facts / dates           → 1 mark
[2] Cause and effect explained                  → 2 marks
[3] Key figures / events mentioned              → 1 mark
[4] Conclusion / significance stated            → 1 mark
─────────────────────────────
Total: 5 marks
Note: Vague answers without specific dates or names lose marks."""
    },
    "fallback": {
        "keywords": [],
        "rubric": """GENERAL FALLBACK RUBRIC
─────────────────────────────
[1] Relevance to the question asked             → 1 mark
[2] Coverage of key points                      → 2 marks
[3] Clarity and coherence of explanation        → 1 mark
[4] Logical structure and language quality      → 1 mark
─────────────────────────────
Total: 5 marks
Note: Used when no subject-specific rubric matches."""
    }
}

# ─────────────────────────────────────────────
#  RUBRIC RETRIEVAL  (keyword matching)
# ─────────────────────────────────────────────
def retrieve_rubric(question: str) -> tuple[str, str]:
    """Return (subject_name, rubric_text) for the best-matching rubric."""
    q_lower = question.lower()
    best_subject = "fallback"
    best_score = 0

    for subject, data in RUBRICS.items():
        if subject == "fallback":
            continue
        score = sum(1 for kw in data["keywords"] if kw in q_lower)
        if score > best_score:
            best_score = score
            best_subject = subject

    return best_subject, RUBRICS[best_subject]["rubric"]


# ─────────────────────────────────────────────
#  LLM EVALUATION  (Grok via OpenAI-compat SDK)
# ─────────────────────────────────────────────
def build_prompt(question: str, student_answer: str, rubric: str, use_rubric: bool) -> str:
    if use_rubric:
        return f"""You are a strict but fair academic evaluator.

QUESTION:
{question}

STUDENT ANSWER:
{student_answer}

RUBRIC (use this to award marks):
{rubric}

Evaluate the student's answer strictly against the rubric above.
Return ONLY a valid JSON object — no markdown, no explanation outside JSON.

{{
  "marks_awarded": <integer>,
  "max_marks": <integer from rubric>,
  "feedback": "<concise feedback pointing to what was good and what was missing>",
  "justification": "<criterion-by-criterion justification referencing rubric points>"
}}"""
    else:
        return f"""You are a strict but fair academic evaluator.

QUESTION:
{question}

STUDENT ANSWER:
{student_answer}

Evaluate this answer on general academic quality (no specific rubric provided).
Award marks out of 5 based on: correctness, coverage, clarity, and language.
Return ONLY a valid JSON object — no markdown, no explanation outside JSON.

{{
  "marks_awarded": <integer 0-5>,
  "max_marks": 5,
  "feedback": "<concise feedback>",
  "justification": "<your reasoning for the marks>"
}}"""


def evaluate_with_grok(question: str, student_answer: str, rubric: str,
                        use_rubric: bool, api_key: str) -> dict:
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.x.ai/v1",
    )
    prompt = build_prompt(question, student_answer, rubric, use_rubric)

    response = client.chat.completions.create(
        model="grok-3-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    raw = response.choices[0].message.content.strip()
    # Strip possible ```json fences
    raw = re.sub(r"^```(?:json)?", "", raw).strip()
    raw = re.sub(r"```$", "", raw).strip()
    return json.loads(raw)


# ─────────────────────────────────────────────
#  HELPER: score colour
# ─────────────────────────────────────────────
def score_class(awarded, max_m):
    ratio = awarded / max_m if max_m else 0
    if ratio >= 0.7:
        return "score-green"
    elif ratio >= 0.4:
        return "score-yellow"
    return "score-red"


def render_result(result: dict, title: str = "Evaluation Result"):
    awarded = result.get("marks_awarded", 0)
    max_m   = result.get("max_marks", 5)
    css_cls = score_class(awarded, max_m)

    st.markdown(f"#### {title}")
    st.markdown(
        f'<div class="result-card">'
        f'<span class="label-tag">Score</span><br>'
        f'<span class="score-big {css_cls}">{awarded} / {max_m}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<span class="label-tag">Feedback</span>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="feedback-box">{result.get("feedback","—")}</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<span class="label-tag">Justification</span>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="feedback-box">{result.get("justification","—")}</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
#  API KEY (from Streamlit Secrets only)
# ─────────────────────────────────────────────
api_key_input = ""
try:
    api_key_input = st.secrets["GROK_API_KEY"]
except Exception:
    pass

compare_mode = False


# ─────────────────────────────────────────────
#  MAIN UI
# ─────────────────────────────────────────────
st.markdown('<div class="hero-title">Mini Answer Evaluator</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">Rubric-based AI evaluation · Physics · Math · English · Chemistry · Biology · History</div>',
    unsafe_allow_html=True,
)

question = st.text_area(
    "📌 Question",
    placeholder="e.g. Define Newton's Second Law of Motion and state its formula.",
    height=90,
)

student_answer = st.text_area(
    "✏️ Student Answer",
    placeholder="Paste or type the student's answer here…",
    height=160,
)

evaluate_btn = st.button("🔍 Evaluate", use_container_width=True, type="primary")

# ─────────────────────────────────────────────
#  EVALUATION LOGIC
# ─────────────────────────────────────────────
if evaluate_btn:
    if not api_key_input:
        st.error("GROK_API_KEY not found. Please set it in Streamlit Secrets.")
    elif not question.strip():
        st.warning("Please enter a question.")
    elif not student_answer.strip():
        st.warning("Please enter the student's answer.")
    else:
        subject, rubric_text = retrieve_rubric(question)

        # Show retrieved rubric
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown(
            f'<span class="label-tag">Rubric Retrieved → {subject.upper()}</span>',
            unsafe_allow_html=True,
        )
        st.markdown(f'<div class="rubric-card">{rubric_text}</div>', unsafe_allow_html=True)

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        if compare_mode:
            col1, col2 = st.columns(2)

            with col1:
                with st.spinner("Evaluating WITH rubric…"):
                    try:
                        r_with = evaluate_with_grok(
                            question, student_answer, rubric_text,
                            use_rubric=True, api_key=api_key_input
                        )
                        render_result(r_with, "✅ With Rubric")
                    except Exception as e:
                        st.error(f"Error: {e}")

            with col2:
                with st.spinner("Evaluating WITHOUT rubric…"):
                    try:
                        r_without = evaluate_with_grok(
                            question, student_answer, rubric_text,
                            use_rubric=False, api_key=api_key_input
                        )
                        render_result(r_without, "❌ Without Rubric")
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            with st.spinner("Evaluating…"):
                try:
                    result = evaluate_with_grok(
                        question, student_answer, rubric_text,
                        use_rubric=True, api_key=api_key_input
                    )
                    render_result(result)
                except json.JSONDecodeError:
                    st.error("The model returned non-JSON output. Try again.")
                except Exception as e:
                    st.error(f"API Error: {e}")
