import os
import json
import re
from openai import OpenAI


class OpenAIClient:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set")

        self.client = OpenAI(api_key=api_key)

    def analyze_scenario(self, prompt: str) -> dict:
        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert in autonomous driving scenarios. "
                               "Always respond with valid JSON."
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )

        raw_text = response.choices[0].message.content

        return self._parse_json_safely(raw_text)

    # --------------------------------------------------
    # Robust JSON extraction
    # --------------------------------------------------

    def _parse_json_safely(self, text: str) -> dict:
        """
        Extract and parse JSON from an LLM response.
        Falls back to raw text if parsing fails.
        """

        # 1. Remove Markdown fences ```json ... ```
        cleaned = re.sub(r"```json|```", "", text).strip()

        # 2. Try direct JSON parsing
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # 3. Try to extract first JSON object via regex
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

        # 4. Fallback: return raw text
        return {
            "raw_llm_output": text,
            "parsing_error": True
        }
