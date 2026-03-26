import requests
import traceback
import json
import time
import re
import os
from groq import Groq
from huggingface_hub import InferenceClient

from dotenv import load_dotenv
load_dotenv()

class BaseAI():

    sys_prompt = (
        "You are an ATS resume generator.\n"
        "Return ONLY valid JSON.\n"
        "DO NOT include reasoning_content.\n"
        "DO NOT think step by step.\n"
        "DO NOT explain.\n"
        "DO NOT include any text before or after JSON.\n"
        "Output must start with { and end with }.\n"
        "Try to complete the response within 1500 completion tokens itself\n",
        "Strictly follow schema."
    )

    important_rules = """
        IMPORTANT RULES:
            - Output ONLY JSON
            - No ``` or markdown
            - The generated context should come under 1500 completion tokens only (VERY IMPORTANT)
            - No comments
            - No extra keys
            - No missing keys
            - Dates must be YYYY-MM-DD where possible
            - If dates are mentioned like January 2025 keep it as it is
            - If any data is missing like any required data wherever it cant be generated, then keep the text value empty
        """

    with open("models/assets/resume_prompts.json", "r") as json_file:
        resume_parts_prompt = json.load(json_file) 


    with open("models/assets/resume_schema.json", "r") as json_file:
        resume_schema = json.load(json_file) 

    def extract_json(self, text):
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            return text[start:end+1]
        return text
    
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

    def define_resume_part_prompt(self, _type: str):
        return self.resume_parts_prompt[_type]    

    def generate_schema_for_prompt(self, _type: str):
        return self.resume_schema[_type]

    def generate_user_prompt(self, jd: str, part: str, resume_content: str):

        user_prompt = f"""
        Generate the {part} section of a resume in JSON format based on the candidate data. Here are the complete details:

        {self.define_resume_part_prompt(part)}

        INSTRUCTIONS:
        1. Follow the JSON schema strictly:
        {self.generate_schema_for_prompt(part)}
        Set missing optional fields to null. Do NOT add extra fields or text outside JSON.


        2. Align the content with the provided JOB DESCRIPTION:
        {jd}

        3. Use only the data provided:
        {resume_content}

        4. Follow professional resume conventions:
        - ATS-friendly
        - Concise, clear, and results-oriented
        - Avoid personal pronouns (I, We)
        - Limit bullets/lines according to section type

        5. Return ONLY valid JSON. No explanations or extra text.

        Additional Rules:
        {self.important_rules}

    """
        
        return user_prompt


class PollinationsAI(BaseAI):
    
    url = "https://text.pollinations.ai/openai/v1/chat/completions"

    def __init__(self,  debug):
        self.debug = debug
        self.ai_model = "openai"

    def generate_from_ai(self, jd: str, resume_content: str, part: str = "introduction", retries: int = 2) -> dict:

        user_prompt = self.generate_user_prompt(jd=jd, resume_content=resume_content, part=part)

        payload = {
            "model": self.ai_model,
            "messages": [
                {"role": "system", "content": "".join(self.sys_prompt)},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "max_tokens": 20000
        }

        for attempt in range(retries + 1):
            try:
                response = requests.post(self.url, json=payload, timeout=30)
                if response.status_code != 200:
                    print("Status:", response.status_code)
                    print("Response:", response.text)
                    raise ValueError("API request failed")
                data = response.json()

                if (self.debug):
                    print("AI Response: ")
                    print(json.dumps(data, indent=4))

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

                text_output = self.extract_json(text_output)

                # Try parsing JSON
                try:
                    return json.loads(text_output)
                except json.JSONDecodeError:
                    # Attempt to repair common JSON mistakes
                    repaired = self._repair_json(text_output)
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


class GroqAI(BaseAI):
    def __init__(self):
        self.api_key = os.environ.get("GROQ_API_KEY")
    
    def generate_from_ai(self, jd: str, resume_content: str, part: str = "introduction", retries: int = 2) -> dict:

        client = Groq(api_key=self.api_key)

        user_prompt = self.generate_user_prompt(jd=jd, part=part, resume_content=resume_content)
        
        for attempt in range(retries + 1):
            completion = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {"role": "system", "content": "".join(self.sys_prompt)},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_completion_tokens=5000,
                top_p=1,
            )

            response_text = completion.choices[0].message.content.strip()
            print(f"Attempt {attempt+1} raw:\n", response_text)

            try:
                return json.loads(response_text)

            except json.JSONDecodeError:
                print("Invalid JSON, retrying...")
                # Attempt to repair common JSON mistakes
                repaired = self._repair_json(response_text)
                return json.loads(repaired)

        return None
    


