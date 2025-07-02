import re
import string
from collections import defaultdict
from fuzzywuzzy import fuzz
import spacy
from spacy.matcher import PhraseMatcher, Matcher
from domain_keywords import DOMAIN_KEYWORDS

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

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
    Also extracts common bigrams (two-word phrases).
    """
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    words = re.findall(r'\b\w{3,}\b', text) # words of 3 or more characters
    
    # Add bigrams (two-word phrases)
    bigrams = [" ".join(words[i:i+2]) for i in range(len(words) - 1)]
    
    all_terms = set(word for word in words if word not in STOPWORDS)
    all_terms.update(set(bigram for bigram in bigrams if all(word not in STOPWORDS for word in bigram.split())))
    
    return all_terms



def extract_and_categorize_keywords(job_description: str, categories: dict) -> dict:
    """
    Extracts keywords from the job description and categorizes them into universal categories using NLP and domain-specific keywords.
    """
    doc = nlp(job_description)
    
    # Reset keywords for each call
    for category in categories:
        categories[category]["keywords"] = []

    # Detect job domain
    job_domain = None
    for domain, keywords in DOMAIN_KEYWORDS.items():
        for category, keyword_list in keywords.items():
            for keyword in keyword_list:
                if keyword in job_description.lower():
                    job_domain = domain
                    break
            if job_domain:
                break
        if job_domain:
            break

    # Populate categories with domain-specific keywords
    if job_domain:
        for category, keyword_list in DOMAIN_KEYWORDS[job_domain].items():
            categories[category]["keywords"].extend(keyword_list)

    # Keyword extraction logic
    for ent in doc.ents:
        if ent.label_ in ["ORG", "PRODUCT", "SKILL"]:
            categories["Skills"]["keywords"].append(ent.text)
        elif ent.label_ == "PERSON":
            categories["Soft Skills"]["keywords"].append(ent.text)
        elif ent.label_ == "DATE":
            if "year" in ent.text.lower() or "experience" in ent.text.lower():
                categories["Experience"]["keywords"].append(ent.text)
        elif ent.label_ in ["GPE", "LOC"]:
            categories["Skills"]["keywords"].append(ent.text)

    # Enhanced keyword extraction for Skills, Responsibilities, and Job Title
    for token in doc:
        if token.pos_ == "NOUN" and not token.is_stop:
            if "experience" in token.text.lower() or "years" in token.text.lower():
                categories["Experience"]["keywords"].append(token.text)
            elif "degree" in token.text.lower() or "education" in token.text.lower() or "bachelor" in token.text.lower() or "master" in token.text.lower() or "phd" in token.text.lower():
                categories["Education"]["keywords"].append(token.text)
            elif "certification" in token.text.lower() or "certified" in token.text.lower():
                categories["Certifications"]["keywords"].append(token.text)
            elif "project" in token.text.lower() or "portfolio" in token.text.lower():
                categories["Projects / Portfolios"]["keywords"].append(token.text)
            else:
                # General nouns as skills
                categories["Skills"]["keywords"].append(token.text)
        elif token.pos_ == "VERB" and not token.is_stop:
            # Responsibilities: look for action verbs
            categories["Responsibilities Match"]["keywords"].append(token.lemma_)

    # Extracting multi-word skills and technologies
    skill_patterns = [
        {"LOWER": "html"}, {"LOWER": "css"}, {"LOWER": "javascript"},
        {"LOWER": "react"}, {"LOWER": "angular"}, {"LOWER": "node.js"},
        {"LOWER": "web"}, {"LOWER": "development"}, {"LOWER": "frameworks"},
        {"LOWER": "python"}, {"LOWER": "sql"}, {"LOWER": "kali"}, {"LOWER": "linux"},
        {"LOWER": "technical"}, {"LOWER": "support"}, {"LOWER": "security"}, {"LOWER": "researcher"}
    ]
    from spacy.matcher import PhraseMatcher
    matcher = PhraseMatcher(nlp.vocab)
    
    # Add patterns for common skills and technologies
    patterns = [nlp.make_doc(text) for text in [
        "HTML", "CSS", "JavaScript", "React", "Angular", "Node.js", "Web Development",
        "Python", "SQL", "Kali Linux", "Technical Support", "Security Researcher",
        "Sophos Firewall", "network interfaces", "firewall", "NAT rules", "VPN",
        "web filtering", "intrusion prevention", "threat protection", "logging",
        "firmware updates", "Google Analytics", "data storytelling", "client engagement",
        "campaign", "ROI", "customer segments", "Burp Suite", "OWASP", "OSCP", "CISSP"
    ]]
    matcher.add("SKILL_PATTERNS", patterns)

    matches = matcher(doc)
    for match_id, start, end in matches:
        span = doc[start:end]
        categories["Skills"]["keywords"].append(span.text)

    # Job Title & Role Match (more robust extraction)
    job_title_patterns = [
        {"LOWER": {"IN": ["developer", "engineer", "analyst", "manager", "specialist", "architect", "consultant"]}},
        {"POS": "NOUN", "OP": "+"},
        {"LOWER": {"IN": ["web", "software", "data", "security", "marketing", "financial"]}, "OP": "?"}
    ]
    from spacy.matcher import Matcher
    title_matcher = Matcher(nlp.vocab)
    title_matcher.add("JOB_TITLE", [job_title_patterns])
    title_matches = title_matcher(doc)
    for match_id, start, end in title_matches:
        span = doc[start:end]
        categories["Job Title & Role Match"]["keywords"].append(span.text)

    # Achievements & Impact (look for quantifiable terms and strong action verbs)
    impact_terms = [
        "increased", "decreased", "reduced", "improved", "achieved", "generated",
        "optimized", "streamlined", "implemented", "developed", "launched", "managed"
    ]
    for term in impact_terms:
        if term in job_description.lower():
            categories["Achievements & Impact"]["keywords"].append(term)

    return categories

def generate_detailed_report(resume_text: str, job_description: str, threshold=80) -> dict:
    """
    Generates a detailed report by categorizing keywords and providing recommendations.
    """
    UNIVERSAL_CATEGORIES = {
        "Job Title & Role Match": {"weight": 10, "keywords": []},
        "Experience": {"weight": 15, "keywords": []},
        "Skills": {"weight": 20, "keywords": []},
        "Certifications": {"weight": 10, "keywords": []},
        "Education": {"weight": 10, "keywords": []},
        "Soft Skills": {"weight": 10, "keywords": []},
        "Responsibilities Match": {"weight": 15, "keywords": []},
        "Achievements & Impact": {"weight": 5, "keywords": []},
        "Projects / Portfolios": {"weight": 5, "keywords": []},
        "Language / Communication Quality": {"weight": 0, "keywords": []} # Score handled separately
    }

    categorized_keywords = extract_and_categorize_keywords(job_description, UNIVERSAL_CATEGORIES)
    resume_keywords = extract_keywords(resume_text)

    ats_match_breakdown = []
    recommendations = []
    total_score = 0
    total_weight = 0

    all_matched_keywords = set()
    all_missing_keywords = set()

    for category, data in categorized_keywords.items():
        if not data["keywords"]:
            continue

        matched_in_category = set()
        for job_kw in data["keywords"]:
            for resume_kw in resume_keywords:
                if fuzz.token_set_ratio(job_kw, resume_kw) >= threshold:
                    matched_in_category.add(job_kw)
                    break

        category_match_percentage = 0
        if data["keywords"]:
            category_match_percentage = int(len(matched_in_category) / len(data["keywords"]) * 100)

        match_level = "None"
        if category_match_percentage >= 80:
            match_level = "Excellent"
        elif category_match_percentage >= 50:
            match_level = "Good"
        elif category_match_percentage > 0:
            match_level = "Partial"

        details = f"Matched: {', '.join(sorted(list(matched_in_category))) if matched_in_category else 'None'}. Missing: {', '.join(sorted(list(set(data['keywords']) - matched_in_category))) if (set(data['keywords']) - matched_in_category) else 'None'}."

        ats_match_breakdown.append({
            "category": category,
            "match_level": match_level,
            "percentage": f"{category_match_percentage}%",
            "details": details,
        })

        all_matched_keywords.update(matched_in_category)
        all_missing_keywords.update(set(data["keywords"]) - matched_in_category)

        if category_match_percentage < 50:
            recommendations.append(f"Improve your profile in '{category}' by adding relevant experience or skills. Missing keywords: {', '.join(sorted(list(set(data['keywords']) - matched_in_category)))}.")
        
        total_score += (category_match_percentage / 100) * data["weight"]
        total_weight += data["weight"]

    overall_match_score = int((total_score / total_weight) * 100) if total_weight > 0 else 0

    # Sort breakdown by percentage (descending) and then by category name
    ats_match_breakdown.sort(key=lambda x: (int(x['percentage'].replace('%', '')), x['category']), reverse=True)

    # Summary
    summary = (
        "This report evaluates your resume against the job description. "
        "Focus on improving areas with lower match percentages to enhance your ATS compatibility. "
        "Consider tailoring your resume to include more of the missing keywords and related concepts."
    )

    report = {
        "overall_match_score": f"{overall_match_score}%",
        "ats_match_breakdown": ats_match_breakdown,
        "recommendations": recommendations,
        "summary": summary,
        "matched_keywords": sorted(list(all_matched_keywords)),
        "missing_keywords": sorted(list(all_missing_keywords))
    }

    return report
