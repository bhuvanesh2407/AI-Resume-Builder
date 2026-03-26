import requests
import traceback
import json
import time
import re
from abc import ABC, abstractmethod

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

    resume_parts_prompt = {
        "introduction":"""
            Generate the Introduction section of a resume in JSON format.

            Instructions:
            1. Extract and structure the candidate’s basic details from the input.
            2. Populate all fields strictly according to the provided schema.

            Field Guidelines:
            - name: Full name of the candidate
            - designation: Current role or target job title (aligned with job description if provided)
            - place: Current location (City, Country format preferred)
            - emails: List all valid email addresses
            - mobile_numbers: Include phone numbers with country code if available
            - links: Include relevant links (LinkedIn, GitHub, Portfolio, etc.)

            Optional Fields (set to null if not available):
            - nationality
            - dob (format: YYYY-MM-DD)
            - visa_status
            - notice_period

            3. Data Rules:
            - Do NOT hallucinate missing personal details
            - Do NOT leave required fields empty—use best available data
            - Normalize formatting (e.g., phone numbers, dates)
            - Remove duplicates in arrays

            4. Job Alignment:
            - If a job description is provided, align the designation accordingly

            5. Output Rules:
            - Return ONLY valid JSON
            - Follow the schema strictly
            - No extra text, explanations, or formatting outside JSON
        """,
        "professional_summary": """
            Generate the Professional Summary section of a resume in JSON format.

            Instructions:
            1. Write a single-paragraph professional summary (4–6 lines).
            2. The summary must include:
            - Total years of experience
            - Key skills and technologies
            - Major achievements or measurable impact
            - Industries or domains worked in
            - Career focus or goals

            3. Writing style:
            - Professional, concise, and results-oriented
            - ATS-friendly with relevant keywords
            - No bullet points (strictly one paragraph)
            - No personal pronouns (I, We)
            - Avoid generic phrases

            4. Job Alignment:
            - Tailor the summary to align with the provided job description (if available)

            5. Data Rules:
            - Do NOT hallucinate years of experience or achievements
            - Use only the provided data
            - Keep it realistic and relevant

            6. Output Rules:
            - Return ONLY valid JSON
            - Follow the schema strictly
            - No extra text outside JSON

            Output Example:

            "
            Dynamic Python Full-Stack Developer with 2+ years of experience specializing in the Django ecosystem to build robust, scalable web applications. 
            Expert in architecting high-performance backends using Django Rest Framework (DRF), integrated with AI solutions and MENA-specific fintech services. 
            Currently based in Riyadh with direct GCC market experience, including regional payment gateway integrations 
            (Tabby, Tamara, Tap) and automated data-sync tools for platforms like Noon. 
            Offering a strong cross-cultural perspective and a proven ability to lead full-stack projects—from responsive frontend development to containerized 
            Python deployments—within fast-paced, collaborative environments across the Middle East.
            "
        """,
        "technical_skills": """
            Generate the Technical Skills section of a resume in JSON format.

            Instructions:
            1. Identify and group skills into logical categories based on the input data.
            - Do NOT strictly rely on predefined categories.
            - Dynamically create appropriate categories such as (but not limited to):
                Programming Languages, Frameworks, Tools, Databases, Cloud, DevOps, Core Competencies, etc.
            - Only include categories that are relevant to the candidate.

            2. Formatting rules (inside the string output):
            - Each category should be written on a new line using \\n
            - Use this exact format per line:
                Category Name: skill1, skill2, skill3
            - Keep each category on a single line (no bullet points)
            - Use commas to separate skills
            - Maintain a clean, ATS-friendly structure

            3. Skill extraction rules:
            - Extract only relevant and realistic skills from the input
            - You may infer closely related skills if strongly implied
            - Do NOT include unrelated or generic terms
            - Avoid duplication across categories

            4. Proficiency:
            - Add proficiency levels only when clearly justified (e.g., Python (Advanced))

            5. Keep the output concise, well-organized, and professional

            6. Job Alignment:
            - Prioritize skills relevant to the provided job description (if available)

            7. Output Rules:
            - Return ONLY valid JSON
            - Follow the schema strictly
            - No extra text outside JSON

            Output Example:

            {
                "technical_skills": "Programming Languages: Python (Advanced), JavaScript, Java\\nFrameworks & Libraries: Django, Flask, React\\nTools & Platforms: Docker, Git, AWS\\nDatabases: PostgreSQL, MySQL, Redis\\nCore Competencies: RESTful API Development, Microservices Architecture, System Design"
            }
        """,
        "professional_experience": """
            Generate the Professional Experience section of a resume in JSON format.

            Instructions:
            1. For each role, extract and structure the following fields:
            - job_title
            - company_name
            - place (City, Country format preferred)
            - from_date (Month Year format if available)
            - to_date (Month Year or "Present")

            2. For the "description" field:
            - Combine all bullet points into a single string
            - Separate each bullet using \\n
            - Each bullet must start with "• "

            3. Bullet point rules:
            - Include 3–4 bullet points per role
            - Start with a strong heading followed by a colon
                (e.g., "Scalable Backend Architecture:", "API Integration:")
            - Clearly describe what was built, improved, or implemented
            - Mention technologies used (e.g., Python, Django, Docker)
            - Include measurable impact wherever possible
            - Focus on achievements, not responsibilities

            4. Writing style:
            - Use action verbs (Architected, Engineered, Developed, Optimized, Implemented)
            - Keep each bullet 1–2 lines max
            - Avoid repetition and generic phrases
            - No personal pronouns (I, We)

            5. Order:
            - Return roles in reverse chronological order

            6. Data Rules:
            - Do NOT hallucinate companies, roles, or metrics
            - Use only the provided data
            - If any field is missing, set it to null

            7. Job Alignment:
            - Prioritize and highlight experience relevant to the job description (if provided)

            8. Output Rules:
            - Return ONLY valid JSON
            - Follow the schema strictly
            - No extra text outside JSON

            Output Example:

            [
                {
                    "job_title": "Software Development Engineer",
                    "company_name": "Karaz Trading Company",
                    "place": "Riyadh, KSA",
                    "from_date": "February 2025",
                    "to_date": "Present",
                    "description": "• Scalable Fintech Architecture: Architected a Python/Django backend integrating payment gateways, increasing transaction volume by 25%.\\n• ERP Automation: Developed a Python/Flask tool reducing manual effort by 40+ hours weekly.\\n• DevOps Optimization: Implemented Docker and CI/CD pipelines, improving uptime to 99.9%."
                }
            ]
            """,
        "technical_projects":  """
            Generate the Technical Projects section of a resume in JSON format.

            Instructions:
            1. For each project, extract and structure:
            - project_name
            - description

            2. For "project_name":
            - Use the project title
            - Optionally include a short descriptor in parentheses if relevant

            3. For "description":
            - Combine all sections into a single string
            - Use \\n to separate each line
            - Follow this exact internal structure:

                • Tech Stack: technologies (comma-separated)  
                • Problem: 1 line describing the problem  
                • Action: 1–2 lines explaining implementation and approach  
                • Result: measurable outcome or impact  

            4. Content rules:
            - Include 1–3 projects (not more than 3)
            - Keep content concise and focused
            - Use only relevant and realistic data
            - Emphasize impact, scalability, and technical depth

            5. Writing style:
            - Use action verbs (Architected, Developed, Implemented, Designed)
            - No personal pronouns (I, We)
            - Avoid generic or vague statements
            - Ensure clarity and readability

            6. Data Rules:
            - Do NOT hallucinate project details or metrics
            - Use only the provided input
            - If any detail is missing, omit rather than fabricate

            7. Job Alignment:
            - Prioritize projects relevant to the job description (if provided)

            8. Output Rules:
            - Return ONLY valid JSON
            - Follow the schema strictly
            - No extra text outside JSON

            Output Example:

            [
                {
                    "project_name": "Karaz Cards Platform (B2B/B2C Fintech Ecosystem)",
                    "description": "• Tech Stack: Python, Django, PostgreSQL, Redis, Docker\\n• Problem: Required a secure and scalable system to manage digital voucher distribution.\\n• Action: Architected a multi-tenant backend using Django REST Framework and integrated secure authentication and payment systems.\\n• Result: Automated 10,000+ transactions with full traceability and zero security issues."
                }
            ]
        """,
        "education": """
            Generate the Education section of a resume in JSON format.

            Instructions:
            1. For each education entry, extract and structure:
            - degree_name
            - college_name
            - place (City, Country format preferred)
            - completed_on (Month Year format if available)
            - result (GPA / Percentage if provided)
            - description

            2. For the "description" field:
            - Combine additional details into a single string
            - Use \\n to separate each line
            - Include only relevant optional details such as:
                • Relevant Coursework  
                • Academic achievements or honors  
                • Certifications, equivalency, or credential status  

            3. Formatting rules (inside description):
            - Each line should start with "• "
            - Keep each point concise (1 line max)
            - Do not exceed 1–2 bullet points per entry

            4. Content rules:
            - Include GPA/percentage only if explicitly provided
            - Include coursework only if relevant to the role
            - Do NOT add assumptions or fabricate details
            - If no additional details exist, set description to null

            5. Order:
            - Return entries in reverse chronological order (most recent first)

            6. Writing style:
            - Professional and concise
            - No personal pronouns (I, We)
            - Avoid unnecessary text

            7. Data Rules:
            - Do NOT hallucinate missing information
            - Use only the provided input
            - Set missing fields to null where appropriate

            8. Output Rules:
            - Return ONLY valid JSON
            - Follow the schema strictly
            - No extra text outside JSON

            Output Example:

            [
                {
                    "degree_name": "Bachelor of Engineering (BE) in Computer Science",
                    "college_name": "The Oxford College of Engineering",
                    "place": "Bengaluru, India",
                    "completed_on": "June 2024",
                    "result": "GPA: 3.7 / 5.0",
                    "description": "• Relevant Coursework: Data Structures & Algorithms, Database Management Systems, Operating Systems, Cloud Computing\\n• Credential Status: Degree eligible for international equivalency and attestation"
                },
                {
                    "degree_name": "Senior Secondary (PCMC)",
                    "college_name": "Vijaya Composite Pre-University College",
                    "place": "Bengaluru, India",
                    "completed_on": "April 2020",
                    "result": "Percentage: 78.67%",
                    "description": null
                }
            ]
        """,
        "certifications": """
            Generate the Certifications section of a resume in JSON format.

            Instructions:
            1. For each certification, extract and structure:
            - title
            - issuing_company
            - completion_date (Month Year format if available)

            2. Content rules:
            - Include only relevant and recognized certifications
            - Do NOT add descriptions unless explicitly provided
            - Do NOT hallucinate certifications
            - Use only the provided input

            3. Formatting rules:
            - Maintain clean, professional structure
            - Do not use bullet points
            - List certifications in reverse chronological order (most recent first)

            4. Writing style:
            - Concise and professional
            - No personal pronouns
            - No extra text or explanations

            5. Output Rules:
            - Return ONLY valid JSON
            - Follow the schema strictly
            - No extra text outside JSON

            Output Example:

            [
                {
                    "title": "Career Essentials in Generative AI",
                    "issuing_company": "Microsoft & LinkedIn Learning",
                    "completion_date": "December 2023"
                }
            ]
        """
    }

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

    resume_schema = {
        "introduction":"""
    {
        "name": "string",
        "designation": "string",
        "place": "string",
        "emails": ["string"],
        "mobile_numbers": ["string"],
        "links": ["string"],
        "nationality": "string|null",
        "dob": "YYYY-MM-DD|null",
        "visa_status": "string|null",
        "notice_period": "string|null"
    }
    """,
        "professional_summary": "string|null",
        "technical_skills": "string|null",
        "professional_experience": """ [
        {
        "job_title": "string",
        "company_name": "string",
        "place": "string",
        "from_date": "string|null",
        "to_date": "string|null",
        "description": "string|null"
        }
    ]""",
        "technical_projects": """[
        {
        "project_name": "string",
        "description": "string|null"
        }
    ]""",
        "education": """
        [
        {
        "degree_name": "string",
        "college_name": "string",
        "place": "string",
        "completed_on": "string|null",
        "result": "string|null",
        "description": "string|null"
        }
    ]""",
        "certifications": """[
        {
        "title": "string",
        "issuing_company": "string",
        "completion_date": "string|null"
        }
    ]"""
    }


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



