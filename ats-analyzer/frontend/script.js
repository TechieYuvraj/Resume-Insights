const uploadBtn = document.getElementById('upload-btn');
const resumeFileInput = document.getElementById('resume-file');
const uploadStatus = document.getElementById('upload-status');

const jobDescriptionSection = document.getElementById('job-description-section');
const jobDescriptionInput = document.getElementById('job-description');
const submitJobBtn = document.getElementById('submit-job-btn');
const jobStatus = document.getElementById('job-status');

const matchScoreSection = document.getElementById('match-score-section');
const matchScoreDisplay = document.getElementById('match-score');
const generateReportBtn = document.getElementById('generate-report-btn');
const reportStatus = document.getElementById('report-status');

let sessionId = null;
let currentMatchScore = null;
let currentMatchedKeywords = [];
let currentMissingKeywords = [];

uploadBtn.addEventListener('click', async () => {
    if (!resumeFileInput.files.length) {
        uploadStatus.textContent = 'Please select a resume file to upload.';
        return;
    }
    const file = resumeFileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);

    uploadStatus.textContent = 'Uploading...';

    try {
        const response = await fetch('http://127.0.0.1:8000/upload-resume', {
            method: 'POST',
            body: formData,
        });
        const data = await response.json();
        if (response.ok) {
            uploadStatus.textContent = 'Resume uploaded successfully.';
            sessionId = data.session_id;
            jobDescriptionSection.style.display = 'block';
        } else {
            uploadStatus.textContent = `Error: ${data.detail || 'Upload failed.'}`;
        }
    } catch (error) {
        uploadStatus.textContent = `Error: ${error.message}`;
    }
});

submitJobBtn.addEventListener('click', async () => {
    const description = jobDescriptionInput.value.trim();
    if (!description) {
        jobStatus.textContent = 'Please enter a job description.';
        return;
    }
    jobStatus.textContent = 'Submitting job description...';

    try {
        const formData = new FormData();
        formData.append('description', description);

        const response = await fetch('http://127.0.0.1:8000/submit-job', {
            method: 'POST',
            headers: {
                'x-session-id': sessionId,
            },
            body: formData,
        });
        const data = await response.json();
        if (response.ok) {
            jobStatus.textContent = 'Job description submitted successfully.';
            matchScoreSection.style.display = 'block';
            await fetchMatchScore();
        } else {
            jobStatus.textContent = `Error: ${data.detail || 'Submission failed.'}`;
        }
    } catch (error) {
        jobStatus.textContent = `Error: ${error.message}`;
    }
});

async function fetchMatchScore() {
    matchScoreDisplay.textContent = 'Calculating match score...';
    try {
        const response = await fetch('http://127.0.0.1:8000/match-score', {
            method: 'POST',
            headers: {
                'x-session-id': sessionId,
            },
        });
        const data = await response.json();
        if (response.ok) {
            currentMatchScore = data.match_score !== undefined ? data.match_score : null;
            currentMatchedKeywords = data.matched_keywords || [];
            currentMissingKeywords = data.missing_keywords || [];
            matchScoreDisplay.textContent = `Match Score: ${currentMatchScore !== null ? currentMatchScore : 'N/A'}`;
        } else {
            matchScoreDisplay.textContent = `Error: ${data.detail || 'Failed to get match score.'}`;
        }
    } catch (error) {
        matchScoreDisplay.textContent = `Error: ${error.message}`;
    }
}

generateReportBtn.addEventListener('click', async () => {
    reportStatus.textContent = 'Generating report...';

    try {
        const payload = {
            match_score: currentMatchScore !== null ? currentMatchScore : 0,
            matched_keywords: currentMatchedKeywords,
            missing_keywords: currentMissingKeywords,
            resume_name: resumeFileInput.files[0]?.name || 'Resume',
            job_role: 'Sample Job Role',
        };

        const response = await fetch('http://127.0.0.1:8000/generate-report', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `ATS_Report_${payload.resume_name.replace(/\s+/g, '_')}.pdf`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
            reportStatus.textContent = 'Report downloaded.';
        } else {
            const data = await response.json();
            reportStatus.textContent = `Error: ${data.detail || 'Failed to generate report.'}`;
        }
    } catch (error) {
        reportStatus.textContent = `Error: ${error.message}`;
    }
});
