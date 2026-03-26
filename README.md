# AI-Resume-Builder

AI-powered, ATS-friendly resume builder built with Flask. Users enter structured data and get a clean, job-description-specific, ATS-optimized resume exported as a Word document (DOCX).

---

## Overview

**AI-Resume-Builder** helps candidates quickly generate professional resumes tailored for Applicant Tracking Systems (ATS) using a simple web interface. Unlike generic resumes, it creates job-description-specific resumes that closely align with target roles while remaining ATS-friendly.

---

## Project Motivation

In today’s competitive job market, even highly capable candidates often don’t get selected for interviews. While digging deeper, I discovered that many resumes are filtered out by **Applicant Tracking Systems (ATS)** before a human ever sees them.  

Even ATS-friendly resumes can fail to stand out because they are **generic** and don’t match the specific **Job Description (JD)** of the role being applied for. I wanted to create resumes that are **both ATS-compliant and JD-tailored**.  

However, tailoring resumes manually for each JD is time-consuming, especially when applying to multiple companies with different requirements.  

Then I learned about **Python libraries for generating Word documents** and AI model providers like **Pollinations, Groq, and Hugging Face** (which offer free tiers).  

This inspired me to develop **AI-Resume-Builder**, a tool that generates **JD-specific, ATS-friendly resumes quickly and efficiently**. And here it is!

---

## Tech Stack

- **Backend:** Python 3.x, Flask  
- **Frontend:** HTML5, CSS3, jQuery  
- **Storage:** IndexedDB (browser-side storage for resumes)  
- **Resume Export:** python-docx  
- **AI Providers:** Pollinations, Groq, Hugging Face  

---

## Frontend Pages & UX

### Home Page – Resume Dashboard
- Displays all resumes stored in IndexedDB.
- Provides **View, Edit, Select, Delete** actions for each resume.
- Supports multiple resume variants (different roles, regions, experience focus).

### Index Page – JD → DOCX Generation
- Select a saved resume.
- Paste the target Job Description (JD).
- Submit to generate a JD-specific, ATS-optimized resume as a DOCX.

### Create / Edit Resume Page – Structured Form
- Sections include:
  - Introduction & contact details
  - Professional summary
  - Technical skills
  - Professional experience
  - Technical projects
  - Education
  - Certifications
- Dynamic addition/removal of repeated items.
- Client-side validation and IndexedDB storage for offline-friendly editing.

---

## Backend & AI Pipeline

- **Flask** backend handles resume processing and DOCX generation.
- On submission:
  1. The resume metadata is transformed into a structured internal object.
  2. Passed to the chosen AI provider (Pollinations, Groq, Hugging Face) along with the JD.
  3. AI generates section-wise structured JSON.
  4. JSON is merged into a unified resume object.
  5. `python-docx` generates an ATS-friendly Word document on the fly.
- Direct DOCX download without intermediate server storage.

---

## Data Storage

- Resume records are stored **entirely in the browser** using IndexedDB.
- Benefits:
  - Privacy: raw data never leaves the user’s device.
  - Offline support: resumes remain editable without internet.
  - Backend fetches resume on demand for DOCX generation.

---

## ATS Considerations

- Clear, standard sections for better ATS parsing.
- Keyword-rich, concise descriptions aligned with JD.
- Avoids complex tables, graphics, and non-text elements.

---

## Getting Started

### Prerequisites

- Python 3.x  
- pip  
- (Optional) venv / virtualenv  

### Installation

```bash
git clone https://github.com/bhuvaneshp2407/AI-Resume-Builder.git
cd AI-Resume-Builder

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate , Change for other operating systems

pip install -r requirements.txt
```

### Create a `.env` File

Create a `.env` file in the project root and add your API keys and environment settings:

```text
FLASK_ENV=development
SECRET_KEY=your-secret-key
POLLINATIONS_API_KEY=your-pollinations-key
GROQ_API_KEY=your-groq-key
HUGGING_FACE_API_KEY=your-hf-key
```

### Run Locally

```bash
flask run
# or
python main.py
```

### Open your browser:

```
http://127.0.0.1:5000/
```

---

### Usage
- Go to Create Resume and fill out all sections.
- Save the resume; it appears on the Home page (IndexedDB).
- Select a resume to use.
- On the Index page, paste the target JD.
- Choose an AI provider (Pollinations, Groq, or Hugging Face).
- Click Generate Resume to download the JD-specific DOCX.


### Roadmap
- Add multiple ATS-safe visual templates.
- Introduce ATS score / keyword matching based on JD.
- Support PDF export in addition to DOCX.
- Optional cloud sync for cross-device access.
- Add authentication and user accounts.

### Contributing

Contributions are welcome:

- Fork the repository.
- Create a feature branch: git checkout -b feature/your-feature.
- Commit your changes: git commit -m "Add your feature".
- Push to the branch: git push origin feature/your-feature.
- Open a Pull Request.

This is a personal project; external contributions are optional.

---

## License

MIT License © 2026 **Bhuvanesh Pranesh Acharya**