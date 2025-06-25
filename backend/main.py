from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import uuid
from parser import extract_text_from_pdf, extract_text_from_docx
from matcher import compare_resume_job_keywords
from report_generator import generate_pdf_report

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

        pdf_path = generate_pdf_report(match_score, matched_keywords, missing_keywords, resume_name, job_role)

        def iterfile():
            with open(pdf_path, "rb") as f:
                yield from f

        headers = {
            "Content-Disposition": f"attachment; filename=ATS_Report_{resume_name.replace(' ', '_')}.pdf"
        }
        return StreamingResponse(iterfile(), media_type="application/pdf", headers=headers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")
