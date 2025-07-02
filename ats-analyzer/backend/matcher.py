import re
import string
from collections import defaultdict
from fuzzywuzzy import fuzz

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
    """
    Extracts keywords from text by tokenizing, removing punctuation and stopwords.
    """
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    words = re.findall(r'\b\w{3,}\b', text)
    return set(word for word in words if word not in STOPWORDS)

def compare_resume_job_keywords(resume_text: str, job_description: str, threshold=80) -> dict:
    """
    Compares resume and job description keywords using fuzzy matching.
    """
    resume_keywords = extract_keywords(resume_text)
    job_keywords = extract_keywords(job_description)

    matched_keywords = set()
    missing_keywords = set(job_keywords)

    for job_keyword in job_keywords:
        for resume_keyword in resume_keywords:
            if fuzz.ratio(job_keyword, resume_keyword) >= threshold:
                matched_keywords.add(job_keyword)
                if job_keyword in missing_keywords:
                    missing_keywords.remove(job_keyword)
                break

    match_score = 0
    if job_keywords:
        match_score = int(len(matched_keywords) / len(job_keywords) * 100)

    return {
        "match_score": match_score,
        "matched_keywords": sorted(list(matched_keywords)),
        "missing_keywords": sorted(list(missing_keywords))
    }

def generate_detailed_report(resume_text: str, job_description: str) -> dict:
    """
    Generates a detailed report by categorizing keywords and providing recommendations.
    """
    comparison_results = compare_resume_job_keywords(resume_text, job_description)
    matched_keywords = set(comparison_results["matched_keywords"])
    
    job_keywords = extract_keywords(job_description)

    # Predefined category keywords for reference
    predefined_categories = {
        "Experience Level": {"internship", "trainee", "junior", "senior", "lead", "manager", "consultant"},
        "Application Security": {"vulnerability", "assessment", "penetration", "secure", "code", "review", "testing"},
        "Programming Skills": {"java", "c++", "python", "javascript", "js", "shell", "bash"},
        "Security Tools": {"burp", "ida", "wireshark", "nmap", "nessus", "splunk", "zap"},
        "Certifications": {"oscp", "cissp", "security+", "ejpt", "oswe", "gwapt"},
        "Threat Modeling & Architecture": {"threat", "modeling", "architecture", "design"},
        "Manual Pen Testing": {"manual", "penetration", "exploit"},
        "Mobile App Security": {"mobile", "android", "ios", "app"},
        "Education": {"b.tech", "bachelor", "computer", "information", "technology", "cs"},
        "Communication Skills": {"communication", "teamwork", "leadership", "collaboration", "presentation"},
        "Projects & Initiatives": {"project", "initiative", "development", "software"},
    }

    # Map keywords to categories dynamically
    category_keywords_map = defaultdict(set)
    other_keywords = set()

    for keyword in job_keywords:
        matched_category = None
        for category, keywords_set in predefined_categories.items():
            if keyword in keywords_set:
                category_keywords_map[category].add(keyword)
                matched_category = category
                break
        if not matched_category:
            other_keywords.add(keyword)

    if other_keywords:
        category_keywords_map["Other"] = other_keywords

    # Evaluate each category
    ats_match_breakdown = []
    recommendations = []
    for category, keywords in category_keywords_map.items():
        category_matched = matched_keywords.intersection(keywords)
        
        if category_matched:
            match_level = "Good"
            details = f"Matched keywords: {', '.join(sorted(list(category_matched)))}"
        else:
            match_level = "None"
            details = "Not mentioned."

        ats_match_breakdown.append({
            "category": category,
            "match_level": match_level,
            "details": details,
        })

        # Add generic recommendation for categories with no match
        if match_level == "None":
            recommendations.append(f"Consider gaining experience or knowledge in '{category}' related areas.")

    # Summary
    summary = (
        "The resume is evaluated against the provided job description dynamically. "
        "Focus on improving areas with low or no match to increase your ATS compatibility."
    )

    match_score_value = comparison_results["match_score"]
    
    report = {
        "match_score_estimate": f"~{match_score_value - 5}-{match_score_value + 5}%",
        "ats_match_breakdown": ats_match_breakdown,
        "recommendations": recommendations,
        "summary": summary,
    }

    return report