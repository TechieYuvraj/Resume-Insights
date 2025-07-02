import re
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

def generate_detailed_report(resume_text: str, job_description: str) -> dict:
    resume_keywords = extract_keywords(resume_text)
    job_keywords = extract_keywords(job_description)

    matched_keywords = resume_keywords.intersection(job_keywords)
    missing_keywords = job_keywords.difference(resume_keywords)

    match_score_value = 0
    if job_keywords:
        match_score_value = int(len(matched_keywords) / len(job_keywords) * 100)

    # Example mappings for strengths and improvements
    strengths = []
    improvements = []

    # Sample keywords for categories (expand as needed)
    certifications = {"ceh", "security+", "oscp", "google cybersecurity professional certificate", "nptel"}
    tools = {"wireshark", "nmap", "nessus", "burp suite", "splunk", "kali linux", "termux", "reconx", "sophos firewall"}
    skills = {"python", "shell scripting", "vulnerability scanning", "penetration testing", "network protocols", "linux", "windows"}

    # Check strengths
    if any(cert in matched_keywords for cert in certifications):
        strengths.append("Certifications: Relevant certifications found in resume.")
    if any(tool in matched_keywords for tool in tools):
        strengths.append("Tools: Experience with key security tools.")
    if any(skill in matched_keywords for skill in skills):
        strengths.append("Skills: Strong relevant skills matched.")

    # Check improvements
    missing_certs = [cert for cert in certifications if cert in missing_keywords]
    if missing_certs:
        improvements.append(f"Certifications to consider: {', '.join(missing_certs)}")
    missing_tools = [tool for tool in tools if tool in missing_keywords]
    if missing_tools:
        improvements.append(f"Tools to gain experience with: {', '.join(missing_tools)}")
    missing_skills = [skill for skill in skills if skill in missing_keywords]
    if missing_skills:
        improvements.append(f"Skills to improve: {', '.join(missing_skills)}")

    # General suggestions
    suggestions = []
    if match_score_value < 70:
        suggestions.append("Consider including more relevant keywords from the job description in your resume.")
    else:
        suggestions.append("Your resume matches well with the job description.")

    report = {
        "match_score": match_score_value,
        "strengths": strengths,
        "areas_for_improvement": improvements,
        "suggestions": suggestions,
        "matched_keywords": list(matched_keywords),
        "missing_keywords": list(missing_keywords),
    }

    return report
