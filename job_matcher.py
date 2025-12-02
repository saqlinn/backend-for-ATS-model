import pandas as pd
import json
import re

def preprocess(x):
    return re.sub(r'[^a-zA-Z0-9\s]', ' ', x.lower())

def load_jobs(path="data/jobs.csv"):
    return pd.read_csv(path)

def load_skill_dict(path="data/skills.json"):
    with open(path, "r") as f:
        return json.load(f)

def calculate_match_score(present_skills, required_skills):
    if len(required_skills) == 0:
        return 0

    present_count = sum(1 for skill in required_skills if skill in present_skills)
    return int((present_count / len(required_skills)) * 100)

def match_best_job(category, present_skills):
    jobs = load_jobs()
    jobs = jobs[jobs["category"] == category]

    best_job = None
    best_score = -1

    for _, row in jobs.iterrows():
        required = [s.strip().lower() for s in row["required_skills"].split(",")]

        score = calculate_match_score(present_skills, required)

        if score > best_score:
            best_score = score
            best_job = {
                "job_title": row["job_title"],
                "required_skills": required,
                "match_score": best_score
            }

    return best_job

if __name__ == "__main__":
    present = ["python", "django", "sql"]
    result = match_best_job("Software Developer", present)
    print(result)
