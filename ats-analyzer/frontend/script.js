const uploadBtn = document.getElementById('upload-btn');
const resumeFileInput = document.getElementById('resume-file');
const uploadStatus = document.getElementById('upload-status');

const jobDescriptionSection = document.getElementById('job-description-section');
const jobDescriptionInput = document.getElementById('job-description');
const submitJobBtn = document.getElementById('submit-job-btn');
const jobStatus = document.getElementById('job-status');

const matchScoreSection = document.getElementById('match-score-section');
const matchScoreDisplay = document.getElementById('match-score');
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
            await fetchDetailedReport();
        } else {
            jobStatus.textContent = `Error: ${data.detail || 'Submission failed.'}`;
        }
    } catch (error) {
        jobStatus.textContent = `Error: ${error.message}`;
    }
});

async function fetchDetailedReport() {
    matchScoreDisplay.textContent = 'Generating detailed report...';
    try {
        const response = await fetch('http://127.0.0.1:8000/detailed-report', {
            method: 'POST',
            headers: {
                'x-session-id': sessionId,
            },
        });
        const data = await response.json();
        if (response.ok) {
            displayDetailedReport(data);
        } else {
            matchScoreDisplay.textContent = `Error: ${data.detail || 'Failed to get detailed report.'}`;
        }
    } catch (error) {
        matchScoreDisplay.textContent = `Error: ${error.message}`;
    }
}

function displayDetailedReport(report) {
    // Clear previous content
    matchScoreDisplay.innerHTML = '';

    // Match Score
    const scoreElem = document.createElement('p');
    scoreElem.textContent = `ATS Compatibility Score: ${report.match_score}/100`;
    matchScoreDisplay.appendChild(scoreElem);

    // Strengths
    const strengthsHeader = document.createElement('h3');
    strengthsHeader.textContent = 'Strengths';
    matchScoreDisplay.appendChild(strengthsHeader);
    const strengthsList = document.createElement('ul');
    report.strengths.forEach(strength => {
        const li = document.createElement('li');
        li.textContent = strength;
        strengthsList.appendChild(li);
    });
    matchScoreDisplay.appendChild(strengthsList);

    // Areas for Improvement
    const improvementsHeader = document.createElement('h3');
    improvementsHeader.textContent = 'Areas for Improvement';
    matchScoreDisplay.appendChild(improvementsHeader);
    const improvementsList = document.createElement('ul');
    report.areas_for_improvement.forEach(improvement => {
        const li = document.createElement('li');
        li.textContent = improvement;
        improvementsList.appendChild(li);
    });
    matchScoreDisplay.appendChild(improvementsList);

    // Suggestions
    const suggestionsHeader = document.createElement('h3');
    suggestionsHeader.textContent = 'Suggestions';
    matchScoreDisplay.appendChild(suggestionsHeader);
    const suggestionsList = document.createElement('ul');
    report.suggestions.forEach(suggestion => {
        const li = document.createElement('li');
        li.textContent = suggestion;
        suggestionsList.appendChild(li);
    });
    matchScoreDisplay.appendChild(suggestionsList);
}

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

