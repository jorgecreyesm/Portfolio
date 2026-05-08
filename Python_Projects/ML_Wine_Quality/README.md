# 🍷 Wine Quality Predictor: ML Classification

## 📁 Project Structure

This folder contains the **end-to-end ML pipeline** from exploratory analysis to an interactive prediction app:

### 🌐 Interactive App (Primary)
- **`app.py`** — Streamlit application with 5 interactive pages
- **`requirements.txt`** — Python dependencies
- **`.streamlit/config.toml`** — App styling and configuration

### 📊 Research & Modeling Notebooks
- **`01_EDA.ipynb`** — Exploratory data analysis
  - Dataset overview and class balance inspection
  - Feature distributions and correlation analysis
  - Business context framing (cost of sensory testing)

- **`02_Model_Training.ipynb`** — Model training and evaluation
  - Trains 4 classifiers: Logistic Regression, Random Forest, SVM, XGBoost
  - Compares accuracy, F1, precision, recall, and ROC-AUC
  - Saves best model to `models/`

### 📦 Model Artifacts
- **`models/best_model.pkl`** — Trained Random Forest classifier
- **`models/model_metadata.pkl`** — Model name, feature columns, scaling flag

### 📂 Data
- **`data/winequality-combined.csv`** — 6,497 red and white wines with 11 chemical features

---

## 🚀 Running the App

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 🧠 The Problem

Wine quality is traditionally assessed by trained sensory panels — expensive, subjective, and slow.
This project tests whether **11 measurable chemical properties** alone can reliably predict whether a wine is good or bad.

---

## 📊 Dataset

| Property | Value |
|---|---|
| Source | UCI Wine Quality Dataset |
| Total Wines | 6,497 |
| Red Wines | 1,599 |
| White Wines | 4,898 |
| Features | 11 physicochemical properties |
| Target | Quality score (3–9) → binarized: Good (≥6) vs Bad (<6) |
| Class Balance | 63% Good / 37% Bad |

**Features:** fixed acidity, volatile acidity, citric acid, residual sugar, chlorides, free sulfur dioxide, total sulfur dioxide, density, pH, sulphates, alcohol

---

## 🤖 Model Results

| Model | Test Accuracy | F1 Score | ROC-AUC |
|---|---|---|---|
| Logistic Regression | 73.4% | 0.800 | 0.805 |
| SVM | 77.9% | 0.834 | 0.839 |
| XGBoost | 81.6% | 0.858 | 0.884 |
| **Random Forest ★** | **83.8%** | **0.875** | **0.904** |

**Best Model:** Random Forest — selected by F1 score.

> **Note:** Random Forest achieves 100% training accuracy, indicating overfitting. Despite this, test performance is strong. Future work: hyperparameter tuning with GridSearchCV.

---

## 🔑 Key Findings

- **Alcohol** is the strongest predictor of quality — higher alcohol wines score better
- **Volatile acidity** is the strongest negative driver — high levels produce a vinegar-like taste
- **Sulphates** and **density** round out the top 4 most important features
- Chemical properties alone predict wine quality with 83.8% accuracy

---

## ☁️ Live Deployment

The app is deployed on **Streamlit Cloud** and accessible publicly.

Get the URL from your Streamlit Cloud dashboard at https://share.streamlit.io

---

## 🛠 Tools

Python · scikit-learn · XGBoost · Streamlit · pandas · matplotlib · joblib

**Author:** Jorge Reyes-Ornelas
*Data Analyst | Wine Operations Specialist | MS Data Analytics Candidate*
