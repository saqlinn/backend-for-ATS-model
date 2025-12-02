import os
import json
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report
import joblib

def train_resume_classifier():
    # Load dataset JSONL
    dataset_path = "data/dataset.jsonl"
    rows = []

    with open(dataset_path, "r", encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))

    df = pd.DataFrame(rows)

    # Using only the resume text + category
    df = df[["text", "category"]]


    # Convert categories to numeric labels
    label_encoder = LabelEncoder()
    df["label"] = label_encoder.fit_transform(df["category"])

    # TF-IDF vectorization
    vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
    X = vectorizer.fit_transform(df["text"])
    y = df["label"]

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train Naive Bayes classifier
    model = MultinomialNB()
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    print("\nClassification Report:\n")
    print(classification_report(
        y_test, 
        y_pred, 
        labels=label_encoder.transform(label_encoder.classes_),
        target_names=label_encoder.classes_,
        zero_division=0
))


    # Save models
    joblib.dump(model, "models/classifier_model.pkl")
    joblib.dump(vectorizer, "models/tfidf_vectorizer.pkl")
    joblib.dump(label_encoder, "models/label_encoder.pkl")

    print("\nClassifier training completed! Models saved in /models folder.\n")

if __name__ == "__main__":
    os.makedirs("models", exist_ok=True)
    train_resume_classifier()
