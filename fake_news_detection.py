import os
import re
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.cluster import KMeans
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)

# --- 1. DATA LOADING (WELFake) WITH SAFE FALLBACK ---
def load_news_data():
    csv_path = os.path.join("data", "WELFake_Dataset.csv")
    try:
        if os.path.isfile(csv_path) and os.path.getsize(csv_path) > 0:
            welfake = pd.read_csv(csv_path)
            welfake = welfake.dropna(subset=["label"])
            welfake["label"] = welfake["label"].astype(int)

            # Actual WELFake file mein: 0 = Real, 1 = Fake (is code ke jaisa hi), isliye flip nahi karna

            welfake = welfake[["title", "text", "label"]]
            return welfake, f"WELFake Dataset ({len(welfake)} rows)"
    except Exception as exc:
        print(f"WELFake load skipped ({exc}) -> using expanded starter dataset.")

    rows = [
        ("Breaking: Secret pill cures all diseases overnight without side effects", "Anonymous insiders claim doctors are hiding this miracle cure.", 1),
        ("SHOCKING: Moon landing was completely filmed in a studio", "Viral post claims NASA faked every mission with zero evidence.", 1),
        ("Government to give Rs 50,000 free cash to every citizen tomorrow", "Forward this message to 10 groups to claim instant transfer.", 1),
        ("Celebrity caught alien shifting on live TV broadcast", "Unverified clip circulates online with sensational claims.", 1),
        ("Miracle tea melts fat in 2 days with zero exercise", "Click link before health authorities ban this post.", 1),
        ("Secret document proves elections were rigged by invisible signals", "Unverified viral claim spreads across social media.", 1),
        ("URGENT: WhatsApp will charge money from tonight unless forwarded", "Hoax message warns users to share with contacts immediately.", 1),
        ("Scientists discover immortality water hidden in deep cave", "Sensational blog posts no peer-reviewed evidence or study.", 1),
        ("Banks freezing all savings accounts for maintenance this weekend", "Fake alert spreads panic without any official bank notice.", 1),
        ("Eat this single fruit before bed and lose 15 kg in a week", "Clickbait ad promises unrealistic weight loss overnight.", 1),
        ("Hidden microchip found inside currency notes claims viral video", "False rumor debunked by financial and technical experts.", 1),
        ("Exclusive leak reveals famous actor faked entire career", "Unverified gossip site publishes baseless rumor without sources.", 1),
        ("RBI keeps repo rate unchanged after MPC review meeting", "The Reserve Bank of India maintained status quo on policy rates following inflation assessment.", 0),
        ("ISRO successfully completes thermal vacuum test for satellite payload", "Engineers verified subsystem performance under simulated space conditions.", 0),
        ("Parliament passes bill to strengthen digital data protection rules", "Lawmakers debated privacy safeguards and compliance timelines during the session.", 0),
        ("Monsoon rainfall expected to remain near normal across central India", "Meteorological department released seasonal forecast based on ocean temperature models.", 0),
        ("Supreme Court schedules hearing on digital privacy petition next month", "Court registry issued notice to concerned authorities for response.", 0),
        ("Ministry of Education releases new academic calendar guidelines", "Officials outlined semester timelines and assessment schedules for institutions.", 0),
        ("Election Commission announces voter roll revision schedule for state", "Official notification details dates for claims, objections, and verification.", 0),
        ("State transport corporation adds electric buses on city routes", "Authorities stated new fleet aims to cut emissions and improve commuting.", 0),
        ("Health ministry updates vaccination advisory for seasonal flu", "Public health guidelines recommend hygiene measures and timely medical consultation.", 0),
        ("National stock index closes higher on gains in banking and IT stocks", "Market analysts cited steady quarterly earnings and institutional inflows.", 0),
        ("University grants commission publishes updated research fellowship norms", "Circular outlines eligibility criteria, stipend rules, and application deadlines.", 0),
        ("Railway board introduces additional express train for winter travel", "Timetable and booking details were published on official passenger portals.", 0),
    ]
    return pd.DataFrame(rows, columns=["title", "text", "label"]), "Expanded Starter Dataset (24 rows)"


df, source_name = load_news_data()

# --- 2. DATA FUNDAMENTALS & CLEANING ---
df["content"] = df["title"].fillna("") + " " + df["text"].fillna("")
df = df[df["content"].str.strip() != ""].drop_duplicates(subset=["content"]).reset_index(drop=True)
df["word_count"] = df["content"].str.split().str.len()
df["char_count"] = df["content"].str.len()

print("Source:", source_name)
print("Clean Shape:", df.shape)
print("Class Distribution:", df["label"].value_counts().to_dict())

# --- 3. DATA ANALYTICS & VISUALIZATION ---
fig, axes = plt.subplots(1, 2, figsize=(11, 4))
sns.countplot(x="label", data=df, ax=axes[0])
axes[0].set_title("Class Distribution (0 = Real, 1 = Fake)")
axes[0].set_xlabel("Label")
axes[0].set_ylabel("Count")

# Bahut lambe articles hata kar graph readable banaya
sns.histplot(data=df[df["word_count"] < 2000], x="word_count", hue="label", bins=30, kde=True, ax=axes[1])
axes[1].set_title("Word Count Distribution by Class")
axes[1].set_xlabel("Word Count")

