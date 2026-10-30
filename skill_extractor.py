import json
import re
from pathlib import Path
from typing import Any

from role_taxonomy import ROLE_TAXONOMY

BASE_DIR = Path(__file__).resolve().parent
ALIASES = {
    "sklearn": "scikit-learn",
    "scikit learn": "scikit-learn",
    "powerbi": "power bi",
    "power-bi": "power bi",
    "js": "javascript",
    "node": "node.js",
    "wireframe": "wireframing",
    "prototype": "prototyping",
    "randomforest": "random forest",
    "random-forest": "random forest",
    "hyperparameter optimisation": "hyperparameter tuning",
    "hyperparameter optimization": "hyperparameter tuning",
    "model validation": "model evaluation",
    "f1": "model evaluation",
    "tuned hyperparameters": "hyperparameter tuning",
}


def preprocess_text(text: str) -> str:
    text = text.casefold().replace("&", " and ")
    text = re.sub(r"[\u2010-\u2015-]", "-", text)
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9+#./\s-]", " ", text)).strip()


def load_skill_dict(path: str | Path | None = None) -> dict[str, list[str]]:
    skill_path = Path(path) if path else BASE_DIR / "data" / "skills.json"
    with skill_path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _skill_variants(skill: str) -> list[str]:
    normalized = preprocess_text(skill)
    variants = [normalized]
    for alias, canonical in ALIASES.items():
        if normalized == canonical:
            variants.append(alias)
    return list(dict.fromkeys(variants))


def _find_evidence(text: str, skill: str) -> str | None:
    source_lines = [line.strip() for line in text.splitlines() if line.strip()]
    patterns = [
        re.compile(r"(?<![a-z0-9])" + re.escape(variant).replace(r"\ ", r"\s+") + r"(?![a-z0-9])", re.I)
        for variant in _skill_variants(skill)
    ]
    matches = [line for line in source_lines if any(pattern.search(line) for pattern in patterns)]
    if not matches:
        return None
    sections = extract_sections(text)
    priority = {"experience": 4, "projects": 4, "certifications": 3, "achievements": 3, "skills": 2, "summary": 1, "other": 0}
    return max(matches, key=lambda line: priority.get(_section_for_line(line, sections), 0))[:300]


def _section_for_line(line: str, sections: dict[str, str]) -> str:
    for name, content in sections.items():
        if line in content:
            return name
    return "other"


def extract_sections(text: str) -> dict[str, str]:
    names = {
        "summary": ("summary", "profile", "objective"),
        "skills": ("skills", "technical skills", "competencies"),
        "experience": ("experience", "employment", "work history"),
        "projects": ("projects", "portfolio"),
        "education": ("education", "academic"),
        "certifications": ("certifications", "certificates"),
        "achievements": ("achievements", "awards"),
    }
    sections: dict[str, list[str]] = {"other": []}
    current = "other"
    for raw_line in text.splitlines():
        line = raw_line.strip()
        normalized = preprocess_text(line).rstrip(":")
        matched = next((key for key, aliases in names.items() if normalized in aliases), None)
        if matched:
            current = matched
            sections.setdefault(current, [])
        else:
            sections.setdefault(current, []).append(raw_line)
    return {key: "\n".join(value).strip() for key, value in sections.items() if "\n".join(value).strip()}


def extract_skill_evidence(resume_text: str, target_role: str | None = None) -> dict[str, Any]:
    if not resume_text or len(resume_text.strip()) < 10:
        return {
            "explicit": [], "demonstrated": [], "mentioned_without_evidence": [],
            "inferred": [], "strongest_supported": [], "strong_skills": [],
            "strong_skill_evidence": [], "evidence": [],
        }

    sections = extract_sections(resume_text)
    catalog: dict[str, set[str]] = {}
    for skills in load_skill_dict().values():
        for skill in skills:
            catalog.setdefault(preprocess_text(skill), set()).add(skill)
    for metadata in ROLE_TAXONOMY.values():
        for skill in metadata["skills"]:
            catalog.setdefault(preprocess_text(skill), set()).add(skill)

    evidence: list[dict[str, Any]] = []
    for normalized, spellings in catalog.items():
        canonical = sorted(spellings, key=len)[0]
        line = _find_evidence(resume_text, canonical)
        if line:
            section = _section_for_line(line, sections)
            support = "experience" if section == "experience" else "project" if section == "projects" else "listed"
            score = 1.0 if support in {"experience", "project"} else 0.4
            evidence.append({"skill": canonical, "evidence": line, "section": section, "support": support, "score": score})

    project_or_experience = "\n".join(
        sections.get(name, "") for name in ("projects", "experience")
    )
    if re.search(r"\b(random forest|neural network|deep learning|classification|regression)\b", project_or_experience, re.I):
        if not any(item["skill"] == "machine learning" and item["support"] in {"project", "experience"} for item in evidence):
            evidence.append({
                "skill": "machine learning",
                "evidence": next(
                    line.strip() for line in project_or_experience.splitlines()
                    if re.search(r"\b(random forest|neural network|deep learning|classification|regression)\b", line, re.I)
                )[:300],
                "section": "projects" if sections.get("projects") else "experience",
                "support": "project" if sections.get("projects") else "experience",
                "score": 1.0,
            })

    explicit = [item["skill"] for item in evidence if item["support"] == "listed"]
    demonstrated = [item["skill"] for item in evidence if item["support"] in {"experience", "project"}]
    target_skills = ROLE_TAXONOMY.get(target_role or "", {}).get("skills", [])
    mentioned = [item["skill"] for item in evidence if item["skill"] not in demonstrated and item["skill"] in target_skills]
    strong_evidence = [
        item for item in evidence
        if item["score"] >= 0.7
    ]
    strongest = list(dict.fromkeys(item["skill"] for item in strong_evidence))
    return {
        "explicit": list(dict.fromkeys(explicit)),
        "demonstrated": list(dict.fromkeys(demonstrated)),
        "mentioned_without_evidence": list(dict.fromkeys(mentioned)),
        "inferred": [],
        "strongest_supported": strongest,
        "strong_skills": strongest,
        "strong_skill_evidence": strong_evidence,
        "evidence": evidence,
    }


def extract_skills(resume_text: str, category: str | None = None) -> tuple[list[str], list[str]]:
    """Compatibility wrapper returning skills and role skills not evidenced in the document."""
    extracted = extract_skill_evidence(resume_text, category)
    compatibility_roles = {
        "Software Developer": "Software Engineer",
        "Digital Marketing": "Digital Marketing Specialist",
        "Machine Learning": "Machine Learning Engineer",
    }
    role_metadata = ROLE_TAXONOMY.get(category or "") or ROLE_TAXONOMY.get(compatibility_roles.get(category or "", ""))
    required = role_metadata.get("skills", []) if role_metadata else []
    present = extracted["strongest_supported"]
    present_normalized = {preprocess_text(skill) for skill in present}
    missing = [skill for skill in required if preprocess_text(skill) not in present_normalized]
    return present, missing


def fuzzy_skill_match(text: str, skill: str, threshold: float = 0.7) -> bool:
    """Retained for compatibility; matching is now boundary-safe and non-fuzzy."""
    return _find_evidence(text, skill) is not None
