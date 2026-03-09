import requests
import warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")
# import google.generativeai as genai
import google as genai
import os
from dotenv import load_dotenv

# ---------- Load environment variables ----------
load_dotenv()

# ---------- LLM Configuration ----------
ACTIVE_LLM = os.getenv("ACTIVE_LLM", "mistral_cloud")  # gemini | mistral_cloud

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash")

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-small-latest")


def call_llm(prompt: str) -> str:
    try:
        # ===============================
        # Gemini Cloud
        # ===============================
        if ACTIVE_LLM == "gemini":
            if not GEMINI_API_KEY:
                return "[LLM Error] Missing GEMINI_API_KEY"

            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel(MODEL_NAME)

            response = model.generate_content(prompt)
            return response.text.strip()


        # ===============================
        # Mistral Cloud
        # ===============================
        elif ACTIVE_LLM == "mistral_cloud":
            if not MISTRAL_API_KEY:
                return "[LLM Error] Missing MISTRAL_API_KEY"

            url = "https://api.mistral.ai/v1/chat/completions"

            headers = {
                "Authorization": f"Bearer {MISTRAL_API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": MISTRAL_MODEL,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3
            }

            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()

            data = response.json()
            return data["choices"][0]["message"]["content"].strip()


        # ===============================
        # Invalid Config
        # ===============================
        else:
            return "[LLM Error] ACTIVE_LLM must be 'gemini' or 'mistral_cloud'."


    except requests.exceptions.RequestException as e:
        return f"[Network Error] {str(e)}"

    except Exception as e:
        return f"[LLM Error] {str(e)}"
