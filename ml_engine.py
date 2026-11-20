import re
from urllib.parse import quote_plus
import joblib
import streamlit as st

PHRASE_PATTERNS = [
    ("share this", 12),
    ("forward this", 12),
    ("before it gets deleted", 18),
    ("media won't show", 18),
    ("100% true", 14),
    ("shocking truth", 14),
    ("free recharge", 16),
    ("free rs", 12),
    ("free ₹", 12),
    ("breaking", 8),
    ("urgent", 8),
    ("otp", 10),
    ("click the link", 10),
]

HOAX_TEMPLATES = [
    ("₹2000 note GPS-chip hoax", {"2000", "note", "nano", "gps", "chip", "tracking"}),
    ("Free recharge scam", {"free", "recharge", "jio", "airtel", "link"}),
    ("KYC-update account-blocked scam", {"kyc", "update", "account", "blocked", "suspended", "link"}),
    ("PM scheme registration link", {"pm", "yojana", "registration", "link", "free", "apply"}),
]

SOURCE_KEYWORDS = re.compile(
    r"according to|said|official|statement|pti|ani|ministry|police|reported|rbi",
    re.IGNORECASE,
)

VERIFY_SITES = [
    ("PIB Fact Check", "factcheck.pib.gov.in"),
    ("BOOM", "boomlive.in"),
    ("Alt News", "altnews.in"),
    ("Times of India", "timesofindia.indiatimes.com"),
    ("The Hindu", "thehindu.com"),
    ("Indian Express", "indianexpress.com"),
    ("NDTV", "ndtv.com"),
]


def clean_for_model(text: str) -> str:
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


@st.cache_resource
def load_ml_bundle():
    model = joblib.load("model.joblib")
    vectorizer = joblib.load("vectorizer.joblib")
    return model, vectorizer


def evaluate_news_claim(headline: str, body: str, source: str, platform: str, model, vectorizer) -> dict:
    full_text = f"{headline.strip()}. {body.strip()}".strip() if headline.strip() else body.strip()
    lower_t = full_text.lower()

    risk_score = 0
    red_flags = []
    for phrase, weight in PHRASE_PATTERNS:
        if phrase in lower_t:
            risk_score += weight
            red_flags.append(phrase)

    if full_text.count("!") >= 3:
        risk_score += 8
        red_flags.append("many exclamation marks")

    tokens = set(re.findall(r"[a-z0-9₹]+", lower_t))
    for name, keywords in HOAX_TEMPLATES:
        hits = len(tokens.intersection(keywords))
        if hits >= 2 and (hits / len(keywords)) >= 0.5:
            risk_score += 20
            red_flags.append(f"hoax pattern: {name}")
            break

    has_source = bool(SOURCE_KEYWORDS.search(full_text)) or (
        len(source.strip()) > 2 and not re.search(r"whatsapp|forward|unknown|group", source, re.I)
    )
    if not has_source:
        risk_score += 10
        red_flags.append("no verified source named")

    risk_score = min(100, risk_score)

    cleaned = clean_for_model(full_text)
    vec = vectorizer.transform([cleaned])
    pred = int(model.predict(vec)[0])

    if hasattr(model, "predict_proba"):
        fake_prob = float(model.predict_proba(vec)[0][1])
    elif hasattr(model, "decision_function"):
        score = float(model.decision_function(vec)[0])
        fake_prob = 1.0 / (1.0 + pow(2.718281828, -score))
    else:
        fake_prob = 0.85 if pred == 1 else 0.15

    blended_fake = min(0.99, max(0.01, 0.7 * fake_prob + 0.3 * (risk_score / 100.0)))

    if 0.43 <= blended_fake <= 0.57 or (not has_source and platform in {"WhatsApp", "Facebook", "Other"} and not red_flags):
        verdict = "Likely Unverified"
        cls = "Unverified"
        confidence = round(max(45.0, min(75.0, (1.0 - abs(blended_fake - 0.5) * 2) * 80)), 1)
        reason = "NewsCheckr found limited source attribution or near-threshold signals, so this claim should be verified with trusted sources."
    elif blended_fake >= 0.65:
        verdict = "Likely Fake"
        cls = "Fake"
        confidence = round(min(96.0, max(55.0, blended_fake * 100)), 1)
        reason = "Model probability and sensational, urgency, or hoax indicators suggest this claim is likely false or manipulated."
    elif blended_fake >= 0.55:
        verdict = "Likely Misleading"
        cls = "Misleading"
        confidence = round(min(90.0, max(52.0, blended_fake * 100)), 1)
        reason = "Some phrasing or missing context suggests distortion or exaggerated framing around the claim."
    else:
        verdict = "Likely Real"
        cls = "Real"
        confidence = round(min(96.0, max(55.0, (1.0 - blended_fake) * 100)), 1)
        reason = "Text patterns and structure align more closely with credible reporting, though you should still verify via trusted outlets."

    query = headline.strip() or full_text[:90]
    verify_links = [
        (name, f"https://www.google.com/search?q={quote_plus(f'site:{domain} {query}')}")
        for name, domain in VERIFY_SITES
    ]

    return {
        "verdict": verdict,
        "cls": cls,
        "confidence": confidence,
        "fake_prob": round(blended_fake * 100, 1),
        "risk_score": risk_score,
        "red_flags": list(dict.fromkeys(red_flags)),
        "reason": reason,
        "verify_links": verify_links,
    }