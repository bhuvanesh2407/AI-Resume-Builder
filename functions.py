from models.resume_generator import ResumeGenerator
import json
from models.resume import Resume
from models.word_document import PageSize, PageMargin, WordDoc, ResumeBuilder
from docx.shared import Inches, Cm
import uuid

def generate_ai_resume(generator: ResumeGenerator, resume_obj: Resume):
    generator.generate_introduction(resume_obj=resume_obj)
    generator.generate_professional_summary(resume_obj=resume_obj)
    generator.generate_technical_skills(resume_obj=resume_obj)
    generator.generate_professional_experience(resume_obj=resume_obj)
    generator.generate_technical_projects(resume_obj=resume_obj)
    generator.generate_education(resume_obj=resume_obj)
    generator.generate_certifications(resume_obj=resume_obj)

    return generator


def build_word_doc(resume_obj: Resume,  debug: bool = False):
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

    doc_name = uuid.uuid4().hex
    document.save(f"sample_doc/{doc_name}.docx")

    return f"sample_doc/{doc_name}.docx"