import os
from google.genai import Client

client = Client(api_key=os.getenv("GEMINI_API_KEY"))

def classify_intent(question: str) -> bool:
    prompt = f"""
You are an intent classifier for a government analytics system.

Question:
"{question}"

Is this question related to Aadhaar enrolment, Aadhaar updates,
UIDAI operations, demographics, state-wise trends, or prediction?

Reply ONLY with YES or NO.
"""
    try:
        response = client.models.generate_content(
            model="gemini-pro-latest",
            contents=prompt
        )
        return response.text.strip().upper().startswith("YES")
    except Exception:
        return False

def generate_human_insight(context: str) -> str:
    prompt = f"""
Convert the following context into a professional policy insight.

Use EXACTLY this format:
Finding:
Impact:
Recommendation:

Context:
{context}
"""
    try:
        response = client.models.generate_content(
            model="gemini-pro-latest",
            contents=prompt
        )
        return response.text.strip()
    except Exception:
        return """
Finding:
Relevant Aadhaar trends were identified.

Impact:
These trends affect operational planning.

Recommendation:
Review data regularly to optimize resource allocation.
""".strip()
