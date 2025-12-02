# pipeline.py
import joblib
from skill_extractor import extract_skills
from job_matcher import match_best_job
import os

# load saved classifier & vectorizer & label encoder
MODEL_DIR = "models"
MODEL_FILE = os.path.join(MODEL_DIR, "classifier_model.pkl")
VECT_FILE = os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl")
LE_FILE = os.path.join(MODEL_DIR, "label_encoder.pkl")

clf = joblib.load(MODEL_FILE)
vectorizer = joblib.load(VECT_FILE)
label_encoder = joblib.load(LE_FILE)

def predict_category(resume_text: str):
    X = vectorizer.transform([resume_text])
    label = clf.predict(X)[0]
    category = label_encoder.inverse_transform([label])[0]
    return category

def analyze_resume_text(resume_text: str, user_id: str=None, filename: str=None):
    # Validate input
    if not resume_text or len(resume_text.strip()) < 20:
        return {
            "error": "Resume text is too short or empty. Please upload a valid PDF or DOCX file.",
            "category": None,
            "skills": {"present": []},
            "missing_skills": [],
            "ats_score": 0,
            "match_score": 0,
            "best_job": None,
            "explanations": {"why_missing": "Invalid resume", "top_keywords": []}
        }
    
    # 1) Predict category
    category = predict_category(resume_text)

    # 2) Extract skills
    present_skills, missing_skills = extract_skills(resume_text, category)

    # 3) Job matching
    best_job = match_best_job(category, present_skills)

    # 4) Compute simple scores
    required_skills = best_job["required_skills"] if best_job else []
    match_score = best_job["match_score"] if best_job else 0

    keyword_match_pct = int((len(present_skills) / max(1, len(required_skills))) * 100) if required_skills else 0
    # simple ATS score (tunable)
    ats_score = int(0.6 * keyword_match_pct + 0.4 * match_score)

    # build response
    result = {
        "category": category,
        "skills": {
            "present": present_skills,
        },
        "missing_skills": missing_skills,
        "ats_score": ats_score,
        "match_score": match_score,
        "best_job": best_job,
        "explanations": {
            "why_missing": f"Missing skills for {category}: {', '.join(missing_skills) if missing_skills else 'None'}" if missing_skills else f"Great! No missing skills for {category}",
            "top_keywords": present_skills
        }
    }
    return result
