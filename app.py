import re
import joblib
import streamlit as st

st.set_page_config(page_title="Fake News Detector", page_icon="📰", layout="centered")

def preprocess_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

@st.cache_resource
def load_artifacts():
    model = joblib.load("model.joblib")
    vectorizer = joblib.load("vectorizer.joblib")
    return model, vectorizer

st.title("Fake News Detection System")
st.write("Enter a news headline and optional article text to check Fake vs. Real probability.")

try:
    model, vectorizer = load_artifacts()
except Exception as e:
    st.error(f"Could not load model artifacts. Run fake_news_detection.py first. Details: {e}")
    st.stop()

headline = st.text_input("News Headline", placeholder="e.g., RBI keeps repo rate unchanged after review meeting")
body = st.text_area("Article Body (Optional)", height=120, placeholder="Paste article text here...")

if st.button("Analyze News"):
    combined = f"{headline} {body}".strip()
    if not combined:
        st.warning("Please enter a headline or article text first.")
    else:
        cleaned = preprocess_text(combined)
        vec = vectorizer.transform([cleaned])
        pred = int(model.predict(vec)[0])
        fake_prob = float(model.predict_proba(vec)[0][1])

        if pred == 1:
            st.error(f"Prediction: FAKE NEWS | Fake Probability: {fake_prob * 100:.2f}%")
        else:
            real_prob = (1.0 - fake_prob) * 100
            st.success(f"Prediction: REAL NEWS | Real Confidence: {real_prob:.2f}% (Fake Prob: {fake_prob * 100:.2f}%)")