import unittest

from job_matcher import calculate_match_score
from pipeline import analyze_resume_text
from skill_extractor import extract_skill_evidence


DATA_ANALYST = """DATA ANALYST
SUMMARY
Data analyst skilled in Excel, SQL and Power BI.
SKILLS
Excel, SQL, Power BI
EXPERIENCE
Built Power BI dashboards using SQL for 20 projects.
EDUCATION
BS Statistics
"""

ML_ENGINEER = """Machine Learning Engineer
SKILLS
Python, pandas, scikit-learn
PROJECTS
Built a classification model with feature engineering and cross validation.
EXPERIENCE
Trained models in Python for customer churn prediction.
"""


class AnalysisTests(unittest.TestCase):
    def test_skill_matching_requires_boundaries_and_returns_evidence(self):
        evidence = extract_skill_evidence("The candidate used SQL in a project.\nPROJECTS\nSQL reporting")
        self.assertIn("sql", [skill.casefold() for skill in evidence["strongest_supported"]])
        self.assertFalse(extract_skill_evidence("The candidate used sequel in a project.")["strongest_supported"])

    def test_scores_are_capped_and_unique(self):
        self.assertEqual(calculate_match_score(["SQL", "sql", "Power BI"], ["sql", "power bi"]), 100)
        result = analyze_resume_text(DATA_ANALYST)
        self.assertLessEqual(result["ats_score"], 100)
        self.assertLessEqual(result["match_score"], 100)

    def test_different_documents_produce_different_roles(self):
        data_result = analyze_resume_text(DATA_ANALYST)
        ml_result = analyze_resume_text(ML_ENGINEER)
        self.assertNotEqual(data_result["primary_role"], ml_result["primary_role"])
        self.assertEqual(data_result["analysis_id"], analyze_resume_text(DATA_ANALYST)["analysis_id"])

    def test_missing_resume_is_not_fabricated(self):
        result = analyze_resume_text("too short")
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["skills"]["present"], [])


if __name__ == "__main__":
    unittest.main()
