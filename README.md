# NewsCheckr 🛡️

**NewsCheckr** is a simple, easy-to-use web application that helps users check whether an English news headline, article, or forwarded message is **Likely Real**, **Likely Fake**, **Likely Misleading**, or **Likely Unverified**.

You do not need any technical or Machine Learning knowledge to use it—just paste a news headline and message, select where you saw it, and click **Check News**.

---

## ✨ What NewsCheckr Does

- **Check News Claims:** Enter a news headline, full text, optional source, and platform (WhatsApp, Facebook, X / Twitter, News site, or Other) to evaluate credibility.
- **Clear Verdict & Confidence Score:** Displays an easy-to-read badge (`Likely Real`, `Likely Fake`, `Likely Misleading`, or `Likely Unverified`) along with a confidence percentage and explanation.
- **Red Flag Detection:** Highlights common warning signs such as urgency/forwarding phrases, known hoax patterns, or missing source attribution.
- **Trusted Fact-Check Links:** Provides one-click search links to verify the claim on trusted fact-checking and news websites (such as PIB Fact Check, BOOM, Alt News, and major news outlets).
- **Account & Check History:** Lets users create an account, log in, and view their previously checked news items.

---

## 🗂️ Project Structure

```text
fake_news_detector/
├── app.py                  # Main Streamlit web application & navigation
├── ui_pages.py             # User interface pages (Home, Check News, History, Account)
├── ml_engine.py            # Prediction logic, text signal checks & verification links
├── storage_helper.py       # Local JSON storage for user accounts and check history
├── fake_news_detection.py  # Model training and evaluation script
├── model.joblib            # Trained classification model
├── vectorizer.joblib       # Saved TF-IDF text vectorizer
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```
