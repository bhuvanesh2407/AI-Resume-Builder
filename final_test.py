from models.resume_generator import ResumeGenerator
import json
from models.resume import Resume
from models.word_document import PageSize, PageMargin, WordDoc, ResumeBuilder
from docx.shared import Inches, Cm


debug = True

# Sample Job Description
jd = """
We are looking for a Python Developer with experience in REST APIs,
FastAPI, and cloud platforms like AWS. Candidate should have strong
problem-solving skills and experience with SQL and microservices.
"""

with open('models/test/test.json', 'r') as file:
    resume_pre_data = json.load(file)  # This reads the JSON into a Python dictionary/list


resume_obj = Resume(name="", designation="", place="")
generator = ResumeGenerator(model="pollinations", resume_data=resume_pre_data, jd=jd, debug=debug)



generator.generate_introduction(resume_obj=resume_obj)
generator.generate_professional_summary(resume_obj=resume_obj)
generator.generate_technical_skills(resume_obj=resume_obj)
generator.generate_professional_experience(resume_obj=resume_obj)
generator.generate_technical_projects(resume_obj=resume_obj)
generator.generate_education(resume_obj=resume_obj)
generator.generate_certifications(resume_obj=resume_obj)



if debug:
    print("Stored in Resume object (professional_summary):", resume_obj.professional_summary)
    print("Stored in Resume object (technical_skills):", resume_obj.technical_skills)
    print("Stored in Resume object (professional_experience):", resume_obj.professional_experience)
    print("Stored in Resume object (technical_projects):", resume_obj.technical_projects)
    print("Stored in Resume object (education):", resume_obj.education)
    print("Stored in Resume object (certifications):", resume_obj.certifications)



# A4 size
page_size = PageSize(Inches(8.27), Inches(11.69))

# Margins in cm
page_margin = PageMargin(top=0.5, bottom=1, left=0.5, right=0.5)

document = WordDoc(page_size, page_margin, font_name="Helvetica", debug=debug)

resume = ResumeBuilder(document, debug=debug)

resume.build_name(resume_obj.name)
resume.build_designation(resume_obj.designation)

resume.build_personal_details(
        place=resume_obj.place,
        emails=resume_obj.emails,
        phone_numbers=resume_obj.mobile_numbers,
        links=resume_obj.links,
        nationality=resume_obj.nationality,
        dob=resume_obj.dob,
        visa_status=resume_obj.visa_status,
        notice_period=resume_obj.notice_period
    )

resume.build_professional_summary(
    resume_obj.professional_summary)
    
resume.build_technical_skills(resume_obj.technical_skills)

resume.build_professional_experience(resume_obj.professional_experience)

resume.build_technical_projects(resume_obj.technical_projects)

resume.build_education(resume_obj.education)

resume.build_certifications(resume_obj.certifications)


document.save("sample_doc/output_test_1.docx")