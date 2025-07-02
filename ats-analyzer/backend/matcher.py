import re
import string
from collections import defaultdict
from fuzzywuzzy import fuzz
import spacy
from spacy.matcher import PhraseMatcher, Matcher

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
    doc = nlp(job_description.lower()) # Process in lowercase for consistent matching

    # Reset keywords for each call and initialize sets for uniqueness
    for category in categories:
        categories[category]["keywords"] = set()

    # Use PhraseMatcher for skills and certifications from predefined lists
    skill_matcher = PhraseMatcher(nlp.vocab)
    cert_matcher = PhraseMatcher(nlp.vocab)

    # Add common skills and technologies, including those previously from DOMAIN_KEYWORDS
    common_skills = [
        "HTML", "CSS", "JavaScript", "React", "Angular", "Node.js", "Web Development",
        "Python", "SQL", "Kali Linux", "Technical Support", "Security Researcher",
        "Sophos Firewall", "network interfaces", "firewall", "NAT rules", "VPN",
        "web filtering", "intrusion prevention", "threat protection", "logging",
        "firmware updates", "Google Analytics", "data storytelling", "client engagement",
        "campaign", "ROI", "customer segments", "Burp Suite", "OWASP", "OSCP", "CISSP",
        "machine learning", "artificial intelligence", "data science", "cloud computing",
        "devops", "agile", "scrum", "project management", "cybersecurity", "network security",
        "python", "java", "c++", "javascript", "react", "angular", "vue", "node.js", "django", "flask", "spring", "sql", "mongodb", "aws", "azure", "gcp", "docker", "kubernetes",
        "seo", "sem", "google analytics", "salesforce", "hubspot", "lead generation", "content marketing", "social media marketing"
    ]
    skill_patterns = [nlp.make_doc(text.lower()) for text in common_skills]
    skill_matcher.add("SKILL_PATTERNS", skill_patterns)

    # Add common certifications, including those previously from DOMAIN_KEYWORDS
    common_certifications = [
        "PMP", "CISSP", "CCNA", "CompTIA Security+", "AWS Certified Solutions Architect",
        "Microsoft Certified: Azure Administrator Associate", "Certified ScrumMaster", "OSCP",
        "aws certified developer", "google certified professional cloud architect", "microsoft certified: azure developer associate",
        "google analytics individual qualification (iq)", "hubspot content marketing certification", "salesforce certified administrator"
    ]
    cert_patterns = [nlp.make_doc(text.lower()) for text in common_certifications]
    cert_matcher.add("CERT_PATTERNS", cert_patterns)

    matches = skill_matcher(doc)
    for match_id, start, end in matches:
        span = doc[start:end]
        categories["Skills"]["keywords"].add(span.text)

    matches = cert_matcher(doc)
    for match_id, start, end in matches:
        span = doc[start:end]
        categories["Certifications"]["keywords"].add(span.text)

    # Enhanced keyword extraction using spaCy's NER and token attributes
    for ent in doc.ents:
        if ent.label_ in ["ORG", "PRODUCT", "SKILL", "LANGUAGE"]: # Broader entity types for skills
            categories["Skills"]["keywords"].add(ent.text)
        elif ent.label_ == "DATE":
            # Look for patterns indicating years of experience
            if "year" in ent.text or "experience" in ent.text:
                categories["Experience"]["keywords"].add(ent.text)
        elif ent.label_ in ["GPE", "LOC"]: # Geographic locations can sometimes be relevant for roles
            categories["Skills"]["keywords"].add(ent.text) # Or a new "Location" category

    # Iterate through tokens for more granular extraction
    for token in doc:
        # Education
        if token.pos_ == "NOUN" and any(edu_kw in token.text for edu_kw in ["degree", "bachelor", "master", "phd", "education", "university", "college"]):
            categories["Education"]["keywords"].add(token.text)
        
        # Experience (looking for years, or action verbs in context)
        if token.pos_ == "NOUN" and ("year" in token.text or "experience" in token.text):
            categories["Experience"]["keywords"].add(token.text)
        elif token.pos_ == "VERB" and not token.is_stop:
            # Responsibilities: action verbs
            categories["Responsibilities Match"]["keywords"].add(token.lemma_)
        
        # Soft Skills (often adjectives or nouns related to personal attributes)
        if token.pos_ == "ADJ" and token.text in ["strong", "excellent", "proven", "effective", "analytical", "creative", "problem-solving", "communication", "leadership", "teamwork"]:
            categories["Soft Skills"]["keywords"].add(token.text)
        elif token.pos_ == "NOUN" and token.text in ["communication", "leadership", "teamwork", "collaboration", "adaptability"]:
            categories["Soft Skills"]["keywords"].add(token.text)

        # Projects / Portfolios
        if token.pos_ == "NOUN" and ("project" in token.text or "portfolio" in token.text):
            categories["Projects / Portfolios"]["keywords"].add(token.text)

    # Job Title & Role Match (more robust extraction using patterns)
    title_matcher = Matcher(nlp.vocab)
    job_title_patterns = [
        [{"POS": "ADJ", "OP": "*"}, {"POS": "NOUN", "OP": "+"}, {"LOWER": {"IN": ["developer", "engineer", "analyst", "manager", "specialist", "architect", "consultant", "lead", "director"]}}]
    ]
    title_matcher.add("JOB_TITLE", job_title_patterns)
    title_matches = title_matcher(doc)
    for match_id, start, end in title_matches:
        span = doc[start:end]
        categories["Job Title & Role Match"]["keywords"].add(span.text)

    # Achievements & Impact (look for quantifiable terms and strong action verbs)
    impact_terms = [
        "increased", "decreased", "reduced", "improved", "achieved", "generated",
        "optimized", "streamlined", "implemented", "developed", "launched", "managed",
        "led", "drove", "delivered", "exceeded", "surpassed"
    ]
    for term in impact_terms:
        if term in job_description.lower():
            categories["Achievements & Impact"]["keywords"].add(term)

    # Convert sets back to lists for the report, ensuring uniqueness
    for category in categories:
        categories[category]["keywords"] = list(categories[category]["keywords"])

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

        details = f"Matched Keywords: {', '.join(sorted(list(matched_in_category))) if matched_in_category else 'None'}. Missing Keywords: {', '.join(sorted(list(set(data['keywords']) - matched_in_category))) if (set(data['keywords']) - matched_in_category) else 'None'}."

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
