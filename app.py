import streamlit as st
from openai import OpenAI
import json

# -------------------------------
# 🔐 CONFIG
# -------------------------------
MODEL_NAME = "grok-1"

client = OpenAI(
    api_key=st.secrets["GROK_API_KEY"],
    base_url="https://api.x.ai/v1"
)

# -------------------------------
# 📚 RUBRICS
# -------------------------------
RUBRICS = {
    "physics": {
        "keywords": ["force", "motion", "newton", "acceleration"],
        "criteria": [
            "Definition correctness",
            "Formula usage (F = ma)",
            "Concept clarity",
            "Units and accuracy"
        ]
    },
    "math": {
        "keywords": ["solve", "equation", "integral", "derivative"],
        "criteria": [
            "Correct steps",
            "Method used",
            "Final answer accuracy"
        ]
    },
    "english": {
        "keywords": ["explain", "theme", "story", "paragraph"],
        "criteria": [
            "Clarity",
            "Key points",
            "Language quality"
        ]
    }
}

FALLBACK = [
    "Relevance",
    "Coverage",
    "Clarity",
    "Structure",
    "Language"
]

# -------------------------------
# 🔍 RUBRIC RETRIEVAL
# -------------------------------
def get_rubric(question):
    q = question.lower()
    for subject, data in RUBRICS.items():
        if any(k in q for k in data["keywords"]):
            return subject, data["criteria"]
    return "fallback", FALLBACK

# -------------------------------
# 🤖 PROMPT BUILDER
# -------------------------------
def build_prompt(question, answer, criteria):
    criteria_text = "\n".join([f"- {c}" for c in criteria])

    return f"""
You are a strict examiner.

Evaluate the student's answer using EACH criterion separately.

Question:
{question}

Student Answer:
{answer}

Criteria:
{criteria_text}

Instructions:
- Give marks per criterion (0 or 1 each)
- Sum total marks
- Max marks = number of criteria

Return ONLY JSON:
{{
    "criteria_scores": {{
        "criterion1": 1,
        "criterion2": 0
    }},
    "marks_awarded": int,
    "max_marks": int,
    "feedback": "...",
    "justification": "...",
    "confidence": 0-1
}}
"""

# -------------------------------
# 🧠 LLM CALL (SAFE)
# -------------------------------
def call_llm(prompt):
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a fair and strict examiner."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        return response.choices[0].message.content

    except Exception as e:
        return json.dumps({
            "error": "LLM call failed",
            "details": str(e)
        })

# -------------------------------
# 🧪 SAFE JSON PARSE
# -------------------------------
def safe_parse(text):
    try:
        return json.loads(text)
    except:
        return {
            "error": "Invalid JSON from model",
            "raw_output": text
        }

# -------------------------------
# 🔁 CONSISTENCY CHECK
# -------------------------------
def evaluate_with_consistency(prompt):
    out1 = safe_parse(call_llm(prompt))
    out2 = safe_parse(call_llm(prompt))

    if "marks_awarded" in out1 and "marks_awarded" in out2:
        consistency = abs(out1["marks_awarded"] - out2["marks_awarded"])
    else:
        consistency = "N/A"

    return out1, out2, consistency

# -------------------------------
# 🌐 STREAMLIT UI
# -------------------------------
st.set_page_config(page_title="Mini Answer Evaluator", layout="centered")

st.title("📊 Mini Answer Evaluator")

question = st.text_area("Enter Question")
answer = st.text_area("Enter Student Answer")

show_debug = st.checkbox("Show Debug Info")

if st.button("Evaluate"):
    if not question or not answer:
        st.warning("Please enter both question and answer.")
    else:
        subject, criteria = get_rubric(question)

        st.subheader("📚 Detected Subject")
        st.write(subject)

        st.subheader("📏 Evaluation Criteria")
        st.write(criteria)

        prompt = build_prompt(question, answer, criteria)

        with st.spinner("Evaluating..."):
            res1, res2, consistency = evaluate_with_consistency(prompt)

        st.subheader("🧠 Final Evaluation")
        st.json(res1)

        st.subheader("📊 Consistency Check")
        st.write(f"Difference in marks: {consistency}")

        if show_debug:
            st.subheader("🔍 Debug Output")
            st.write("Run 1:", res1)
            st.write("Run 2:", res2)
