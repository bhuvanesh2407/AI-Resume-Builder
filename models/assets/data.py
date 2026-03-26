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

dict_data = {
    "resume_prompts": resume_parts_prompt,
    "resume_schema" : resume_schema
}

def build_json_file(dict_data: dict, file_name: str):
    import json
    with open("models/assets/resume_prompts.json", "w") as json_file:
        json.dump(dict_data[file_name], json_file, indent=4, default=str)
        print(f"Dictionary successfully updated \nFile Name: {file_name}.json ")

build_json_file(dict_data=dict_data, file_name="resume_prompts")