class PollinationsAI(BaseAI):
    
    url = "https://text.pollinations.ai/openai/v1/chat/completions"

    def __init__(self,  debug):
        self.debug = debug
        self.ai_model = "openai"
        # Initialize Pollinations-specific stuff here

    def generate(self, prompt: str) -> str:
        # Call Pollinations API
        return f"Pollinations response for: {prompt}"


    def generate_from_ai(self, jd: str, resume_content: str, part: str = "introduction", retries: int = 2) -> dict:

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

        payload = {
            "model": self.ai_model,
            "messages": [
                {"role": "system", "content": self.sys_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "max_tokens": 20000
        }

        for attempt in range(retries + 1):
            try:
                response = requests.post(self.url, json=payload, timeout=30)
                response.raise_for_status()
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
    def __init__(self, api_key):
        self.api_key = api_key
        # Initialize Groq AI-specific stuff here

    def generate(self, prompt: str) -> str:
        # Call Groq AI API
        return f"Groq AI response for: {prompt}"




class AI:

    url = "https://text.pollinations.ai/openai/v1/chat/completions"

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

    model = "openai"

    resume_parts_prompt = {
        "introduction":"""
            Generate the Introduction section of a resume in JSON format.

            Instructions:
            1. Extract and structure the candidate’s basic details from the input.
            2. Populate all fields strictly according to the provided schema.

            Field Guidelines:
            - name: Full name of the candidate
            - designation: Current role or target job title (aligned with job description if provided)
            - place: Current location (City, Country format preferred)
            - emails: List all valid email addresses
            - mobile_numbers: Include phone numbers with country code if available
            - links: Include relevant links (LinkedIn, GitHub, Portfolio, etc.)

            Optional Fields (set to null if not available):
            - nationality
            - dob (format: YYYY-MM-DD)
            - visa_status
            - notice_period

            3. Data Rules:
            - Do NOT hallucinate missing personal details
            - Do NOT leave required fields empty—use best available data
            - Normalize formatting (e.g., phone numbers, dates)
            - Remove duplicates in arrays

            4. Job Alignment:
            - If a job description is provided, align the designation accordingly

            5. Output Rules:
            - Return ONLY valid JSON
            - Follow the schema strictly
            - No extra text, explanations, or formatting outside JSON
        """,
        "professional_summary": """
            Generate the Professional Summary section of a resume in JSON format.

            Instructions:
            1. Write a single-paragraph professional summary (4–6 lines).
            2. The summary must include:
            - Total years of experience
            - Key skills and technologies
            - Major achievements or measurable impact
            - Industries or domains worked in
            - Career focus or goals

            3. Writing style:
            - Professional, concise, and results-oriented
            - ATS-friendly with relevant keywords
            - No bullet points (strictly one paragraph)
            - No personal pronouns (I, We)
            - Avoid generic phrases

            4. Job Alignment:
            - Tailor the summary to align with the provided job description (if available)

            5. Data Rules:
            - Do NOT hallucinate years of experience or achievements
            - Use only the provided data
            - Keep it realistic and relevant

            6. Output Rules:
            - Return ONLY valid JSON
            - Follow the schema strictly
            - No extra text outside JSON

            Output Example:

            "
            Dynamic Python Full-Stack Developer with 2+ years of experience specializing in the Django ecosystem to build robust, scalable web applications. 
            Expert in architecting high-performance backends using Django Rest Framework (DRF), integrated with AI solutions and MENA-specific fintech services. 
            Currently based in Riyadh with direct GCC market experience, including regional payment gateway integrations 
            (Tabby, Tamara, Tap) and automated data-sync tools for platforms like Noon. 
            Offering a strong cross-cultural perspective and a proven ability to lead full-stack projects—from responsive frontend development to containerized 
            Python deployments—within fast-paced, collaborative environments across the Middle East.
            "
        """,
        "technical_skills": """
            Generate the Technical Skills section of a resume in JSON format.

            Instructions:
            1. Identify and group skills into logical categories based on the input data.
            - Do NOT strictly rely on predefined categories.
            - Dynamically create appropriate categories such as (but not limited to):
                Programming Languages, Frameworks, Tools, Databases, Cloud, DevOps, Core Competencies, etc.
            - Only include categories that are relevant to the candidate.

            2. Formatting rules (inside the string output):
            - Each category should be written on a new line using \\n
            - Use this exact format per line:
                Category Name: skill1, skill2, skill3
            - Keep each category on a single line (no bullet points)
            - Use commas to separate skills
            - Maintain a clean, ATS-friendly structure

            3. Skill extraction rules:
            - Extract only relevant and realistic skills from the input
            - You may infer closely related skills if strongly implied
            - Do NOT include unrelated or generic terms
            - Avoid duplication across categories

            4. Proficiency:
            - Add proficiency levels only when clearly justified (e.g., Python (Advanced))

            5. Keep the output concise, well-organized, and professional

            6. Job Alignment:
            - Prioritize skills relevant to the provided job description (if available)

            7. Output Rules:
            - Return ONLY valid JSON
            - Follow the schema strictly
            - No extra text outside JSON

            Output Example:

            {
                "technical_skills": "Programming Languages: Python (Advanced), JavaScript, Java\\nFrameworks & Libraries: Django, Flask, React\\nTools & Platforms: Docker, Git, AWS\\nDatabases: PostgreSQL, MySQL, Redis\\nCore Competencies: RESTful API Development, Microservices Architecture, System Design"
            }
        """,
        "professional_experience": """
            Generate the Professional Experience section of a resume in JSON format.

            Instructions:
            1. For each role, extract and structure the following fields:
            - job_title
            - company_name
            - place (City, Country format preferred)
            - from_date (Month Year format if available)
            - to_date (Month Year or "Present")

            2. For the "description" field:
            - Combine all bullet points into a single string
            - Separate each bullet using \\n
            - Each bullet must start with "• "

            3. Bullet point rules:
            - Include 3–4 bullet points per role
            - Start with a strong heading followed by a colon
                (e.g., "Scalable Backend Architecture:", "API Integration:")
            - Clearly describe what was built, improved, or implemented
            - Mention technologies used (e.g., Python, Django, Docker)
            - Include measurable impact wherever possible
            - Focus on achievements, not responsibilities

            4. Writing style:
            - Use action verbs (Architected, Engineered, Developed, Optimized, Implemented)
            - Keep each bullet 1–2 lines max
            - Avoid repetition and generic phrases
            - No personal pronouns (I, We)

            5. Order:
            - Return roles in reverse chronological order

            6. Data Rules:
            - Do NOT hallucinate companies, roles, or metrics
            - Use only the provided data
            - If any field is missing, set it to null

            7. Job Alignment:
            - Prioritize and highlight experience relevant to the job description (if provided)

            8. Output Rules:
            - Return ONLY valid JSON
            - Follow the schema strictly
            - No extra text outside JSON

            Output Example:

            [
                {
                    "job_title": "Software Development Engineer",
                    "company_name": "Karaz Trading Company",
                    "place": "Riyadh, KSA",
                    "from_date": "February 2025",
                    "to_date": "Present",
                    "description": "• Scalable Fintech Architecture: Architected a Python/Django backend integrating payment gateways, increasing transaction volume by 25%.\\n• ERP Automation: Developed a Python/Flask tool reducing manual effort by 40+ hours weekly.\\n• DevOps Optimization: Implemented Docker and CI/CD pipelines, improving uptime to 99.9%."
                }
            ]
            """,
        "technical_projects":  """
            Generate the Technical Projects section of a resume in JSON format.

            Instructions:
            1. For each project, extract and structure:
            - project_name
            - description

            2. For "project_name":
            - Use the project title
            - Optionally include a short descriptor in parentheses if relevant

            3. For "description":
            - Combine all sections into a single string
            - Use \\n to separate each line
            - Follow this exact internal structure:

                • Tech Stack: technologies (comma-separated)  
                • Problem: 1 line describing the problem  
                • Action: 1–2 lines explaining implementation and approach  
                • Result: measurable outcome or impact  

            4. Content rules:
            - Include 1–3 projects (not more than 3)
            - Keep content concise and focused
            - Use only relevant and realistic data
            - Emphasize impact, scalability, and technical depth

            5. Writing style:
            - Use action verbs (Architected, Developed, Implemented, Designed)
            - No personal pronouns (I, We)
            - Avoid generic or vague statements
            - Ensure clarity and readability

            6. Data Rules:
            - Do NOT hallucinate project details or metrics
            - Use only the provided input
            - If any detail is missing, omit rather than fabricate

            7. Job Alignment:
            - Prioritize projects relevant to the job description (if provided)

            8. Output Rules:
            - Return ONLY valid JSON
            - Follow the schema strictly
            - No extra text outside JSON

            Output Example:

            [
                {
                    "project_name": "Karaz Cards Platform (B2B/B2C Fintech Ecosystem)",
                    "description": "• Tech Stack: Python, Django, PostgreSQL, Redis, Docker\\n• Problem: Required a secure and scalable system to manage digital voucher distribution.\\n• Action: Architected a multi-tenant backend using Django REST Framework and integrated secure authentication and payment systems.\\n• Result: Automated 10,000+ transactions with full traceability and zero security issues."
                }
            ]
        """,
        "education": """
            Generate the Education section of a resume in JSON format.

            Instructions:
            1. For each education entry, extract and structure:
            - degree_name
            - college_name
            - place (City, Country format preferred)
            - completed_on (Month Year format if available)
            - result (GPA / Percentage if provided)
            - description

            2. For the "description" field:
            - Combine additional details into a single string
            - Use \\n to separate each line
            - Include only relevant optional details such as:
                • Relevant Coursework  
                • Academic achievements or honors  
                • Certifications, equivalency, or credential status  

            3. Formatting rules (inside description):
            - Each line should start with "• "
            - Keep each point concise (1 line max)
            - Do not exceed 1–2 bullet points per entry

            4. Content rules:
            - Include GPA/percentage only if explicitly provided
            - Include coursework only if relevant to the role
            - Do NOT add assumptions or fabricate details
            - If no additional details exist, set description to null

            5. Order:
            - Return entries in reverse chronological order (most recent first)

            6. Writing style:
            - Professional and concise
            - No personal pronouns (I, We)
            - Avoid unnecessary text

            7. Data Rules:
            - Do NOT hallucinate missing information
            - Use only the provided input
            - Set missing fields to null where appropriate

            8. Output Rules:
            - Return ONLY valid JSON
            - Follow the schema strictly
            - No extra text outside JSON

            Output Example:

            [
                {
                    "degree_name": "Bachelor of Engineering (BE) in Computer Science",
                    "college_name": "The Oxford College of Engineering",
                    "place": "Bengaluru, India",
                    "completed_on": "June 2024",
                    "result": "GPA: 3.7 / 5.0",
                    "description": "• Relevant Coursework: Data Structures & Algorithms, Database Management Systems, Operating Systems, Cloud Computing\\n• Credential Status: Degree eligible for international equivalency and attestation"
                },
                {
                    "degree_name": "Senior Secondary (PCMC)",
                    "college_name": "Vijaya Composite Pre-University College",
                    "place": "Bengaluru, India",
                    "completed_on": "April 2020",
                    "result": "Percentage: 78.67%",
                    "description": null
                }
            ]
        """,
        "certifications": """
            Generate the Certifications section of a resume in JSON format.

            Instructions:
            1. For each certification, extract and structure:
            - title
            - issuing_company
            - completion_date (Month Year format if available)

            2. Content rules:
            - Include only relevant and recognized certifications
            - Do NOT add descriptions unless explicitly provided
            - Do NOT hallucinate certifications
            - Use only the provided input

            3. Formatting rules:
            - Maintain clean, professional structure
            - Do not use bullet points
            - List certifications in reverse chronological order (most recent first)

            4. Writing style:
            - Concise and professional
            - No personal pronouns
            - No extra text or explanations

            5. Output Rules:
            - Return ONLY valid JSON
            - Follow the schema strictly
            - No extra text outside JSON

            Output Example:

            [
                {
                    "title": "Career Essentials in Generative AI",
                    "issuing_company": "Microsoft & LinkedIn Learning",
                    "completion_date": "December 2023"
                }
            ]
        """
    }

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

    resume_schema = {
        "introduction":"""
    {
        "name": "string",
        "designation": "string",
        "place": "string",
        "emails": ["string"],
        "mobile_numbers": ["string"],
        "links": ["string"],
        "nationality": "string|null",
        "dob": "YYYY-MM-DD|null",
        "visa_status": "string|null",
        "notice_period": "string|null"
    }
    """,
        "professional_summary": "string|null",
        "technical_skills": "string|null",
        "professional_experience": """ [
        {
        "job_title": "string",
        "company_name": "string",
        "place": "string",
        "from_date": "string|null",
        "to_date": "string|null",
        "description": "string|null"
        }
    ]""",
        "technical_projects": """[
        {
        "project_name": "string",
        "description": "string|null"
        }
    ]""",
        "education": """
        [
        {
        "degree_name": "string",
        "college_name": "string",
        "place": "string",
        "completed_on": "string|null",
        "result": "string|null",
        "description": "string|null"
        }
    ]""",
        "certifications": """[
        {
        "title": "string",
        "issuing_company": "string",
        "completion_date": "string|null"
        }
    ]"""
    }

    def __init__(self, model: str, debug):
        self.debug = debug

        if model == "pollinations":
            self.model = PollinationsAI(self.debug)
        elif model == "groq":
            self.model = GroqAI()
        else:
            raise ValueError("Unsupported model")
        
    def switch_model(self, model: str, api_keys: dict):
        """Switch to a different AI backend on the fly"""
        if model == "pollinations":
            self.model = PollinationsAI(self.debug)
        elif model == "groq":
            self.model = GroqAI()
        else:
            raise ValueError("Unsupported model")


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

    def generate_from_ai(self, jd: str, resume_content: str, part: str = "introduction", retries: int = 2) -> dict:
                

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

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.sys_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "max_tokens": 20000,

        }

        for attempt in range(retries + 1):
            try:
                response = requests.post(self.url, json=payload, timeout=30)
                response.raise_for_status()
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
        resume = AI()

        resume_content = resume_data['experience']
        
        result = resume.generate_from_ai(jd = jd, part="professional_experience", resume_content=resume_content)
        
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


