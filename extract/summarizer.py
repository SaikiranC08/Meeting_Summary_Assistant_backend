# nlp-service/extract/summarizer.py
from dotenv import load_dotenv
load_dotenv()
from utils.json_sanitizer import sanitize_summary


class MeetingSummarizer:
    def __init__(self, llm_client):
        self.llm = llm_client

    def generate_summary(self, text: str):
        prompt = f"""
You are a strict JSON generator. 
ALWAYS return ONLY valid JSON. 
NO explanation. NO markdown. NO text before or after the JSON.
If content is missing, return an empty string or empty list.

Transcript:
\"\"\"{text}\"\"\"

Return JSON in this exact format:

{{
  "tldr": "",
  "executive_summary": "",
  "progress_updates": [],
  "challenges": [],
  "risks_blockers": [],
  "decisions": [],
  "next_steps": [],
  "project_health": "",
  "team_alignment": {{
    "agreements": [],
    "misalignments": [],
    "confusions": []
  }}
}}
"""

        resp = self.llm.create_json_response(prompt, max_tokens=1200)
        return {
            "ok": True,
            "source_text_snippet": text[:180],
            "summary": sanitize_summary(resp["json"]),
            "llm_raw": resp["raw"]
        }
