import tempfile
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from fastapi import HTTPException

def generate_pdf_report(match_score, matched_keywords, missing_keywords, resume_name="Resume", job_role="Job Role"):
    try:
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

        return temp_file.name
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")
