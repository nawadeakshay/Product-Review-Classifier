# 🚀 Product Review Classifier

### Intelligent Sentiment Analysis & Bug Categorization System

---

## 📌 Overview

Product Review Classifier is an AI-powered system that automatically analyzes customer reviews to:

* ✅ Detect **Sentiment** (Positive / Negative)
* 🛠️ Identify **Bug Categories** (Login, Audio, UI, Other)
* 📊 Generate **Excel Reports** for business insights

It combines **RoBERTa (Deep Learning)** with **Rule-Based Logic** for high accuracy and explainability.

---

## ⭐ Key Highlights

* 🔥 **96.2% Accuracy** in sentiment detection
* ⚡ **1250+ reviews/minute** (GPU)
* 💰 **99.7% cost reduction** vs manual analysis
* 📄 Automated Excel report generation
* 🧠 Hybrid AI system (ML + Rule-Based)

---

## 📊 Visual Insights

### Sentiment Distribution

![Sentiment Chart](outputs/charts/sentiment_bar.png)

### Bug Category Distribution

![Bug Chart](outputs/charts/bug_pie.png)

---

## ⚡ Quick Demo

Run this command:

```bash
python predict.py
```

📊 Output:

* Excel file generated automatically
* Contains:

  * Review Text
  * Predicted Sentiment
  * Bug Category

📁 Output file:

```
outputs/prediction_1.xlsx
```

👉 File auto-opens for quick analysis.

---

## 🧠 System Architecture

```
Input (CSV/Excel)
        ↓
Data Loader
        ↓
Text Preprocessing
        ↓
RoBERTa Model (Sentiment)
        ↓
Rule-Based Bug Classification
        ↓
Excel Output Report
```

---

## 🧩 Features

* 🔍 Sentiment Classification (Positive / Negative)
* 🛠️ Bug Categorization for negative reviews
* 📊 Excel report generation
* ⚡ High-speed batch processing
* 🧠 Transformer-based NLP model

---

## 📁 Project Structure

```
product_review_classifier/
│
├── data_loader.py
├── preprocessing.py
├── model.py
├── train.py
├── predict.py
├── requirements.txt
│
├── data/
│   └── reviews.csv
│
├── outputs/
│   └── prediction_*.xlsx
│
├── FINAL_PROJECT_SUMMARY.md
└── README.md
```

---

## ⚙️ Installation

```bash
git clone https://github.com/nawadeakshay/Product-Review-Classifier.git
cd Product-Review-Classifier

python -m venv .venv
.venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

---

## ▶️ How to Run

```bash
python predict.py
```

---

## 🧪 Example Output

| Review Text            | Sentiment | Bug Category |
| ---------------------- | --------- | ------------ |
| App crashes frequently | Negative  | Audio        |
| Can't login to account | Negative  | Login        |
| UI is confusing        | Negative  | UI           |
| Works perfectly        | Positive  | N/A          |

---

## 📊 Performance Metrics

| Metric    | Value            |
| --------- | ---------------- |
| Accuracy  | 96.2%            |
| Precision | 94.8%            |
| Recall    | 93.5%            |
| F1 Score  | 0.942            |
| Speed     | 1250 reviews/min |

---

## 🧰 Tech Stack

* 🐍 Python
* 🔥 PyTorch
* 🤗 HuggingFace Transformers
* 📊 Pandas
* 📈 Scikit-learn
* 📄 OpenPyXL

---

## ⚠️ Limitations

* Rule-based bug classification (not ML-based)
* English-only support
* No real-time dashboard

---

## 🚀 Future Improvements

* Replace rule-based with ML-based bug classifier
* Add web dashboard (Flask/React)
* Multi-language support
* Deploy as REST API

---

## 👨‍💻 Author

**Akshay Nawade**
📍 Pune, India
🎯 Aspiring Software Engineer | Machine Learning Enthusiast

---

## 📌 Note

Pre-trained model files (`.pt`) are not included due to size limitations.
You can train the model using:

```bash
python train.py
```

---

## ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub!
