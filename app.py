import streamlit as st
from openai import OpenAI
import json

# -------------------------------
# 🔐 Load Grok API from Secrets
# -------------------------------
client = OpenAI(
    api_key=st.secrets["GROK_API_KEY"],
    base_url="https://api.x.ai/v1"
)

# -------------------------------
# 📚 Rubrics
# -------------------------------
RUBRICS = {
    "physics": {
        "keywords": ["force", "motion", "newton", "acceleration"],
        "rubric": """
        - Definition correctness
        - Formula usage (F = ma)
        - Concept clarity
        - Units and accuracy
        Max Marks: 5
        """
    },
    "math": {
        "keywords": ["solve", "equation", "integral", "derivative"],
        "rubric": """
        - Correct steps
        - Method used
        - Final answer accuracy
        Max Marks: 5
        """
    },
    "english": {
        "keywords": ["explain", "theme", "story", "paragraph"],
        "rubric": """
        - Clarity of explanation
        - Key points covered
        - Language quality
        Max Marks: 5
        """
    }
}

FALLBACK_RUBRIC = """
- Relevance to question
- Coverage of key points
- Clarity
- Logical structure
- Language quality
Max Marks: 5
"""

# -------------------------------
# 🔍 Rubric Retrieval
# -------------------------------
def get_rubric(question):
    q = question.lower()
    for subject, data in RUBRICS.items():
        for keyword in data["keywords"]:
            if keyword in q:
                return subject, data["rubric"]
    return "fallback", FALLBACK_RUBRIC

# -------------------------------
# 🤖 Prompt Builder
# -------------------------------
def build_prompt(question, answer, rubric):
    return f"""
You are a strict examiner.

Evaluate the student's answer using the rubric.

Question:
{question}

Student Answer:
{answer}

Rubric:
{rubric}

Return STRICT JSON ONLY:
{{
    "marks_awarded": int,
    "max_marks": 5,
    "feedback": "...",
    "justification": "..."
}}
"""

# -------------------------------
# 🧠 LLM Evaluation (Grok)
# -------------------------------
def evaluate_answer(question, answer, rubric):
    prompt = build_prompt(question, answer, rubric)

    response = client.chat.completions.create(
        model="grok-2-latest",
        messages=[
            {"role": "system", "content": "You are a strict evaluator."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    return response.choices[0].message.content

# -------------------------------
# 🧪 Safe JSON Parsing
# -------------------------------
def safe_parse(output):
    try:
        return json.loads(output)
    except:
        return {
            "error": "Invalid JSON from model",
            "raw_output": output
        }

# -------------------------------
# 🌐 Streamlit UI
# -------------------------------
st.set_page_config(page_title="Mini Answer Evaluator")

st.title("📊 Mini Answer Evaluator")

question = st.text_area("Enter Question")
answer = st.text_area("Enter Student Answer")

if st.button("Evaluate"):
    if not question or not answer:
        st.warning("Please enter both question and answer.")
    else:
        subject, rubric = get_rubric(question)

        st.subheader("📚 Retrieved Rubric")
        st.write(f"**Subject:** {subject}")
        st.write(rubric)

        with st.spinner("Evaluating..."):
            raw_output = evaluate_answer(question, answer, rubric)
            result = safe_parse(raw_output)

        st.subheader("🧠 Evaluation Result")
        st.json(result)
