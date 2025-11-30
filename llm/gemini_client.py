# nlp-service/llm/gemini_client.py

import os
import time
import json
import re
import google.generativeai as genai
from typing import Dict, Any
from dotenv import load_dotenv
from google.generativeai.types import GenerationConfig

load_dotenv()


class GeminiClient:
    """
    Stable Gemini wrapper:
    - Strict JSON model prompting
    - Auto-repair malformed JSON
    - Extract JSON even from noisy text
    - Force rewrite fallback
    """

    def __init__(self, model: str = "models/gemini-2.5-flash-preview-09-2025"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY missing in environment (.env).")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)

    # -----------------------------------------------------------
    # Extract JSON even if surrounding text exists
    # -----------------------------------------------------------
    def _extract_json(self, raw: str):
        try:
            return json.loads(raw)
        except:
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                return json.loads(match.group(0))
        return None

    # -----------------------------------------------------------
    # Attempt JSON repair
    # -----------------------------------------------------------
    def _repair_json(self, raw: str):
        try:
            cleaned = raw.strip()

            # Remove trailing commas
            cleaned = cleaned.replace(",}", "}")
            cleaned = cleaned.replace(",]", "]")

            return json.loads(cleaned)
        except:
            return None

    # -----------------------------------------------------------
    # MASTER FUNCTION: generates always-valid JSON
    # -----------------------------------------------------------
    def create_json_response(self, prompt: str, max_tokens: int = 600) -> Dict[str, Any]:

        last_exc = None

        for attempt in range(3):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=GenerationConfig(
                        max_output_tokens=max_tokens,
                        temperature=0.1,
                        response_mime_type="application/json"
                    )
                )

                raw = response.text or ""

                # 1️⃣ Direct JSON
                try:
                    parsed = json.loads(raw)
                    return {"json": parsed, "raw": raw}
                except:
                    pass

                # 2️⃣ Attempt repair
                repaired = self._repair_json(raw)
                if repaired is not None:
                    return {"json": repaired, "raw": raw}

                # 3️⃣ Try extracting from messy output
                extracted = self._extract_json(raw)
                if extracted is not None:
                    return {"json": extracted, "raw": raw}

                # 4️⃣ FINAL REWRITE – guarantees valid JSON
                rewrite_prompt = f"""
                Convert the following text into VALID JSON ONLY.
                Do not include comments, markdown, or text outside the JSON.
                Fix formatting, remove invalid commas, ensure every key has a value.

                RAW:
                {raw}
                """

                retry = self.model.generate_content(
                    rewrite_prompt,
                    generation_config=GenerationConfig(
                        max_output_tokens=max_tokens,
                        temperature=0.0,
                        response_mime_type="application/json"
                    )
                )

                rewritten_raw = retry.text
                final_json = json.loads(rewritten_raw)

                return {"json": final_json, "raw": rewritten_raw}

            except Exception as e:
                last_exc = e
                time.sleep(0.6)

        # FATAL
        raise RuntimeError(f"Gemini failed after auto-repair: {last_exc}")
