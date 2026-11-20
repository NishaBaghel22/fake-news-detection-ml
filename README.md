# NewsCheckr — Fake News Detection Web Application

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://fake-news-detection-ml-epmzkr3j9hv2jmoeuj46th.streamlit.app/)

**Live Demo:** [https://fake-news-detection-ml-epmzkr3j9hv2jmoeuj46th.streamlit.app/](https://fake-news-detection-ml-epmzkr3j9hv2jmoeuj46th.streamlit.app/)

## Overview

**NewsCheckr** is a web application built with Python, Streamlit, and scikit-learn that evaluates news headlines, article/message text, and source/platform context to classify claims as _Likely Real_, _Likely Fake_, _Likely Misleading_, or _Likely Unverified_. It combines a trained machine learning classifier with rule-based checks for urgency phrases, known hoax patterns, and source/platform context, while providing a confidence score, red-flag explanations, trusted verification search links, and check history.

## Key Features

- **Multi-Page Interface (`Home`, `Check News`, `History`, `Account`):** Clean navigation with custom orange-and-white styling and aligned action controls.
- **Structured Claim Input:** Dedicated inputs for headline, main text, optional claimed source, and platform selection (`WhatsApp`, `Facebook`, `X / Twitter`, `News site`, `Other`).
- **Two-Step Hybrid Evaluation:**
  1. Cleans and vectorizes text (`vectorizer.joblib`) to obtain a prediction from the trained `scikit-learn` model (`model.joblib`).
  2. Applies rule-based checks for urgency/forward phrasing, known hoax patterns, and missing or unverified source details to compute the final verdict and confidence percentage.
- **Verification Links:** Generates direct Google search links targeting fact-checking and news domains (such as PIB Fact Check, BOOM, Alt News, and news outlets) for further manual verification.
- **Account & History Tracking:** Supports user sign-up/login (with SHA-256 password hashing) and logs past checks with summary counts.

## Dataset & Model Notes

- Trained and evaluated using the **WELFake** dataset (from Zenodo, 72,134 raw articles; ~63,700 cleaned rows after removing missing and duplicate records), using TF-IDF vectorization and a `scikit-learn` classifier (`Logistic Regression`).

## Project Structure

```text
fake_news_detector/
├── app.py                  # Streamlit entry point, navigation, and session state
├── ml_engine.py            # Text cleaning, model loading, risk/hoax scoring, and verdicts
├── ui_pages.py             # Custom CSS styling and page rendering functions
├── storage_helper.py       # JSON persistence and password hashing helpers
├── model.joblib            # Trained scikit-learn classification model
├── vectorizer.joblib       # Fitted TF-IDF vectorizer
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```
