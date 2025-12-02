"""
Test script to verify the model produces different outputs for different resume types
"""
from pipeline import analyze_resume_text

# Test Resume 1: Data Analyst
data_analyst_resume = """
JOHN DOE
Email: john@example.com | Phone: 123-456-7890

SUMMARY
Experienced Data Analyst with strong expertise in data visualization and analysis.
Proficient in Excel, SQL, Power BI, and Tableau. 

SKILLS
- Excel: Advanced pivot tables, VLOOKUP, data analysis
- SQL: Complex queries, JOIN operations, database optimization
- Power BI: Dashboard creation, DAX formulas, report design
- Tableau: Interactive visualizations, story telling
- Data Cleaning: Pandas, data quality assurance
- Statistics: Hypothesis testing, regression analysis

EXPERIENCE
Senior Data Analyst at Tech Company (2020-Present)
- Created Power BI dashboards for C-suite executives
- Optimized SQL queries improving performance by 40%
- Performed statistical analysis on customer data
- Cleaned and validated 5M+ records using Python

Data Analyst at StartUp (2018-2020)
- Built Tableau visualizations for business intelligence
- Developed Excel reports for monthly KPIs
- Created data cleaning pipelines

EDUCATION
BS in Statistics, University (2018)
"""

# Test Resume 2: Software Developer
developer_resume = """
JANE SMITH
Email: jane@example.com | Phone: 987-654-3210

SUMMARY
Full-stack software developer with expertise in modern web technologies.
Experienced in Python, Django, React, and API development.

SKILLS
- Python: 5+ years experience, Flask, Django frameworks
- Django: RESTful APIs, ORM, middleware
- Flask: Microservices, blueprints
- JavaScript: ES6+, async/await
- React: Component design, hooks, state management
- SQL: Database design, query optimization
- Git: Version control, branching strategies
- HTML/CSS: Responsive design, Bootstrap
- APIs: RESTful design, authentication, documentation

EXPERIENCE
Senior Developer at Web Company (2021-Present)
- Built Django REST APIs serving 1M+ requests daily
- Developed React frontend components
- Implemented Git workflow for team of 8 developers
- Optimized database queries using SQL indexing

Python Developer at Agency (2019-2021)
- Created Flask microservices for payment processing
- Wrote HTML/CSS for responsive web design
- Collaborated on JavaScript projects

EDUCATION
BS in Computer Science, University (2019)
"""

# Test Resume 3: UI/UX Designer
designer_resume = """
ALEX JOHNSON
Email: alex@example.com | Phone: 555-123-4567

SUMMARY
Creative UI/UX Designer specializing in user-centered design and prototyping.
Expert in Figma, wireframing, and design systems.

SKILLS
- Figma: Component libraries, prototyping, design systems
- Wireframe: Information architecture, user flows
- Prototype: Interactive prototypes, usability testing
- User Research: User interviews, surveys, personas
- UX Writing: Microcopy, tone of voice, content strategy
- Design Systems: Style guides, component documentation
- Interaction Design: Animation principles, micro-interactions

EXPERIENCE
Lead UX Designer at Design Studio (2021-Present)
- Created comprehensive design systems using Figma
- Conducted user research and testing
- Wireframed 20+ projects using information architecture principles
- Mentored junior designers on UX writing best practices

UX Designer at Tech Startup (2019-2021)
- Built interactive prototypes in Figma
- Created user flows and wireframes
- Researched user needs through interviews

EDUCATION
BFA in Graphic Design, University (2019)
"""

# Test Resume 4: Machine Learning Engineer
ml_resume = """
SARAH CHEN
Email: sarah@example.com | Phone: 222-333-4444

SUMMARY
Machine Learning Engineer with expertise in model development and data science.
Proficient in Python, scikit-learn, pandas, and numpy.

SKILLS
- Python: Advanced programming, OOP, decorators
- Pandas: Data manipulation, time series analysis
- NumPy: Array operations, numerical computing
- Scikit-learn: Classification, regression, clustering algorithms
- Training Models: Cross-validation, hyperparameter tuning
- Feature Engineering: Feature selection, dimensionality reduction
- Data Analysis: Statistical analysis, data exploration

EXPERIENCE
ML Engineer at AI Company (2020-Present)
- Built ML pipelines using scikit-learn for customer churn prediction
- Performed feature engineering on 100+ features
- Trained and tuned models achieving 94% accuracy
- Used pandas for extensive data manipulation

Data Scientist at Research Lab (2018-2020)
- Developed numpy-based algorithms for optimization
- Created ML models using scikit-learn
- Analyzed datasets with statistical methods

EDUCATION
MS in Data Science, University (2018)
"""

def run_tests():
    print("=" * 80)
    print("TESTING MODEL WITH DIFFERENT RESUME TYPES")
    print("=" * 80)
    
    test_cases = [
        ("Data Analyst", data_analyst_resume),
        ("Software Developer", developer_resume),
        ("UI/UX Designer", designer_resume),
        ("Machine Learning Engineer", ml_resume),
    ]
    
    for expected_category, resume_text in test_cases:
        print(f"\n{'='*80}")
        print(f"Testing: {expected_category}")
        print(f"{'='*80}")
        
        result = analyze_resume_text(resume_text)
        
        print(f"\nDetected Category: {result['category']}")
        print(f"Expected Category: {expected_category}")
        print(f"\nPresent Skills ({len(result['skills']['present'])}): {result['skills']['present']}")
        print(f"Missing Skills ({len(result['missing_skills'])}): {result['missing_skills']}")
        print(f"\nATS Score: {result['ats_score']}")
        print(f"Match Score: {result['match_score']}")
        print(f"\nBest Job Match: {result['best_job']['job_title'] if result['best_job'] else 'None'}")
        print(f"Top Keywords: {result['explanations']['top_keywords']}")
        print(f"\nExplanation: {result['explanations']['why_missing']}")

if __name__ == "__main__":
    run_tests()
