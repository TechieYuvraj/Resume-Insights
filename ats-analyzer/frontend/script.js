const uploadBtn = document.getElementById('upload-btn');
const resumeFileInput = document.getElementById('resume-file');
const uploadStatus = document.getElementById('upload-status');

const jobDescriptionSection = document.getElementById('job-description-section');
const jobDescriptionInput = document.getElementById('job-description');
const submitJobBtn = document.getElementById('submit-job-btn');
const jobStatus = document.getElementById('job-status');

const loader = document.getElementById('loader');
const reportSection = document.getElementById('report-section');
const matchScoreDisplay = document.getElementById('match-score');
const matchedKeywordsList = document.getElementById('matched-keywords');
const missingKeywordsList = document.getElementById('missing-keywords');
const detailedReportContainer = document.getElementById('detailed-report');

let sessionId = null;

// API base URL
const API_BASE_URL = 'http://127.0.0.1:8000';

uploadBtn.addEventListener('click', async () => {
    if (!resumeFileInput.files.length) {
        uploadStatus.textContent = 'Please select a resume file.';
        return;
    }
    const file = resumeFileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);

    uploadStatus.textContent = 'Uploading...';
    try {
        const response = await fetch(`${API_BASE_URL}/upload-resume`, {
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

    jobStatus.textContent = '';
    loader.style.display = 'block';
    reportSection.style.display = 'none';

    try {
        const formData = new FormData();
        formData.append('description', description);

        await fetch(`${API_BASE_URL}/submit-job`, {
            method: 'POST',
            headers: {
                'x-session-id': sessionId,
            },
            body: formData,
        });

        const reportResponse = await fetch(`${API_BASE_URL}/detailed-report`, {
            method: 'POST',
            headers: { 'x-session-id': sessionId }
        });

        const reportData = await reportResponse.json();

        if (reportResponse.ok) {
            displayReport(reportData);
        } else {
            throw new Error('Failed to fetch analysis.');
        }

    } catch (error) {
        jobStatus.textContent = `Error: ${error.message}`;
    } finally {
        loader.style.display = 'none';
    }
});

function displayReport(report) {
    reportSection.style.display = 'block';

    // Display match score
    matchScoreDisplay.textContent = `Match Score: ${report.overall_match_score}`;

    // Display keywords
    displayKeywords(matchedKeywordsList, report.matched_keywords);
    displayKeywords(missingKeywordsList, report.missing_keywords);

    // Display detailed report table
    displayDetailedReportTable(report.ats_match_breakdown);
}

function displayKeywords(listElement, keywords) {
    listElement.innerHTML = '';
    if (keywords.length > 0) {
        keywords.forEach(keyword => {
            const li = document.createElement('li');
            li.textContent = keyword;
            listElement.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.textContent = 'None';
        listElement.appendChild(li);
    }
}

function displayDetailedReportTable(breakdown) {
    detailedReportContainer.innerHTML = '';
    const table = document.createElement('table');
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    ['Category', 'Match Level', 'Percentage', 'Details'].forEach(text => {
        const th = document.createElement('th');
        th.textContent = text;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    const tbody = document.createElement('tbody');
    breakdown.forEach(item => {
        const row = document.createElement('tr');
        const categoryTd = document.createElement('td');
        categoryTd.textContent = item.category;
        row.appendChild(categoryTd);

        const matchLevelTd = document.createElement('td');
        matchLevelTd.textContent = item.match_level;
        row.appendChild(matchLevelTd);

        const percentageTd = document.createElement('td');
        percentageTd.textContent = item.percentage;
        row.appendChild(percentageTd);

        const detailsTd = document.createElement('td');
        detailsTd.textContent = item.details;
        row.appendChild(detailsTd);

        tbody.appendChild(row);
    });
    table.appendChild(tbody);
    detailedReportContainer.appendChild(table);
}

// Add event listeners for copy buttons
document.querySelectorAll('.copy-btn').forEach(button => {
    button.addEventListener('click', () => {
        const targetId = button.dataset.target;
        const list = document.getElementById(targetId);
        const textToCopy = Array.from(list.querySelectorAll('li')).map(li => li.textContent).join('\n');
        navigator.clipboard.writeText(textToCopy).then(() => {
            button.textContent = 'Copied!';
            setTimeout(() => { button.textContent = 'Copy'; }, 2000);
        });
    });
});