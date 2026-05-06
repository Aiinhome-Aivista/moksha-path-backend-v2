import os
import json
import httpx
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Basic details from .env
api_key = os.getenv("DATABRICKS_API_KEY")
base_url = os.getenv("DATABRICKS_BASE_URL")
ca_bundle = os.getenv("DATABRICKS_CA_BUNDLE")
model_name_env = os.getenv("DATABRICKS_MODEL_NAME")

# Replace 'path/to/your/ca.crt' with the actual path to your CA certificate file
# custom_ca_path = "AzureDataBricks.pem"
httpx_client = httpx.Client(verify=False)
# client = OpenAI(http_client=httpx_client)

# Use the client as usual
os.environ["REQUESTS_CA_BUNDLE"] = ca_bundle

# Initialize OpenAI client with environment variables
client = OpenAI(
    http_client=httpx_client,
    api_key=api_key,
    base_url=base_url
)

def get_response(ticket: str):  
    model_name = model_name_env
    response = client.chat.completions.create(
        model= model_name, #'databricks-gpt-oss-20b',
        messages= [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "You are an experienced educator. Your task is to analyze student performance data for various subjects and chapters, and generate clear, chapter-wise remediation pointers to help the student improve. Focus only on providing actionable remediation without including summaries or progress information."
                    }
                ]
            },
            {"role": "user", "content": ticket}
        ],
        # reasoning_effort='medium'
        # max_tokens=4000
    )
 
    # Extract and parse the last message content
    content = response.choices[0].message.content
    # return json.loads(content[-1]['text'].replace('```json','').replace('```',''))
    return content #[-1]['text']

def get_remediation_pointers(student_performance_data):
    """
    Constructs the prompt and gets the remediation pointers from the AI.
    """
    # Convert data to string if it's a dictionary
    if isinstance(student_performance_data, dict):
        student_performance_str = json.dumps(student_performance_data)
    else:
        student_performance_str = student_performance_data

    # Exact prompt as per your requirement
    prompt = f"""You are given a JSON object containing the multiple Chapter wise performance data of a student for various subjects, including accuracy and average time per difficulty level.

input_json_object = {student_performance_str}

Generate chapter-wise remediation pointers focused on areas the student needs to improve.
**Instructions:**  
- Provide exactly 5 short and actionable remediation pointers for each chapter in each subject.  
- Each pointer must follow this style: "[Actionable Goal]: [Specific performance insight from data]. [Recommendation]."
- Example styles:
  1. "Master L1 first: Accuracy is below 60% on basics. Engine won't escalate until you are consistent."
  2. "Push L2 past 70%: Currently at 52% accuracy (borderline). Timed practice sessions will help."
  3. "Address L3 Accuracy: 36% accuracy detected. Focus on advanced theorems to unlock next levels."
  4. "Optimize Time: Spending 120s+ on Easy questions. Practice speed drills to improve efficiency."
  5. "Consistency Check: High variance in L1 scores. Aim for 80%+ consistency across all sub-topics."
- Do not include progress, overall accuracy, or performance summaries.  
- Output must strictly follow this JSON structure:
{{
  "subjects": {{
    "list": [
      {{
        "subject_id": <subject_id>,
        "chapters": [
          {{
            "chapter_id": <chapter_id>,
            "chapter_name": "<chapter_name>",
            "remediation_pointers": [
              "<Pointer 1>",
              "<Pointer 2>",
              "<Pointer 3>",
              "<Pointer 4>",
              "<Pointer 5>"
            ]
          }}
          // more chapters if available
        ]
      }}
    ]
  }}
}}

Use the 'input_json_object' input and generate exactly 5 concise remediation pointers tailored to the student's specific areas of weakness and time management in each chapter.
"""
    # Get raw response from AI
    raw_response = get_response(prompt)
    
    try:
        # Clean the string (remove ```json and ```) and parse into a dictionary
        clean_content = raw_response.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_content)
    except Exception as e:
        # If parsing fails, return the raw response string
        return raw_response
 
 
def generate_principal_insights_ai(data):

    teachers = data.get("teacher_data", [])
    insights = []

    # -------------------------------
    # 1. TOP
    # -------------------------------
    top_teachers = [
        t for t in teachers
        if t.get("bench", 0) >= 70 and
           t.get("risk_res", 0) >= 70 and
           t.get("mock_eng", 0) >= 70 and
           t.get("syllabus", 0) >= 80
    ]

    if top_teachers:
        names = " and ".join([t["teacher"] for t in top_teachers[:2]])
        subjects = " and ".join([t["subjects"] for t in top_teachers[:2]])

        insights.append({
            "type": "top",
            "text": f"{names} ({subjects}) lead on all 5 dimensions — consider as department leads."
        })
    else:
        insights.append({
            "type": "top",
            "text": "No teacher currently meets top performance thresholds — focus on improving benchmark attainment and risk resolution."
        })

    # -------------------------------
    # 2. LOW
    # -------------------------------
    worst = None
    if teachers:
        worst = sorted(
            teachers,
            key=lambda x: (x.get("bench", 0), x.get("risk_res", 0))
        )[0]

        name = " ".join(worst["teacher"].split())
        grade = worst.get("grade")
        grade_part = f", {grade}" if grade and grade != "N/A" else ""

        insights.append({
            "type": "low",
            "text": f"{name} ({worst['subjects']}{grade_part}): "
                    f"Benchmark attainment {int(worst['bench'])}%, "
                    f"Risk resolution {int(worst['risk_res'])}%. "
                    f"Structured support plan recommended."
        })

    # -------------------------------
    # 3. RISK
    # -------------------------------
    risk_candidates = [
        t for t in teachers
        if t.get("risk_res", 0) < 50 and t != worst
    ]

    if risk_candidates:
        risk_teacher = sorted(risk_candidates, key=lambda x: x.get("risk_res", 0))[0]
        name = " ".join(risk_teacher["teacher"].split())

        insights.append({
            "type": "risk",
            "text": f"{name}'s at-risk resolution ({int(risk_teacher['risk_res'])}%) "
                    f"needs focus — strong in delivery, weaker in follow-up. Coaching advised."
        })
    else:
        insights.append({
            "type": "risk",
            "text": "At-risk resolution is stable across teachers — maintain follow-up practices."
        })

    # -------------------------------
    # 4. SYLLABUS
    # -------------------------------
    syllabus = int(float(data.get("syllabus_on_track_percent", 0)))
    prev = data.get("prev_syllabus_percent")

    if prev:
        insights.append({
            "type": "syllabus",
            "text": f"School-wide syllabus timeliness at {syllabus}% — up from {int(prev)}% last term. MokshPath pacing alerts are showing measurable impact."
        })
    else:
        insights.append({
            "type": "syllabus",
            "text": f"School-wide syllabus timeliness at {syllabus}% — pacing is effective."
        })

    # -------------------------------
    # 5. MOCK
    # -------------------------------
    low_mock = [t for t in teachers if t.get("mock_eng", 0) < 80]

    insights.append({
        "type": "mock",
        "text": f"Mock engagement below 80% for {len(low_mock)} teachers. "
                f"Standardise a mock review protocol across departments."
    })

    return insights[:5]
