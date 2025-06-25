const form = document.getElementById('analyzer-form');
const loader = document.getElementById('loader');
const resultsDiv = document.getElementById('results');
const matchScoreSpan = document.getElementById('match-score');
const matchedKeywordsList = document.getElementById('matched-keywords');
const missingKeywordsList = document.getElementById('missing-keywords');

let sessionId = null;

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  resultsDiv.style.display = 'none';
  loader.style.display = 'block';

  const resumeFileInput = document.getElementById('resume-file');
  const jobDescriptionInput = document.getElementById('job-description');

  if (resumeFileInput.files.length === 0) {
    alert('Please upload a resume file.');
    loader.style.display = 'none';
    return;
  }

  const resumeFile = resumeFileInput.files[0];
  const jobDescription = jobDescriptionInput.value.trim();

  if (!jobDescription) {
    alert('Please enter a job description.');
    loader.style.display = 'none';
    return;
  }

  try {
    // Upload resume file
    const formData = new FormData();
    formData.append('file', resumeFile);

    const uploadResponse = await fetch('http://localhost:8000/upload-resume', {
      method: 'POST',
      body: formData,
      headers: sessionId ? { 'X-Session-ID': sessionId } : {}
    });

    if (!uploadResponse.ok) {
      const errorData = await uploadResponse.json();
      throw new Error(errorData.detail || 'Failed to upload resume');
    }

    const uploadData = await uploadResponse.json();
    sessionId = uploadData.session_id || sessionId;

    // Submit job description
    const jobFormData = new FormData();
    jobFormData.append('description', jobDescription);

    const jobResponse = await fetch('http://localhost:8000/submit-job', {
      method: 'POST',
      body: jobFormData,
      headers: { 'X-Session-ID': sessionId }
    });

    if (!jobResponse.ok) {
      const errorData = await jobResponse.json();
      throw new Error(errorData.detail || 'Failed to submit job description');
    }

    // Get match score
    const matchResponse = await fetch('http://localhost:8000/match-score', {
      method: 'POST',
      headers: { 'X-Session-ID': sessionId }
    });

    if (!matchResponse.ok) {
      const errorData = await matchResponse.json();
      throw new Error(errorData.detail || 'Failed to get match score');
    }

    const matchData = await matchResponse.json();

    // Display results
    matchScoreSpan.textContent = matchData.match_score;
    matchedKeywordsList.innerHTML = '';
    missingKeywordsList.innerHTML = '';

    matchData.matched_keywords.forEach(keyword => {
      const li = document.createElement('li');
      li.textContent = keyword;
      matchedKeywordsList.appendChild(li);
    });

    matchData.missing_keywords.forEach(keyword => {
      const li = document.createElement('li');
      li.textContent = keyword;
      missingKeywordsList.appendChild(li);
    });

    resultsDiv.style.display = 'block';
  } catch (error) {
    alert('Error: ' + error.message);
  } finally {
    loader.style.display = 'none';
  }
});
