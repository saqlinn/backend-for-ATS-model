"""Configurable role metadata used by classification and target matching."""

TAXONOMY_VERSION = "2026.10"

_COMMON = ["communication", "leadership", "problem solving", "project management"]

ROLE_TAXONOMY = {
    "Software Engineer": {"domain": "Technology", "aliases": ["software developer", "software engineer"], "skills": ["python", "java", "c++", "git", "api", "sql"]},
    "Full Stack Developer": {"domain": "Technology", "aliases": ["full stack", "fullstack"], "skills": ["javascript", "react", "node.js", "html", "css", "api", "sql"]},
    "Frontend Developer": {"domain": "Technology", "aliases": ["front end", "frontend"], "skills": ["html", "css", "javascript", "react", "angular", "vue"]},
    "Backend Developer": {"domain": "Technology", "aliases": ["back end", "backend"], "skills": ["python", "java", "django", "flask", "node.js", "api", "sql"]},
    "Mobile Developer": {"domain": "Technology", "aliases": ["mobile engineer"], "skills": ["android", "ios", "swift", "kotlin", "react native", "flutter"]},
    "Data Analyst": {"domain": "Data", "aliases": ["data analyst"], "skills": ["excel", "sql", "power bi", "tableau", "statistics", "data visualization"]},
    "Business Data Analyst": {"domain": "Data", "aliases": ["business data analyst"], "skills": ["sql", "excel", "statistics", "requirements gathering", "data visualization"]},
    "Business Intelligence Analyst": {"domain": "Data", "aliases": ["bi analyst", "business intelligence"], "skills": ["sql", "power bi", "tableau", "data visualization", "etl"]},
    "Data Scientist": {"domain": "Data", "aliases": ["data science", "data scientist"], "skills": ["python", "pandas", "numpy", "scikit-learn", "statistics", "machine learning", "model evaluation", "experimentation"]},
    "Machine Learning Engineer": {"domain": "AI/ML", "aliases": ["ml engineer", "machine learning engineer", "machine learning"], "skills": ["python", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "feature engineering", "model evaluation", "hyperparameter tuning", "random forest"]},
    "AI Engineer": {"domain": "AI/ML", "aliases": ["ai/ml engineer", "ai ml engineer", "artificial intelligence engineer", "ai engineer"], "skills": ["python", "machine learning", "deep learning", "tensorflow", "pytorch", "model evaluation", "fastapi"]},
    "Generative AI Engineer": {"domain": "AI/ML", "aliases": ["gen ai engineer", "generative ai"], "skills": ["python", "llm", "prompt engineering", "retrieval augmented generation", "embeddings", "transformers"]},
    "NLP Engineer": {"domain": "AI/ML", "aliases": ["nlp engineer", "natural language processing"], "skills": ["python", "nlp", "nltk", "spacy", "transformers", "text classification", "model evaluation"]},
    "Computer Vision Engineer": {"domain": "AI/ML", "aliases": ["computer vision engineer", "computer vision"], "skills": ["python", "opencv", "pytorch", "tensorflow", "image processing", "model evaluation"]},
    "Data Engineer": {"domain": "Data", "aliases": ["data engineering"], "skills": ["python", "sql", "spark", "etl", "airflow", "data pipelines"]},
    "Database Administrator": {"domain": "Technology", "aliases": ["database administrator", "dba"], "skills": ["sql", "postgresql", "mysql", "backup", "database performance"]},
    "QA Engineer": {"domain": "Quality", "aliases": ["quality assurance", "qa engineer"], "skills": ["test planning", "manual testing", "regression testing", "jira"]},
    "Test Automation Engineer": {"domain": "Quality", "aliases": ["automation tester", "test automation"], "skills": ["selenium", "pytest", "cypress", "api testing", "test automation"]},
    "Cybersecurity Analyst": {"domain": "Security", "aliases": ["cyber security", "security analyst"], "skills": ["siem", "penetration testing", "network security", "incident response"]},
    "Cloud Engineer": {"domain": "Cloud", "aliases": ["cloud computing"], "skills": ["aws", "azure", "gcp", "docker", "kubernetes", "terraform"]},
    "DevOps Engineer": {"domain": "Cloud", "aliases": ["dev ops"], "skills": ["docker", "kubernetes", "ci/cd", "terraform", "linux", "jenkins"]},
    "Network Engineer": {"domain": "Infrastructure", "aliases": ["networking"], "skills": ["tcp/ip", "routing", "switching", "firewalls", "cisco"]},
    "IT Support Engineer": {"domain": "IT", "aliases": ["technical support", "it support"], "skills": ["troubleshooting", "windows", "linux", "help desk", "networking"]},
    "Electronics Engineer": {"domain": "Engineering", "aliases": ["electronics"], "skills": ["embedded systems", "microcontrollers", "pcb", "circuit design", "embedded c"]},
    "Embedded Systems Engineer": {"domain": "Engineering", "aliases": ["embedded engineer"], "skills": ["embedded c", "c", "microcontrollers", "rtos", "firmware"]},
    "VLSI Engineer": {"domain": "Engineering", "aliases": ["vlsi", "asic"], "skills": ["verilog", "vhdl", "rtl", "fpga", "asic"]},
    "Electrical Engineer": {"domain": "Engineering", "aliases": ["electrical"], "skills": ["matlab", "power systems", "circuit design", "autocad"]},
    "Civil Engineer": {"domain": "Engineering", "aliases": ["civil"], "skills": ["autocad", "structural analysis", "construction", "site supervision"]},
    "Structural Engineer": {"domain": "Engineering", "aliases": ["structural"], "skills": ["structural analysis", "staad", "revit", "autocad", "concrete design"]},
    "Site Engineer": {"domain": "Engineering", "aliases": ["site supervision"], "skills": ["construction", "site supervision", "autocad", "safety"]},
    "Mechanical Engineer": {"domain": "Engineering", "aliases": ["mechanical"], "skills": ["autocad", "solidworks", "cad", "manufacturing", "thermodynamics"]},
    "Chemical Engineer": {"domain": "Engineering", "aliases": ["chemical"], "skills": ["process design", "chemical safety", "process simulation", "quality control"]},
    "Business Analyst": {"domain": "Business", "aliases": ["business analysis"], "skills": ["requirements gathering", "sql", "excel", "stakeholder management", "process improvement"]},
    "Business Development Executive": {"domain": "Business", "aliases": ["business development", "bde"], "skills": ["sales", "lead generation", "client relationship", "negotiation"]},
    "Operations Analyst": {"domain": "Business", "aliases": ["operations"], "skills": ["excel", "process improvement", "reporting", "data analysis"]},
    "Accountant": {"domain": "Finance", "aliases": ["accounting"], "skills": ["accounting", "financial reporting", "tax", "excel", "bookkeeping"]},
    "Financial Analyst": {"domain": "Finance", "aliases": ["finance analyst"], "skills": ["financial modeling", "excel", "financial analysis", "forecasting"]},
    "HR Executive": {"domain": "People", "aliases": ["human resources", "hr executive"], "skills": ["recruitment", "payroll", "employee relations", "hris"]},
    "Digital Marketing Specialist": {"domain": "Marketing", "aliases": ["digital marketing", "digital marketer"], "skills": ["seo", "sem", "google ads", "content marketing", "email marketing", "analytics"]},
    "Sales Executive": {"domain": "Business", "aliases": ["sales representative"], "skills": ["sales", "lead generation", "crm", "negotiation"]},
    "Supply Chain Analyst": {"domain": "Operations", "aliases": ["supply chain"], "skills": ["inventory", "procurement", "logistics", "excel", "forecasting"]},
    "Healthcare Data Analyst": {"domain": "Healthcare Data", "aliases": ["healthcare analytics"], "skills": ["sql", "statistics", "healthcare", "data visualization"]},
    "Teacher": {"domain": "Education", "aliases": ["educator", "teaching"], "skills": ["lesson planning", "curriculum", "classroom management"]},
    "Research Assistant": {"domain": "Research", "aliases": ["researcher"], "skills": ["research", "data analysis", "literature review", "statistics"]},
    "UI/UX Designer": {"domain": "Design", "aliases": ["ux designer", "ui designer", "user experience"], "skills": ["figma", "wireframing", "prototyping", "user research", "usability testing"]},
    "Graphic Designer": {"domain": "Design", "aliases": ["graphic design"], "skills": ["photoshop", "illustrator", "indesign", "typography", "branding"]},
    "Technical Writer": {"domain": "Writing", "aliases": ["technical writing"], "skills": ["technical writing", "documentation", "api documentation", "markdown"]},
}

for _metadata in ROLE_TAXONOMY.values():
    _metadata["skills"] = list(dict.fromkeys(_metadata["skills"]))
    _metadata["competencies"] = list(_COMMON)
