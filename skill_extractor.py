import json
import re
from difflib import SequenceMatcher

def preprocess_text(text):
    """Convert text to lowercase and remove special characters"""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def load_skill_dict(path="data/skills.json"):
    with open(path, "r") as f:
        return json.load(f)

def fuzzy_skill_match(text, skill, threshold=0.7):
    """
    Check if skill appears in text with fuzzy matching.
    Handles variations like 'powerbi' vs 'power bi' vs 'power-bi'
    """
    skill_clean = skill.lower().replace(' ', '').replace('-', '')
    
    # Try exact word match first
    words = text.split()
    for word in words:
        word_clean = word.replace(' ', '').replace('-', '')
        if skill_clean == word_clean:
            return True
    
    # Try phrase match
    if skill.lower() in text:
        return True
    
    # Try fuzzy matching for variations
    if len(skill_clean) > 2:
        # Remove spaces for fuzzy comparison
        text_clean = text.replace(' ', '').replace('-', '')
        if skill_clean in text_clean:
            return True
        
        # Check similarity ratio
        ratio = SequenceMatcher(None, text_clean, skill_clean).ratio()
        if ratio >= threshold:
            return True
    
    return False

def extract_skills(resume_text, category):
    """
    Extract present and missing skills from resume text.
    Returns tuple of (present_skills, missing_skills)
    """
    if not resume_text or len(resume_text.strip()) < 10:
        return [], []
    
    resume_processed = preprocess_text(resume_text)
    skills_db = load_skill_dict()
    
    role_skills = skills_db.get(category, [])
    if not role_skills:
        return [], []
    
    present = []
    missing = []

    for skill in role_skills:
        if fuzzy_skill_match(resume_processed, skill.lower()):
            present.append(skill)
        else:
            missing.append(skill)

    return present, missing

if __name__ == "__main__":
    # test
    text = "I know Python, Django, SQL, and APIs"
    present, missing = extract_skills(text, "Software Developer")

    print("Present skills:", present)
    print("Missing skills:", missing)
