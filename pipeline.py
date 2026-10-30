import hashlib
import re
from pathlib import Path
from typing import Any

import joblib

from job_matcher import calculate_match_score, match_best_job
from role_taxonomy import ROLE_TAXONOMY, TAXONOMY_VERSION
from skill_extractor import extract_sections, extract_skill_evidence, preprocess_text

BASE_DIR = Path(__file__).resolve().parent
MODEL_VERSION = "legacy-tfidf-nb-v1"
MODEL_DIR = BASE_DIR / "models"

try:
    clf = joblib.load(MODEL_DIR / "classifier_model.pkl")
    vectorizer = joblib.load(MODEL_DIR / "tfidf_vectorizer.pkl")
    label_encoder = joblib.load(MODEL_DIR / "label_encoder.pkl")
    MODEL_AVAILABLE = set(getattr(clf, "classes_", [])) == set(range(len(label_encoder.classes_)))
except (FileNotFoundError, OSError, ValueError):
    clf = vectorizer = label_encoder = None
    MODEL_AVAILABLE = False


def _find_stated_title(text: str) -> str | None:
    raw_lines = [line.strip() for line in text.splitlines() if preprocess_text(line)]
    lines = [preprocess_text(line) for line in raw_lines]
    title_pattern = re.compile(r"(?:title|role|position)\s*[:\-]\s*(.+)", re.I)
    for line in raw_lines[:20]:
        match = title_pattern.match(line)
        if match:
            return match.group(1).strip()
    title_words = ("engineer", "developer", "scientist", "analyst", "designer", "architect", "specialist", "executive", "teacher", "accountant")
    for raw_line, normalized_line in zip(raw_lines[:12], lines[:12]):
        if "|" in raw_line or any(word in normalized_line for word in title_words):
            return raw_line
    return None


def _title_matches_role(title: str | None, role: str, aliases: list[str]) -> bool:
    if not title:
        return False
    normalized_title = preprocess_text(title.split("|", 1)[0])
    return any(
        re.search(r"(?<![a-z0-9])" + re.escape(alias) + r"(?![a-z0-9])", normalized_title, re.I)
        for alias in [role, *aliases]
    )


def _role_scores(text: str, skills: dict[str, Any], stated_title: str | None) -> list[dict[str, Any]]:
    normalized = preprocess_text(text)
    evidence_skills = {preprocess_text(skill) for skill in skills["strongest_supported"]}
    results = []
    for role, metadata in ROLE_TAXONOMY.items():
        relevant = {preprocess_text(skill) for skill in metadata["skills"]}
        skill_score = len(evidence_skills & relevant) / max(1, len(relevant))
        title_score = 1.0 if _title_matches_role(stated_title, role, metadata["aliases"]) else 0.0
        role_mentions = sum(1 for alias in [role, *metadata["aliases"]] if re.search(r"(?<![a-z0-9])" + re.escape(alias) + r"(?![a-z0-9])", normalized))
        score = min(1.0, skill_score * 0.45 + title_score * 0.45 + min(role_mentions, 1) * 0.1)
        if score > 0:
            score_pct = round(score * 100, 1)
            results.append({
                "role": role,
                "domain": metadata["domain"],
                "score": score_pct,
                "score_pct": score_pct,
                "score_fraction": round(score, 4),
                "matched_skills": sorted(evidence_skills & relevant),
            })
    return sorted(results, key=lambda item: (-item["score_pct"], item["role"]))