class HuggingFaceAI(BaseAI):
    def __init__(self):
        self.api_key = os.environ.get("HUGGING_FACE_API_KEY")
    
    def generate_from_ai(self, jd: str, resume_content: str, part: str = "introduction", retries: int = 2) -> dict:

        client = InferenceClient(token=os.environ.get("HUGGING_FACE_API_KEY"))

        user_prompt = self.generate_user_prompt(jd=jd, part=part, resume_content=resume_content)
        
        prompt = "".join(self.sys_prompt) + "\n" + user_prompt

        for attempt in range(retries + 1):
            completion = client.chat.completions.create(
                
                # inputs=prompt,
                model="openai/gpt-oss-120b",
                messages=[
                    {"role": "system", "content": "".join(self.sys_prompt)},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=5000,
                temperature=0.2,
                top_p=1,
            )

            response_text = completion.choices[0].message.content.strip()
            print(f"Attempt {attempt+1} raw:\n", response_text)

            try:
                return json.loads(response_text)

            except json.JSONDecodeError:
                print("Invalid JSON, retrying...")
                # Attempt to repair common JSON mistakes
                repaired = self._repair_json(response_text)
                return json.loads(repaired)

        return None        


class AI:

    def __init__(self, model: str, debug: bool = False):
        self.debug = debug

        if model == "pollinations":
            self.model = PollinationsAI(self.debug)
        elif model == "groq":
            self.model = GroqAI()
        elif model == "hugging_face":
            self.model = HuggingFaceAI()
        else:
            raise ValueError("Unsupported model")
        
    def switch_model(self, model: str):
        """Switch to a different AI backend on the fly"""
        if model == "pollinations":
            self.model = PollinationsAI(self.debug)
        elif model == "groq":
            self.model = GroqAI()
        else:
            raise ValueError("Unsupported model")


if __name__ == "__main__":

    def generate_introduction(resume_data, jd ):
        resume = AI()

        keys = ['designation','dob','emails','links','mobile_numbers','name','nationality','notice_period','place','visa_status']
        resume_content = {key: resume_data.get(key) for key in keys}


        result = resume.generate_from_ai(jd = jd, part="introduction", resume_content=resume_content)
        
        # Pretty print output
        if result:
            print(type(result))
            print("\n✅ Generated Resume JSON:\n")
            print(json.dumps(result, indent=4))

    def generate_professional_summary(resume_data, jd ):
        resume = AI()

        resume_content = resume_data['professional_summary']
        

        result = resume.generate_from_ai(jd = jd, part="professional_summary", resume_content=resume_content)
        
        # Pretty print output
        if result:
            print(type(result))
            print("\n✅ Generated Resume JSON:\n")
            print(json.dumps(result, indent=4))

    def generate_technical_skills(resume_data, jd ):
        resume = AI()

        resume_content = resume_data['technical_skills']


        result = resume.generate_from_ai(jd = jd, part="technical_skills", resume_content=resume_content)
        
        # Pretty print output
        if result:
            print(type(result))
            print("\n✅ Generated Resume JSON:\n")
            print(json.dumps(result, indent=4))

    def generate_professional_experience(resume_data, jd ):
        resume = AI(model="hugging_face")

        resume_content = resume_data['experience']
        
        result = resume.model.generate_from_ai(jd = jd, part="professional_experience", resume_content=resume_content)
        
        # Pretty print output
        if result:
            print(type(result))
            print("\n✅ Generated Resume JSON:\n")
            print(json.dumps(result, indent=4))

    def generate_technical_projects(resume_data, jd ):
        resume = AI()

        resume_content = resume_data['projects']

        result = resume.generate_from_ai(jd = jd, part="technical_projects", resume_content=resume_content)
        
        # Pretty print output
        if result:
            print(type(result))
            print("\n✅ Generated Resume JSON:\n")
            print(json.dumps(result, indent=4))

    def generate_certifications(resume_data, jd ):
        resume = AI()

        resume_content = resume_data['certifications']

        result = resume.generate_from_ai(jd = jd, part="certifications", resume_content=resume_content)
        
        # Pretty print output
        if result:
            print(type(result))
            print("\n✅ Generated Resume JSON:\n")
            print(json.dumps(result, indent=4))



    # Sample Job Description
    jd = """
    We are looking for a Python Developer with experience in REST APIs,
    FastAPI, and cloud platforms like AWS. Candidate should have strong
    problem-solving skills and experience with SQL and microservices.
    """

    with open('models/test/test.json', 'r') as file:
        data = json.load(file)  # This reads the JSON into a Python dictionary/list

    generate_professional_experience(resume_data=data, jd=jd)


