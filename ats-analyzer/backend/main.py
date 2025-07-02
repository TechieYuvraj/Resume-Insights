from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uuid
import logging

from matcher import compare_resume_job_keywords, generate_detailed_report, extract_keywords
from parser import extract_text_from_pdf, extract_text_from_docx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Allow CORS from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# In-memory storage for session data
session_storage = {}

def get_session_id(x_session_id: str = Header(None)) -> str:
    """Returns the session ID from the header or creates a new one."""
    return x_session_id if x_session_id and x_session_id in session_storage else str(uuid.uuid4())

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...), x_session_id: str = Header(None)):
    """Handles resume upload, text extraction, and session management."""
    session_id = get_session_id(x_session_id)
    
    try:
        file_bytes = await file.read()
        if file.content_type == "application/pdf":
            text = extract_text_from_pdf(file_bytes)
        elif file.content_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
            text = extract_text_from_docx(file_bytes)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload PDF or DOCX.")
        
        if session_id not in session_storage:
            session_storage[session_id] = {}
        
        session_storage[session_id]["resume_text"] = text
        logger.info(f"Resume uploaded for session {session_id}. Text length: {len(text)}")
        
        return JSONResponse(content={"extracted_text": text, "session_id": session_id})
    except Exception as e:
        logger.error(f"Error uploading resume for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to process resume.")

@app.post("/submit-job")
async def submit_job(description: str = Form(...), x_session_id: str = Header(None)):
    """Receives job description and stores it in the session."""
    if not x_session_id or x_session_id not in session_storage:
        raise HTTPException(status_code=400, detail="Invalid or missing session ID. Please upload resume first.")
    
    session_storage[x_session_id]["job_description"] = description
    logger.info(f"Job description submitted for session {x_session_id}. Length: {len(description)}")
    
    return JSONResponse(content={"message": "Job description received successfully", "session_id": x_session_id})

@app.post("/match-score")
async def match_score(x_session_id: str = Header(None)):
    """Calculates and returns the match score between resume and job description."""
    if not x_session_id or x_session_id not in session_storage:
        raise HTTPException(status_code=400, detail="Invalid session ID.")

    session_data = session_storage[x_session_id]
    resume_text = session_data.get("resume_text")
    job_description = session_data.get("job_description")

    if not resume_text or not job_description:
        raise HTTPException(status_code=400, detail="Resume and job description must be submitted.")

    result = compare_resume_job_keywords(resume_text, job_description)
    return JSONResponse(content=result)

@app.post("/detailed-report")
async def detailed_report(x_session_id: str = Header(None)):
    """Generates and returns a detailed report."""
    if not x_session_id or x_session_id not in session_storage:
        raise HTTPException(status_code=400, detail="Invalid session ID.")

    session_data = session_storage[x_session_id]
    resume_text = session_data.get("resume_text")
    job_description = session_data.get("job_description")

    if not resume_text or not job_description:
        raise HTTPException(status_code=400, detail="Resume and job description must be submitted.")

    report = generate_detailed_report(resume_text, job_description)
    return JSONResponse(content=report)

@app.get("/keywords")
async def get_keywords(x_session_id: str = Header(None)):
    """Returns extracted keywords from the resume and job description."""
    if not x_session_id or x_session_id not in session_storage:
        raise HTTPException(status_code=400, detail="Invalid session ID.")

    session_data = session_storage[x_session_id]
    resume_text = session_data.get("resume_text", "")
    job_description = session_data.get("job_description", "")

    resume_keywords = sorted(list(extract_keywords(resume_text)))
    job_keywords = sorted(list(extract_keywords(job_description)))

    return JSONResponse(content={
        "resume_keywords": resume_keywords,
        "job_keywords": job_keywords
    })