def _recommendations(text: str, sections: dict[str, str], skills: dict[str, Any], role: str | None) -> list[dict[str, str]]:
    recommendations: list[dict[str, str]] = []
    if not sections.get("summary"):
        recommendations.append({"issue": "No professional summary is evidenced", "evidence": "The document has no summary/profile section.", "why": "A concise summary helps recruiters understand fit quickly.", "suggestion": "Add a 2-3 sentence summary using only verified experience.", "priority": "high", "expected_benefit": "Improves first-pass relevance.", "example": "[Target role] with [verified years] of experience in [verified skills]."})
    experience = sections.get("experience", "")
    if experience and not re.search(r"\d+%|\b\d+\+?\s*(users|customers|projects|records|hours|people|days)\b", experience, re.I):
        recommendations.append({"issue": "Experience lacks measurable outcomes", "evidence": experience.splitlines()[0][:240], "why": "Outcomes make responsibilities more credible and scannable.", "suggestion": "Add a verified metric or scope to relevant bullet points.", "priority": "medium", "expected_benefit": "Makes impact clearer.", "example": "Improved [verified metric] by [verified amount] by [action]."})
    if not sections.get("projects") and role and role in {"Data Scientist", "Machine Learning Engineer", "AI Engineer", "Software Engineer", "UI/UX Designer"}:
        recommendations.append({"issue": "No project evidence is present", "evidence": "No projects/portfolio section was extracted.", "why": "Projects can demonstrate applied skills beyond job titles.", "suggestion": "Add a relevant project with your contribution, tools, and verified outcome.", "priority": "medium", "expected_benefit": "Adds role-specific evidence.", "example": "Built [project] using [verified tools]; contributed [specific contribution]."})
    if skills["mentioned_without_evidence"]:
        recommendations.append({"issue": "Some target skills are listed without supporting evidence", "evidence": ", ".join(skills["mentioned_without_evidence"]), "why": "Listing a tool without context does not show proficiency.", "suggestion": "Add a project or experience bullet showing how each skill was used, or remove it.", "priority": "medium", "expected_benefit": "Improves evidence quality.", "example": "Used [skill] to [verified task] in [project/role]."})
    return recommendations


def predict_category(resume_text: str) -> str | None:
    if not MODEL_AVAILABLE:
        return None
    values = clf.predict(vectorizer.transform([resume_text]))
    return str(label_encoder.inverse_transform(values)[0])


def classifier_signal(resume_text: str) -> dict[str, Any]:
    if not MODEL_AVAILABLE:
        return {"available": False, "reason": "Saved classifier artifacts do not contain a complete class mapping.", "predicted_category": None, "probabilities": []}
    features = vectorizer.transform([resume_text])
    values = clf.predict(features)
    probabilities = clf.predict_proba(features)[0]
    return {
        "available": True,
        "predicted_category": str(label_encoder.inverse_transform(values)[0]),
        "probabilities": [
            {"category": str(category), "probability_pct": round(float(probability) * 100, 1)}
            for category, probability in zip(label_encoder.classes_, probabilities)
        ],
    }


def _empty_result(message: str) -> dict[str, Any]:
    return {
        "analysis_id": None, "status": "failed", "error": message, "category": None,
        "skills": {"present": [], "explicit": [], "demonstrated": [], "strong": [], "inferred": [], "mentioned_without_evidence": [], "evidence": []},
        "strong_skills": [], "strong_skill_evidence": [], "missing_skills": [], "ats_score": 0, "match_score": 0,
        "best_job": None, "explanations": {"why_missing": message, "top_keywords": []},
        "extraction_warnings": [message],
    }


