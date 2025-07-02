import re
import string
from collections import defaultdict

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

    # Dynamic category generation by grouping keywords by common prefixes or stems
    category_keywords_map = defaultdict(set)

    for keyword in job_keywords:
        # Use simple heuristic: group by first 4 letters or whole word if short
        category_key = keyword[:4] if len(keyword) > 4 else keyword
        category_keywords_map[category_key].add(keyword)

    # Evaluate each dynamic category
    ats_match_breakdown = []
    recommendations = []
    for category_key, keywords in category_keywords_map.items():
        matched = matched_keywords.intersection(keywords)
        if matched:
            match_level = "Good"
            details = f"Matched keywords: {', '.join(matched)}"
        else:
            match_level = "None"
            details = "Not mentioned."

        ats_match_breakdown.append({
            "category": category_key.capitalize(),
            "match_level": match_level,
            "details": details,
        })

        # Add generic recommendation for categories with no match
        if match_level == "None":
            recommendations.append(f"Consider gaining experience or knowledge in '{category_key}' related areas.")

    # Summary
    summary = (
        "The resume is evaluated against the provided job description dynamically. "
        "Focus on improving areas with low or no match to increase your ATS compatibility."
    )

    report = {
        "match_score_estimate": f"~{match_score_value - 10}-{match_score_value + 10}%",
        "ats_match_breakdown": ats_match_breakdown,
        "recommendations": recommendations,
        "summary": summary,
    }

    return report
