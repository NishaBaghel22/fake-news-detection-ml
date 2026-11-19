# Fake News Detection System (ML with AI Internship Project)

An end-to-end NLP and Machine Learning pipeline for classifying news articles as **Fake** or **Real**, complete with exploratory data analysis, model benchmarking, cross-validation, feature explainability, unsupervised clustering exploration, and saved model inference.

## Course Topics Covered

- **Introduction to ML & Data Fundamentals:** Train-test splitting (`stratify`), deduplication, and supervised vs. unsupervised paradigms.
- **Python Programming & Data Analytics/Visualization:** `pandas`, `numpy`, `matplotlib`, `seaborn` for cleaning, metrics, and plots (`eda_overview.png`, `confusion_matrix.png`).
- **Data Analytics using AI Tools:** Assisted in rapid prototyping, metric verification, and edge-case testing.
- **Supervised Learning (Classification & Probability):** Compared **Logistic Regression** (with probability confidence score), **Multinomial Naive Bayes**, and **LinearSVC** using Stratified K-Fold cross-validation.
- **Unsupervised Learning (Clustering):** Applied **K-Means** on TF-IDF features to inspect unlabeled text grouping.

## How to Run

```bash
pip install pandas numpy matplotlib seaborn scikit-learn joblib
python fake_news_detection.py
```