def analyze_resume_text(resume_text: str, user_id: str | None = None, filename: str | None = None,
                        target_role: str | None = None, job_description: str | None = None) -> dict[str, Any]:
    if not resume_text or len(resume_text.strip()) < 50:
        return _empty_result("Resume text is too short or empty; no analysis was performed.")

    sections = extract_sections(resume_text)
    stated_title = _find_stated_title(resume_text)
    skills = extract_skill_evidence(resume_text, target_role)
    roles = _role_scores(resume_text, skills, stated_title)
    primary = roles[0] if roles else None
    selected_role = target_role if target_role in ROLE_TAXONOMY else (primary["role"] if primary else None)
    selected_skills = extract_skill_evidence(resume_text, selected_role)
    required = ROLE_TAXONOMY.get(selected_role or "", {}).get("skills", [])
    evidenced_or_listed = list(dict.fromkeys(
        selected_skills["strongest_supported"] + selected_skills["explicit"]
    ))
    matched = sorted({preprocess_text(skill) for skill in evidenced_or_listed} & {preprocess_text(skill) for skill in required})
    missing = [skill for skill in required if preprocess_text(skill) not in set(matched)]
    coverage = calculate_match_score(selected_skills["strongest_supported"], required)
    best_job = match_best_job(predict_category(resume_text), selected_skills["strongest_supported"])
    job_score = calculate_match_score(selected_skills["strongest_supported"], [item for item in (best_job or {}).get("required_skills", [])])
    completeness = min(100, round(sum(bool(sections.get(name)) for name in ("summary", "skills", "experience", "education")) / 4 * 100))
    parsing_quality = min(100, round(min(len(resume_text), 5000) / 5000 * 100))
    primary_score = primary["score_pct"] if primary else 0
    confidence = primary_score if primary else 0
    warnings = []
    if stated_title and primary and stated_title.casefold() != primary["role"].casefold() and stated_title.casefold() not in [alias.casefold() for alias in ROLE_TAXONOMY[primary["role"]]["aliases"]]:
        warnings.append("The stated title does not fully align with the strongest evidence-based role.")
    if not roles:
        warnings.append("Insufficient role-specific evidence for a confident classification.")
    if not MODEL_AVAILABLE:
        warnings.append("The saved classifier artifacts are unavailable or inconsistent; taxonomy scoring was used.")

    analysis_id = hashlib.sha256(((filename or "") + "|" + resume_text).encode("utf-8")).hexdigest()[:16]
    legacy_category = primary["role"] if primary else None
    analysis_status = "complete" if primary and primary_score >= 35 else "uncertain"
    return {
        "analysis_id": analysis_id, "status": analysis_status, "category": legacy_category,
        "stated_job_title": stated_title,
        "primary_role": primary["role"] if primary else None,
        "primary_domain": primary["domain"] if primary else None,
        "secondary_roles": roles[1:4],
        "classification": {
            "confidence": confidence, "confidence_pct": confidence, "confidence_is_calibrated": False,
            "role_relevance_scores_pct": [{"role": item["role"], "score_pct": item["score_pct"]} for item in roles],
            "role_scores": roles,
            "supporting_evidence": skills["evidence"][:10],
            "contradictory_evidence": warnings,
            "explanation": "Role ranking combines stated title, role aliases, and skills evidenced in the document."
        },
        "classifier": classifier_signal(resume_text),
        "skills": {
            "present": list(dict.fromkeys(skills["explicit"] + skills["demonstrated"])),
            "explicit": skills["explicit"],
            "demonstrated": skills["demonstrated"],
            "strong": skills["strong_skills"],
            "strong_skills": skills["strong_skills"],
            "inferred": skills["inferred"],
            "mentioned_without_evidence": skills["mentioned_without_evidence"],
            "evidence": skills["evidence"],
        },
        "strong_skills": skills["strong_skills"],
        "strong_skill_evidence": skills["strong_skill_evidence"],
        "missing_skills": missing, "target_role": selected_role,
        "score_breakdown": {"resume_completeness": completeness, "target_role_skill_coverage": coverage, "job_description_relevance": job_score if job_description or best_job else None, "parsing_quality": parsing_quality},
        "ats_score": round((completeness * 0.35) + (coverage * 0.45) + (parsing_quality * 0.2)),
        "match_score": coverage, "best_job": best_job,
        "explanations": {"why_missing": f"Skills not evidenced for {selected_role or 'the selected role'}: {', '.join(missing) if missing else 'None'}", "top_keywords": skills["strongest_supported"]},
        "profile": {"summary": sections.get("summary"), "sections": sections, "professional_title": stated_title},
        "recommendations": _recommendations(resume_text, sections, selected_skills, selected_role),
        "extraction_warnings": warnings, "analysis_method": "hybrid-title-taxonomy-evidence",
        "model_version": MODEL_VERSION, "taxonomy_version": TAXONOMY_VERSION,
        "limitations": ["Confidence is a deterministic ranking score, not a calibrated probability.", "Skills and claims are limited to evidence in the uploaded document."],
    }
