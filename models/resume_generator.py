import json
from .ai import AI
import requests
import time
from .resume import Resume, ProfessionalExperience, TechnicalProject, Education, Certification

class ResumeGenerator:
    def __init__(self, model, resume_data, jd, max_retries=5, backoff_factor=2, debug = False):
        self.resume_data = resume_data
        self.jd = jd
        self.ai = AI(model=model, debug=debug)  # Instantiate once, use in all methods
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.debug = debug


    def normalise_data(self, result, part):
        if isinstance(result, dict):
            pe = result.get(part)

            if pe is None:
                # If key missing, wrap whole dict
                result = {part: [result]}
            elif isinstance(pe, dict):
                # If value is a dict, wrap in a list
                result[part] = [pe]
            elif isinstance(pe, list):
                # Already correct, do nothing
                pass
            else:
                # If some other type, wrap in a list
                result[part] = [pe]

        elif isinstance(result, list):
            # If input is a list, wrap it as value of the key
            result = {part: result}

        else:
            # For any other type, wrap in a list inside the key
            result = {"professional_experience": [result]}

        return result

    def _call_ai_with_retry(self, part, resume_content):
        """Call AI API with retry logic for 429 errors"""
        retries = 0
        wait_time = 10  # initial wait time in seconds
        while retries < self.max_retries:
            try:
                result = self.ai.model.generate_from_ai(jd=self.jd, part=part, resume_content=resume_content)
                return result
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    if self.debug:
                        print(f"⚠️ Rate limit hit. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    wait_time *= self.backoff_factor  # exponential backoff
                    retries += 1
                else:
                    raise  # re-raise other HTTP errors
        raise Exception("🚨 Max retries reached. API still returning 429.")

    def _pretty_print(self, result, part):
        """Helper method to pretty print JSON results"""
        if result and self.debug:
            print(f"""\n✅ Generated {part} section of the resume JSON:\n""")
            print(json.dumps(result, indent=4) if isinstance(result, dict) else result)

    def generate_introduction(self, resume_obj: Resume):
        keys = [
            'designation', 'dob', 'emails', 'links', 
            'mobile_numbers', 'name', 'nationality', 
            'notice_period', 'place', 'visa_status'
        ]
        resume_content = {key: self.resume_data.get(key) for key in keys}
        result = self._call_ai_with_retry(part="introduction", resume_content=resume_content)
        
        resume_obj.name = result['name']
        resume_obj.place = result['place']
        resume_obj.designation = result['designation']
        resume_obj.emails = result['emails']
        resume_obj.mobile_numbers = result['mobile_numbers']
        resume_obj.links = result['links']
        resume_obj.nationality = result['nationality']
        resume_obj.dob = result['dob']
        resume_obj.visa_status = result['visa_status']
        resume_obj.notice_period = result['notice_period']
        resume_obj.dob = result['dob']
        self._pretty_print(result, "introduction")
        return result

    def generate_professional_summary(self, resume_obj: Resume):
        resume_content = self.resume_data.get('professional_summary')
        result = self._call_ai_with_retry(part="professional_summary", resume_content=resume_content)
        
        # Store result in the Resume object
        resume_obj.professional_summary = result['professional_summary']
        self._pretty_print(result, "Professional Summary")
        return result

    def generate_technical_skills(self, resume_obj: Resume):
        resume_content = self.resume_data.get('technical_skills')
        result = self._call_ai_with_retry(part="technical_skills", resume_content=resume_content)
        
        # Store result in the Resume object
        resume_obj.technical_skills = result['technical_skills']
        self._pretty_print(result, "Technical Skills")
        return result

    def generate_professional_experience(self, resume_obj: Resume):
        resume_content = self.resume_data.get('experience')
        result = self._call_ai_with_retry(part="professional_experience", resume_content=resume_content)
        
        # if isinstance(result, dict):
        #     if 'professional_experience' not in result:
        #         result = {"professional_experience": [result]}
        #     elif isinstance(result.get('professional_experience'), dict):
        #         result['professional_experience'] = [result['professional_experience']]

        # elif isinstance(result, list):
        #     result = {"professional_experience": result}

        result = self.normalise_data(part="professional_experience", result=result)
        
        # if isinstance(result['professional_experience'], dict):
        #     result['professional_experience'] = [result['professional_experience']]
        self._pretty_print(result, "Professional Experience")
        # Store result in the Resume object
        resume_obj.professional_experience = [ProfessionalExperience(**job) for job in result['professional_experience']] 
        return result

    def generate_technical_projects(self, resume_obj: Resume):
        resume_content = self.resume_data.get('projects')
        result = self._call_ai_with_retry(part="technical_projects", resume_content=resume_content)
        
        result = self.normalise_data(part="technical_projects", result=result)
        self._pretty_print(result, "Technical Projects")
        # Store result in the Resume object
        resume_obj.technical_projects = [TechnicalProject(project_name=project["project_name"], description=project["description"]) for project in result['technical_projects']]
        
        return result

    def generate_education(self, resume_obj: Resume):
        resume_content = self.resume_data.get('education')
        result = self._call_ai_with_retry(part="education", resume_content=resume_content)
        
        result = self.normalise_data(part="education", result=result)
        self._pretty_print(result, "Certifications")
        resume_obj.education = [Education(**degree) for degree in result['education']]
        
        return result
    
    def generate_certifications(self, resume_obj: Resume):
        resume_content = self.resume_data.get('certifications')
        result = self._call_ai_with_retry(part="certifications", resume_content=resume_content)
        result = self.normalise_data(part="certifications", result=result)
        # Store result in the Resume object
        resume_obj.certifications = [Certification(**certificate) for certificate in result['certifications']]
        self._pretty_print(result, "Certifications")
        return result
    


if __name__ == "__main__":
    # Sample Job Description
    jd = """
    We are looking for a Python Developer with experience in REST APIs,
    FastAPI, and cloud platforms like AWS. Candidate should have strong
    problem-solving skills and experience with SQL and microservices.
    """

    with open('models/test/test.json', 'r') as file:
        data = json.load(file)  # This reads the JSON into a Python dictionary/list



    resume_obj = Resume(name="", designation="", place="")
    generator = ResumeGenerator(model="pollinations", resume_data=data, jd=jd, debug=True)

    resume_data = []

    resume_data.append(generator.generate_introduction(resume_obj=resume_obj))
    resume_data.append(generator.generate_professional_summary(resume_obj=resume_obj))
    resume_data.append(generator.generate_technical_skills(resume_obj=resume_obj))
    resume_data.append(generator.generate_professional_experience(resume_obj=resume_obj))
    resume_data.append(generator.generate_technical_projects(resume_obj=resume_obj))
    resume_data.append(generator.generate_education(resume_obj=resume_obj))
    resume_data.append(generator.generate_certifications(resume_obj=resume_obj))

    if generator.debug:
        print("Stored in Resume object:", resume_obj.professional_summary)
        print("Stored in Resume object:", resume_obj.technical_skills)
        print("Stored in Resume object:", resume_obj.professional_experience)
        print("Stored in Resume object:", resume_obj.technical_projects)
        print("Stored in Resume object:", resume_obj.education)
        print("Stored in Resume object:", resume_obj.certifications)
        # print(resume_data)

