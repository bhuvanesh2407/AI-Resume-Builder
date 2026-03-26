import requests
import json
import time
from models.test.test_word import Resume, ResumeRenderer, WordDoc, PageSize, PageMargin
from docx.shared import Inches, Cm
from resume import from_dict
import re
import traceback


def extract_json(text):
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        return text[start:end+1]
    return text

def generate_ai_resume(jd: str, resume_content: str, retries: int = 2) -> dict:
    """
    Generate an ATS-optimized resume in JSON format using AI.
    """
    url = "https://text.pollinations.ai/openai/v1/chat/completions"

    system_prompt = (
        "You are an ATS resume generator.\n"
        "Return ONLY valid JSON.\n"
        "DO NOT include reasoning_content.\n"
        "DO NOT think step by step.\n"
        "DO NOT explain.\n"
        "DO NOT include any text before or after JSON.\n"
        "Output must start with { and end with }.\n"
        "Strictly follow schema."
    )

    user_prompt = f"""
Create an ATS-optimized resume tailored to the following job description.

JOB DESCRIPTION:
{jd}

CANDIDATE DATA:
{resume_content}

IMPORTANT RULES:
- Output ONLY JSON
- No ``` or markdown
- No comments
- No extra keys
- No missing keys
- Dates must be YYYY-MM-DD where possible
- If dates are mentioned like January 2025 keep it as it is
- If any data is missing like any required data wherever it cant be generated, then keep the text value empty

SCHEMA:
{{
  "name": "string",
  "designation": "string",
  "place": "string",
  "emails": ["string"],
  "mobile_numbers": ["string"],
  "links": ["string"],
  "nationality": "string|null",
  "dob": "YYYY-MM-DD|null",
  "visa_status": "string|null",
  "notice_period": "string|null",
  "profile_description": "string|null",
  "professional_summary": "string|null",
  "technical_skills": "string|null",
  "professional_experience": [
    {{
      "job_title": "string",
      "company_name": "string",
      "place": "string",
      "from_date": "string|null",
      "to_date": "string|null",
      "description": "string|null"
    }}
  ],
  "technical_projects": [
    {{
      "project_name": "string",
      "description": "string|null"
    }}
  ],
  "education": [
    {{
      "degree_name": "string",
      "college_name": "string",
      "place": "string",
      "completed_on": "string|null",
      "result": "string|null",
      "description": "string|null"
    }}
  ],
  "certifications": [
    {{
      "title": "string",
      "issuing_company": "string",
      "completion_date": "string|null"
    }}
  ]
}}
"""

    payload = {
        "model": "openai",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0,
        "response_format": {"type": "json_object"},
        "max_tokens": 5000
    }

    for attempt in range(retries + 1):
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()

            print(data)

            choice = data["choices"][0]
            message = choice["message"]

            # Detect truncation
            if choice.get("finish_reason") == "length":
                raise ValueError("Response truncated. Increase max_tokens.")

            # Extract content safely
            text_output = message.get("content")

            # If only reasoning exists → force retry
            if not text_output:
                raise ValueError("Model returned no usable content (only reasoning).")
            
            text_output = text_output.strip()
            
            # Remove markdown if any
            if text_output.startswith("```"):
              text_output = "\n".join(text_output.splitlines()[1:-1])

            text_output = extract_json(text_output)

            # Try parsing JSON
            try:
                return json.loads(text_output)
            except json.JSONDecodeError:
                # Attempt to repair common JSON mistakes
                repaired = _repair_json(text_output)
                return json.loads(repaired)

        except Exception as e:
            print(f"Attempt {attempt + 1} failed:", str(e))
            print("Traceback:")
            traceback.print_exc()  # Shows full traceback
            # Optional: inspect variables if needed
            # print("Current variables:", locals())
            time.sleep(1)

    # Return empty dict if all retries fail
    return {}

def _repair_json(text: str) -> str:
    """
    Attempt basic repair on AI-generated JSON text.
    Handles trailing commas, single quotes, and extra whitespace.
    """
    # Remove trailing commas before } or ]
    text = re.sub(r',\s*([}\]])', r'\1', text)

    # Replace single quotes with double quotes if needed
    if text.count('"') < text.count("'"):
        text = text.replace("'", '"')

    # Strip unwanted whitespace
    text = text.strip()

    return text

if __name__ == "__main__":
  # Sample Job Description
  jd = """
  We are looking for a Python Developer with experience in REST APIs,
  FastAPI, and cloud platforms like AWS. Candidate should have strong
  problem-solving skills and experience with SQL and microservices.
  """

  with open('models/test/test.json', 'r') as file:
    data = json.load(file)  # This reads the JSON into a Python dictionary/list
  # Sample Resume Content (raw input)
  resume_content = json.dumps(data)
  print("json file loaded")

  # Generate AI Resume
  print("Generating Resume...")
  result = generate_ai_resume(jd, resume_content)

  # Pretty print output
  if result:
      print("\n✅ Generated Resume JSON:\n")
      print(json.dumps(result, indent=4))

      # Optional: Convert to dataclass
      try:
          print(type(result))
          resume_obj = from_dict(Resume, result)
          print("\n✅ Converted to Resume Dataclass Successfully!")

          page_size = PageSize(Inches(8.27), Inches(11.69))
          page_margin = PageMargin(top=0.5, bottom=1, left=0.5, right=0.5)

          document = WordDoc(page_size, page_margin, font_name="Helvetica")
          renderer = ResumeRenderer(resume=resume_obj, word_doc=document)

          print("Resume is Rendering...")

          renderer.render()

          document.save("AI_Resume.docx")
          print("Resume saved as 'AI_Resume.docx'")

      except TypeError as e:
          print("\n⚠️ Dataclass conversion failed:", str(e))
  else:
      print("\n❌ Failed to generate resume")