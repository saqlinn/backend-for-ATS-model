import json
import os

def create_dataset():
    data_folder = "data"
    os.makedirs(data_folder, exist_ok=True)

    dataset = [
        {
            "text": "Experienced Python developer skilled in Django, REST APIs, backend engineering and SQL.",
            "category": "Software Developer"
        },
        {
            "text": "Digital marketer experienced in SEO, Google Ads, Facebook Ads, email marketing, and analytics.",
            "category": "Digital Marketing"
        },
        {
            "text": "UI/UX designer with experience in Figma, wireframes, user flows, prototyping, and usability testing.",
            "category": "UI/UX Designer"
        },
        {
            "text": "Data analyst skilled in Power BI, Excel, SQL, and data visualization with dashboards.",
            "category": "Data Analyst"
        },
        {
            "text": "Machine learning engineer experienced in training ML models, Python, pandas, and scikit-learn.",
            "category": "Machine Learning"
        }
    ]

    output_path = os.path.join(data_folder, "dataset.jsonl")

    with open(output_path, "w", encoding="utf-8") as f:
        for record in dataset:
            f.write(json.dumps(record) + "\n")

    print("Dataset created successfully!")

if __name__ == "__main__":
    create_dataset()
