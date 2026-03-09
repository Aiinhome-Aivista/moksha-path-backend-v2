import json
import os
import warnings
from mistralai import Mistral
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")
# import google.generativeai as genai
import google as genai
from config import ACTIVE_LLM, MISTRAL_API_KEY, MISTRAL_MODEL, GEMINI_API_KEY, GEMINI_MODEL

def generate_questions_with_ai(board_name, class_name, subject_name, topic_name, count=5):
    """
    Generates questions using the configured Active LLM.
    Returns a Python list of dictionaries.
    """
    
    # Prompt Engineering for JSON Output
    # UPDATED: Added instruction for 'estimated_time'
    prompt = f"""
    You are an expert academic question generator.
    Generate {count} distinct questions for:
    - Board: {board_name}
    - Class: {class_name}
    - Subject: {subject_name}
    - Topic: {topic_name}
    
    Include a mix of:
    1. MCQ (Multiple Choice Questions) with 4 options.
    2. TrueFalse questions.
    3. Textual (Short Answer) questions.

    STRICT JSON FORMAT REQUIRED:
    Return ONLY a raw JSON array. Do not wrap in markdown (```json ... ```).
    
    Structure:
    [
        {{
            "question_text": "Question string",
            "question_type": "MCQ",  // or "TrueFalse" or "Textual"
            "difficulty_level": "Medium", // Easy, Medium, Hard
            "options": {{"a": "Option 1", "b": "Option 2", "c": "Option 3", "d": "Option 4"}}, // Null for Textual/TrueFalse
            "correct_answer": "b", // The correct key for MCQ/TrueFalse or text for Textual
            "marks": 1,
            "estimated_time": 60 // Integer: Estimated time in seconds to solve (e.g., 30, 60, 90, 120)
        }}
    ]
    """

    try:
        # ---------------------------
        # 1. Mistral Cloud Logic
        # ---------------------------
        if ACTIVE_LLM == "mistral_cloud":
            client = Mistral(api_key=MISTRAL_API_KEY)
            response = client.chat.complete(
                model=MISTRAL_MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            raw_content = response.choices[0].message.content

        # ---------------------------
        # 2. Gemini Logic
        # ---------------------------
        elif ACTIVE_LLM == "gemini":
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel(GEMINI_MODEL)
            response = model.generate_content(prompt)
            raw_content = response.text

        else:
            raise Exception("Invalid Active LLM Configuration")

        # ---------------------------
        # 3. Clean & Parse JSON
        # ---------------------------
        # Clean Code Blocks if LLM adds them
        clean_json = raw_content.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_json)

    except Exception as e:
        print(f"AI Generation Error: {str(e)}")
        return None