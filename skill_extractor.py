import json
import re

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    return text

def load_skill_dict(path="data/skills.json"):
    with open(path, "r") as f:
        return json.load(f)

def extract_skills(resume_text, category):
    resume_text = preprocess_text(resume_text)
    skills_db = load_skill_dict()
    
    role_skills = skills_db.get(category, [])
    present = []
    missing = []

    for skill in role_skills:
        if skill.lower() in resume_text:
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