plt.tight_layout()
plt.savefig("eda_overview.png", dpi=150)
plt.close()

# --- 4. TEXT PREPROCESSING & TF-IDF ---
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

df["clean_text"] = df["content"].apply(preprocess_text)

X_train, X_test, y_train, y_test = train_test_split(
    df["clean_text"], df["label"], test_size=0.25, random_state=42, stratify=df["label"]
)

# Bade dataset ke liye features 2000 se badha kar 5000 kiye
tfidf = TfidfVectorizer(max_features=5000, ngram_range=(1, 2), stop_words="english")
X_train_vec = tfidf.fit_transform(X_train)
X_test_vec = tfidf.transform(X_test)

# --- 5. SUPERVISED MODELS + STRATIFIED CROSS-VALIDATION ---
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
    "Multinomial NB": MultinomialNB(),
    "Linear SVC": LinearSVC(random_state=42),
}

cv_splits = min(4, max(2, int(y_train.value_counts().min())))
skf = StratifiedKFold(n_splits=cv_splits, shuffle=True, random_state=42)

summary_rows = []
for model_name, clf in models.items():
    print(f"Training {model_name}...")
    clf.fit(X_train_vec, y_train)
    preds = clf.predict(X_test_vec)
    cv_acc = cross_val_score(clf, X_train_vec, y_train, cv=skf, scoring="accuracy")
    summary_rows.append({
        "Model": model_name,
        "Test Acc": round(float(accuracy_score(y_test, preds)), 4),
        "Precision": round(float(precision_score(y_test, preds, zero_division=0)), 4),
        "Recall": round(float(recall_score(y_test, preds, zero_division=0)), 4),
        "F1": round(float(f1_score(y_test, preds, zero_division=0)), 4),
        "CV Mean": round(float(cv_acc.mean()), 4),
    })

print("\n--- Supervised Model Comparison ---")
print(pd.DataFrame(summary_rows).to_string(index=False))

best_model = models["Logistic Regression"]
y_pred = best_model.predict(X_test_vec)
print("\nClassification Report (Logistic Regression):\n")
print(classification_report(y_test, y_pred, target_names=["Real (0)", "Fake (1)"], zero_division=0))

# Top Fake & Real Indicator N-grams
vocab = np.array(tfidf.get_feature_names_out())
weights = best_model.coef_[0]
top_fake_words = list(vocab[np.argsort(weights)[-6:][::-1]])
top_real_words = list(vocab[np.argsort(weights)[:6]])
print("Top Fake Indicators:", top_fake_words)
print("Top Real Indicators:", top_real_words)

# Save Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(5, 4))
sns.heatmap(
    cm, annot=True, fmt="d", cmap="Blues",
    xticklabels=["Pred Real", "Pred Fake"],
    yticklabels=["Actual Real", "Actual Fake"]
)
plt.title("Confusion Matrix - Logistic Regression")
plt.tight_layout()
plt.savefig("confusion_matrix.png", dpi=150)
plt.close()

# --- 6. MODEL PERSISTENCE (JOBLIB) ---
joblib.dump(best_model, "model.joblib")
joblib.dump(tfidf, "vectorizer.joblib")
print("\nSaved artifacts: model.joblib, vectorizer.joblib, eda_overview.png, confusion_matrix.png")

# --- 7. UNSUPERVISED LEARNING (K-MEANS) ---
n_clusters = min(3, X_train_vec.shape[0])
# n_init=3 rakha hai taaki bade dataset par jaldi chale
kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=3)
cluster_ids = kmeans.fit_predict(X_train_vec)
print("K-Means Cluster Counts:", pd.Series(cluster_ids).value_counts().to_dict())

# --- 8. LIVE PREDICTION + OPTIONAL INTERACTIVE PROMPT ---
def predict_from_saved(headline, body=""):
    loaded_model = joblib.load("model.joblib")
    loaded_vec = joblib.load("vectorizer.joblib")
    cleaned = preprocess_text(f"{headline} {body}")
    vec = loaded_vec.transform([cleaned])
    pred = int(loaded_model.predict(vec)[0])
    fake_prob = float(loaded_model.predict_proba(vec)[0][1])
    status = "FAKE NEWS" if pred == 1 else "REAL NEWS"
    confidence = fake_prob if pred == 1 else (1.0 - fake_prob)
    return {
        "prediction": status,
        "confidence": f"{confidence * 100:.2f}%",
        "fake_probability": round(fake_prob, 4),
    }

print("\n--- Sample Inference (Using Saved Model) ---")
print("Test 1:", predict_from_saved("Shocking secret viral trick exposed", "Click here before it gets deleted"))
print("Test 2:", predict_from_saved("Finance ministry releases quarterly economic growth report", "Officials published updated GDP and trade figures after review"))

# Interactive test if user wants to type custom news in terminal (press Enter on empty line to skip)
try:
    user_headline = input("\nEnter a news headline to test (or press Enter to finish): ").strip()
    if user_headline:
        user_body = input("Enter news body (optional): ").strip()
        print("Result:", predict_from_saved(user_headline, user_body))
except EOFError:
    pass