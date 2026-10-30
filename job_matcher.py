from pathlib import Path
import re
from typing import Iterable

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9+#./\s-]", " ", value.casefold())).strip()


def _canonical(value: str) -> str:
    aliases = {"sklearn": "scikit-learn", "powerbi": "power bi", "power-bi": "power bi", "js": "javascript"}
    value = _normalize(value)
    return aliases.get(value, value)


def load_jobs(path: str | Path | None = None) -> pd.DataFrame:
    return pd.read_csv(path or BASE_DIR / "data" / "jobs.csv")


def calculate_match_score(present_skills: Iterable[str], required_skills: Iterable[str]) -> int:
    required = {_canonical(skill) for skill in required_skills if _canonical(skill)}
    present = {_canonical(skill) for skill in present_skills if _canonical(skill)}
    if not required:
        return 0
    return min(100, int(round(len(required & present) / len(required) * 100)))


def match_best_job(category: str | None, present_skills: Iterable[str], jobs: pd.DataFrame | None = None) -> dict | None:
    if not category:
        return None
    frame = jobs if jobs is not None else load_jobs()
    if "category" not in frame or "required_skills" not in frame:
        return None
    candidates = frame[frame["category"].astype(str).str.casefold() == category.casefold()]
    best_job = None
    best_score = -1
    present = list(present_skills)
    for _, row in candidates.iterrows():
        required = [_canonical(skill) for skill in str(row["required_skills"]).split(",") if _canonical(skill)]
        score = calculate_match_score(present, required)
        if score > best_score:
            best_score = score
            best_job = {"job_title": str(row["job_title"]), "required_skills": list(dict.fromkeys(required)), "match_score": score}
    return best_job
