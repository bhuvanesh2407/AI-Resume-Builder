from flask import Flask, render_template, request, send_file, jsonify,after_this_request
from models.resume import *
import re
from datetime import datetime
from bin.ai_generation import generate_ai_resume
from models.resume_generator import ResumeGenerator
from functions import generate_ai_resume, build_word_doc
import os
import threading
import time

app = Flask(__name__)

debug = True

@app.route('/')
def index():
    # This will be your form page for user to input resume data
    return render_template('index.html')

def extract_simple_list(form, prefix):
    """Extract simple list fields like emails[0], emails[1]"""
    values = []
    pattern = re.compile(rf"{prefix}\[\d+\]")
    for key in form.keys():
        if pattern.match(key):
            values.append(form.get(key))
    return values


def extract_nested_list(form, prefix, fields):
    """
    Extract nested objects like:
    experience[0][job_title]
    experience[0][company_name]
    """
    data = {}
    pattern = re.compile(rf"{prefix}\[(\d+)\]\[(.+)\]")

    for key in form.keys():
        match = pattern.match(key)
        if match:
            index = int(match.group(1))
            field = match.group(2)

            if index not in data:
                data[index] = {}

            data[index][field] = form.get(key)

    return [data[i] for i in sorted(data.keys())]


@app.route('/build-resume', methods=['POST'])
def build_resume():

    form = request.form

    # simple lists
    emails = extract_simple_list(form, "emails")
    mobiles = extract_simple_list(form, "mobile_numbers")
    links = extract_simple_list(form, "links")

    # nested objects
    experiences_data = extract_nested_list(form, "experience", [])
    projects_data = extract_nested_list(form, "projects", [])
    education_data = extract_nested_list(form, "education", [])
    certifications_data = extract_nested_list(form, "certifications", [])

    experiences = [
        ProfessionalExperience(**exp)
        for exp in experiences_data
    ]

    projects = [
        TechnicalProject(**proj)
        for proj in projects_data
    ]

    education = [
        Education(**edu)
        for edu in education_data
    ]

    certifications = [
        Certification(**cert)
        for cert in certifications_data
    ]

    dob = form.get("dob")
    dob_parsed = datetime.strptime(dob, "%Y-%m-%d").date() if dob else None

    resume = Resume(
        name=form.get("name"),
        designation=form.get("designation"),
        place=form.get("place"),
        nationality=form.get("nationality"),
        dob=dob_parsed,
        visa_status=form.get("visa_status"),
        notice_period=form.get("notice_period"),
        profile_description=form.get("profile_description"),
        professional_summary=form.get("professional_summary"),
        technical_skills=form.get("technical_skills"),
        emails=emails,
        mobile_numbers=mobiles,
        links=links
    )

    data = {
        "resume": resume,
        "experiences": experiences,
        "projects": projects,
        "education": education,
        "certifications": certifications
    }

    print(data)

    return jsonify({
        "message": "Resume captured successfully",
        "data": data
    })


@app.route('/create-resume')
def create_resume():
    return render_template('create-resume.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/generate-resume', methods=['POST'])
def generate_resume():
    # Get form data
    job_description = request.form.get("jobDescription", "")
    resume_json_str = request.form.get("resumeData", "{}")  # default to empty JSON

    # Convert resumeData string to Python dict
    try:
        resume_pre_data = json.loads(resume_json_str)
    except json.JSONDecodeError:
        resume_data = {}
        print("Warning: resumeData is not valid JSON")



    # 🔥 Call your AI function
    try:
        doc_name=str(resume_pre_data['name'] + "_Resume")
        resume_obj = Resume(name="", designation="", place="")
        generator = ResumeGenerator(model="groq",resume_data=resume_pre_data, jd=job_description, debug=debug)

        generator = generate_ai_resume(generator=generator, resume_obj=resume_obj)

        word_doc = build_word_doc(resume_obj=resume_obj, doc_name=doc_name, debug=True)


        response = send_file(
            word_doc,
            as_attachment=True,
            download_name=doc_name+".docx",
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        # 🔥 Delete file AFTER response is sent
        def delete_file_later(path, delay=5):
            def task():
                time.sleep(delay)
                try:
                    if os.path.exists(path):
                        os.remove(path)
                        print("Deleted:", path)
                except Exception as e:
                    print("Error deleting file:", e)

            threading.Thread(target=task, daemon=True).start()
        

        # 👇 schedule deletion
        delete_file_later(path=word_doc, delay=20)

        return response

    except Exception as e:
        print("AI Error:", str(e))
        

    # Keep response SAME as requested
    # return jsonify({
    #     "status": "success",
    #     "Job Description": job_description
    # })

if __name__ == '__main__':
    app.run(debug=True)