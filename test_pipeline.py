import unittest

from job_matcher import calculate_match_score
from main import AnalysisResponse
from pipeline import analyze_resume_text
from skill_extractor import extract_skill_evidence


def resume(title: str, skills: str, section: str, body: str) -> str:
    return f"""{title}
SUMMARY
{title} professional.
SKILLS
{skills}
{section.upper()}
{body}
EDUCATION
Relevant degree
"""


AI_ML = resume(
    "AI/ML Engineer | Data Science | Python Developer",
    "Python, scikit-learn, PyTorch, TensorFlow, FastAPI, Random Forest",
    "projects",
    "Built and evaluated a Random Forest model with scikit-learn; tuned hyperparameters and measured F1 score.",
)
DATA_SCIENTIST = resume(
    "Data Scientist",
    "Python, pandas, statistics, experimentation",
    "experience",
    "Designed statistical experiments and evaluated regression models on customer data.",
)
BUSINESS_DATA_ANALYST = resume(
    "Business Data Analyst",
    "SQL, Excel, requirements gathering, data visualization",
    "experience",
    "Gathered stakeholder requirements and built SQL reports and dashboards for business decisions.",
)
DATA_ENGINEER = resume(
    "Data Engineer",
    "Python, SQL, Spark, Airflow, ETL",
    "experience",
    "Built ETL data pipelines with Airflow and Spark and maintained production data jobs.",
)
SOFTWARE_ENGINEER = resume(
    "Software Engineer",
    "Python, API, Git, SQL",
    "experience",
    "Developed and tested backend APIs in Python and maintained Git-based deployments.",
)
QA_ENGINEER = resume(
    "QA Engineer",
    "Selenium, pytest, regression testing, API testing",
    "experience",
    "Automated regression and API tests with Selenium and pytest for each release.",
)


class AnalysisTests(unittest.TestCase):
    def test_ai_ml_headline_and_project_evidence_rank_ai_roles(self):
        result = analyze_resume_text(AI_ML)
        self.assertIn(result["primary_role"], {"AI Engineer", "Machine Learning Engineer"})
        self.assertIn("machine learning", [skill.casefold() for skill in result["strong_skills"]])
        self.assertIn("random forest", [skill.casefold() for skill in result["strong_skills"]])
        self.assertTrue(result["strong_skill_evidence"])

    def test_distinct_roles_are_classified_from_responsibilities(self):
        expected = [
            (DATA_SCIENTIST, "Data Scientist"),
            (BUSINESS_DATA_ANALYST, "Business Data Analyst"),
            (DATA_ENGINEER, "Data Engineer"),
            (SOFTWARE_ENGINEER, "Software Engineer"),
            (QA_ENGINEER, "QA Engineer"),
        ]
        for text, role in expected:
            with self.subTest(role=role):
                self.assertEqual(analyze_resume_text(text)["primary_role"], role)

    def test_listed_skill_is_not_strong_or_missing(self):
        text = resume("Data Engineer", "Python, Spark", "experience", "Maintained data documentation.")
        result = analyze_resume_text(text)
        self.assertIn("spark", [skill.casefold() for skill in result["skills"]["explicit"]])
        self.assertNotIn("spark", [skill.casefold() for skill in result["strong_skills"]])
        self.assertNotIn("spark", [skill.casefold() for skill in result["missing_skills"]])

    def test_alias_in_project_is_demonstrated(self):
        evidence = extract_skill_evidence(
            "Machine Learning Engineer\nPROJECTS\nBuilt a model with sklearn and random-forest tuning."
        )
        skills = [skill.casefold() for skill in evidence["strong_skills"]]
        self.assertIn("scikit-learn", skills)
        self.assertIn("random forest", skills)

    def test_weak_keyword_resume_is_uncertain(self):
        result = analyze_resume_text(
            "Python, SQL, machine learning, testing, design, analytics. "
            "Interested in technology roles and learning new tools."
        )
        self.assertEqual(result["status"], "uncertain")
        self.assertTrue(result["extraction_warnings"])

    def test_results_do_not_leak_between_resumes(self):
        first = analyze_resume_text(DATA_ENGINEER)
        second = analyze_resume_text(QA_ENGINEER)
        self.assertNotEqual(first["analysis_id"], second["analysis_id"])
        self.assertEqual(first["primary_role"], "Data Engineer")
        self.assertEqual(second["primary_role"], "QA Engineer")

    def test_repeated_analysis_is_deterministic(self):
        self.assertEqual(analyze_resume_text(AI_ML), analyze_resume_text(AI_ML))

    def test_missing_text_returns_failure(self):
        result = analyze_resume_text("")
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["strong_skills"], [])

    def test_scores_and_schema_use_percentages_once(self):
        result = analyze_resume_text(AI_ML)
        self.assertGreaterEqual(result["classification"]["confidence_pct"], 0)
        self.assertLessEqual(result["classification"]["confidence_pct"], 100)
        self.assertTrue(all(0 <= item["score_pct"] <= 100 for item in result["secondary_roles"]))
        self.assertLessEqual(result["match_score"], 100)
        self.assertLessEqual(result["ats_score"], 100)
        validated = AnalysisResponse.model_validate(result)
        self.assertEqual(validated.primary_role, result["primary_role"])

    def test_duplicate_skills_do_not_inflate_match(self):
        self.assertEqual(calculate_match_score(["SQL", "sql", "Power BI"], ["sql", "power bi"]), 100)


if __name__ == "__main__":
    unittest.main()
