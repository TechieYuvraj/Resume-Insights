from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import pdfplumber
import docx
import io
import re
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import tempfile
import json

app = FastAPI()

# Allow CORS from all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for resume text and job description per session
session_storage = {}

def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
            return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing PDF file: {str(e)}")

def extract_text_from_docx(file_bytes: bytes) -> str:
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing DOCX file: {str(e)}")

import string

# Common English stopwords list
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at",
    "be", "because", "been", "before", "being", "below", "between", "both", "but", "by",
    "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each",
    "few", "for", "from", "further",
    "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's",
    "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself",
    "let's",
    "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not",
    "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own",
    "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too",
    "under", "until", "up",
    "very",
    "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't",
    "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"
}

def extract_keywords(text: str) -> set:
    # Tokenize text, remove punctuation, lowercase, remove stopwords and short words
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    words = re.findall(r'\b\w{3,}\b', text)
    keywords = set(word for word in words if word not in STOPWORDS)
    return keywords

def compare_resume_job_keywords(resume_text: str, job_description: str) -> dict:
    resume_keywords = extract_keywords(resume_text)
    job_keywords = extract_keywords(job_description)

    matched_keywords = list(resume_keywords.intersection(job_keywords))
    missing_keywords = list(job_keywords.difference(resume_keywords))

    match_score_value = 0
    if job_keywords:
        match_score_value = int(len(matched_keywords) / len(job_keywords) * 100)

    return {
        "match_score": match_score_value,
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords
    }

from fastapi import Header
import uuid

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...), x_session_id: str = Header(None)):
    if not x_session_id:
        x_session_id = str(uuid.uuid4())
    if file.content_type == "application/pdf":
        file_bytes = await file.read()
        text = extract_text_from_pdf(file_bytes)
    elif file.content_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
        file_bytes = await file.read()
        text = extract_text_from_docx(file_bytes)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type. Please upload PDF or DOCX.")
    if x_session_id not in session_storage:
        session_storage[x_session_id] = {"resume_text": "", "job_description": ""}
    session_storage[x_session_id]["resume_text"] = text
    return {"extracted_text": text, "session_id": x_session_id}

@app.post("/submit-job")
async def submit_job(description: str = Form(...), x_session_id: str = Header(None)):
    if not x_session_id or x_session_id not in session_storage:
        raise HTTPException(status_code=400, detail="Invalid or missing session ID. Please upload resume first.")
    session_storage[x_session_id]["job_description"] = description
    return {"message": "Job description received successfully", "description_length": len(description), "session_id": x_session_id}

@app.post("/match-score")
async def match_score(x_session_id: str = Header(None)):
    if not x_session_id or x_session_id not in session_storage:
        raise HTTPException(status_code=400, detail="Invalid or missing session ID. Please upload resume and submit job description first.")
    resume_text = session_storage[x_session_id].get("resume_text", "")
    job_description = session_storage[x_session_id].get("job_description", "")
    if not resume_text or not job_description:
        raise HTTPException(status_code=400, detail="Both resume and job description must be submitted before matching.")

    result = compare_resume_job_keywords(resume_text, job_description)
    return JSONResponse(content=result)

@app.post("/generate-report")
async def generate_report(request: Request):
    try:
        data = await request.json()
        match_score = data.get("match_score")
        matched_keywords = data.get("matched_keywords", [])
        missing_keywords = data.get("missing_keywords", [])
        resume_name = data.get("resume_name", "Resume")
        job_role = data.get("job_role", "Job Role")

        # Create a temporary file for the PDF
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        c = canvas.Canvas(temp_file.name, pagesize=letter)
        width, height = letter

        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(1 * inch, height - 1 * inch, "ATS Resume Analysis Report")

        # Resume name and job role
        c.setFont("Helvetica", 12)
        c.drawString(1 * inch, height - 1.5 * inch, f"Resume: {resume_name}")
        c.drawString(1 * inch, height - 1.8 * inch, f"Job Role: {job_role}")

        # Match score
        c.drawString(1 * inch, height - 2.2 * inch, f"Match Score: {match_score}%")

        # Matched keywords
        c.drawString(1 * inch, height - 2.6 * inch, "Matched Keywords:")
        text = c.beginText(1.2 * inch, height - 2.9 * inch)
        text.setFont("Helvetica", 10)
        for kw in matched_keywords:
            text.textLine(f"- {kw}")
        c.drawText(text)

        # Missing keywords
        y_position = height - 2.9 * inch - 12 * len(matched_keywords) - 20
        c.drawString(1 * inch, y_position, "Missing Keywords:")
        text = c.beginText(1.2 * inch, y_position - 20)
        text.setFont("Helvetica", 10)
        for kw in missing_keywords:
            text.textLine(f"- {kw}")
        c.drawText(text)

        # Suggestions for improvement
        y_position = y_position - 20 - 12 * len(missing_keywords) - 20
        c.drawString(1 * inch, y_position, "Suggestions for Improvement:")
        text = c.beginText(1.2 * inch, y_position - 20)
        text.setFont("Helvetica", 10)
        if match_score is not None and match_score < 70:
            text.textLine("Consider including more relevant keywords from the job description in your resume.")
        else:
            text.textLine("Your resume matches well with the job description.")
        c.drawText(text)

        c.showPage()
        c.save()

        # Return the PDF file as a streaming response
        def iterfile():
            with open(temp_file.name, "rb") as f:
                yield from f

        headers = {
            "Content-Disposition": f"attachment; filename=ATS_Report_{resume_name.replace(' ', '_')}.pdf"
        }
        return StreamingResponse(iterfile(), media_type="application/pdf", headers=headers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")
