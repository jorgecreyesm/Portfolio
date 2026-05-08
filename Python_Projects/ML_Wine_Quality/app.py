"""
Wine Quality Predictor: Interactive Streamlit App
ML-powered wine quality classification using chemical properties

Author: Jorge Reyes-Ornelas
Model: Random Forest Classifier (ROC-AUC: 0.90)
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import joblib
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# PAGE CONFIG
st.set_page_config(
    page_title="Wine Quality Predictor",
    page_icon="🍷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# STYLING
st.markdown("""
    <style>
    .header-section {
        border-bottom: 3px solid #8B0000;
        padding-bottom: 15px;
        margin-bottom: 25px;
    }
    .insight-box {
        background-color: #fdf0f0;
        padding: 15px;
        border-left: 4px solid #8B0000;
        border-radius: 5px;
        margin: 15px 0;
    }
    .good-wine {
        background-color: #eafaf1;
        padding: 20px;
        border-left: 6px solid #27AE60;
        border-radius: 8px;
        font-size: 18px;
    }
    .bad-wine {
        background-color: #fdf2f2;
        padding: 20px;
        border-left: 6px solid #C0392B;
        border-radius: 8px;
        font-size: 18px;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# LOAD ARTIFACTS
# ============================================================================

BASE_DIR = Path(__file__).parent

@st.cache_resource
def load_model():
    models_dir = BASE_DIR / 'models'
    metadata = joblib.load(models_dir / 'model_metadata.pkl')
    model = joblib.load(models_dir / 'best_model.pkl')
    scaler = None
    if metadata['needs_scaling']:
        scaler = joblib.load(models_dir / 'scaler.pkl')
    return model, metadata, scaler

@st.cache_data
def load_data():
    df = pd.read_csv(BASE_DIR / 'data' / 'winequality-combined.csv')
    df['quality_label'] = (df['quality'] >= 6).astype(int)
    return df

model, metadata, scaler = load_model()
df = load_data()

feature_cols = metadata['feature_columns']
model_name = metadata['model_name']
needs_scaling = metadata['needs_scaling']

# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================

st.sidebar.markdown("# 🍷 Navigation")
page = st.sidebar.radio(
    "Select Section:",
    ["🍷 Overview", "🔬 Wine Predictor", "📊 Feature Importance", "📈 Model Performance", "💡 About"]
)

# ============================================================================
# PAGE: OVERVIEW
# ============================================================================

if page == "🍷 Overview":
    st.markdown('<div class="header-section"><h1>🍷 Wine Quality Predictor</h1></div>',
                unsafe_allow_html=True)
    st.markdown("### Can we predict wine quality from chemistry alone — without tasting it?")

    st.markdown("""
    ## The Problem

    Wine quality assessment is traditionally subjective — it depends on trained sommeliers
    and sensory panels. This project asks whether **chemical properties alone** can reliably
    predict whether a wine is good or bad.

    **If yes**, wineries could:
    - Predict quality during production before bottling
    - Identify which chemical properties to optimize
    - Support pricing decisions with objective data
    - Reduce reliance on costly sensory testing

    ---

    ## The Dataset
    """)

    col1, col2, col3, col4 = st.columns(4)

    good_count = df['quality_label'].sum()
    bad_count = len(df) - good_count

    with col1:
        st.metric("Total Wines", f"{len(df):,}")
    with col2:
        st.metric("Good Wines (≥6)", f"{good_count:,}")
    with col3:
        st.metric("Bad Wines (<6)", f"{bad_count:,}")
    with col4:
        st.metric("Chemical Features", len(feature_cols))

    col1, col2 = st.columns(2)

    with col1:
        wine_counts = df['wine_type'].value_counts()
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(wine_counts.index, wine_counts.values,
               color=['#8B0000', '#C8A2C8'], alpha=0.85, edgecolor='white', linewidth=2)
        ax.set_title('Wines by Type', fontsize=13, fontweight='bold')
        ax.set_ylabel('Count')
        for i, (label, val) in enumerate(zip(wine_counts.index, wine_counts.values)):
            ax.text(i, val + 30, f'{val:,}', ha='center', fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        st.pyplot(fig)

    with col2:
        quality_counts = df['quality'].value_counts().sort_index()
        colors = ['#C0392B' if q < 6 else '#27AE60' for q in quality_counts.index]
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(quality_counts.index, quality_counts.values,
               color=colors, alpha=0.85, edgecolor='white', linewidth=2)
        ax.set_title('Quality Score Distribution', fontsize=13, fontweight='bold')
        ax.set_xlabel('Quality Score')
        ax.set_ylabel('Count')
        ax.axvline(5.5, color='black', linestyle='--', linewidth=1.5, label='Good/Bad threshold')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        st.pyplot(fig)

    st.markdown("""
    <div class="insight-box">
    <strong>💡 Key Insight:</strong> The dataset skews toward scores 5 and 6 —
    the binary threshold at ≥6 creates a 63% / 37% split (good vs. bad),
    which the model handles well without resampling.
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# PAGE: WINE PREDICTOR
# ============================================================================

elif page == "🔬 Wine Predictor":
    st.markdown('<div class="header-section"><h1>🔬 Wine Quality Predictor</h1></div>',
                unsafe_allow_html=True)
    st.markdown("### Adjust the chemical properties below and get an instant quality prediction.")

    st.info(f"Model: **{model_name}** | Test Accuracy: **83.8%** | ROC-AUC: **0.90**")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Acidity & Sugar")
        fixed_acidity = st.slider("Fixed Acidity", 3.8, 15.9, 7.2, 0.1,
                                   help="Most acids in wine — tartaric, malic, citric")
        volatile_acidity = st.slider("Volatile Acidity", 0.08, 1.58, 0.34, 0.01,
                                      help="Acetic acid — too high leads to vinegar taste")
        citric_acid = st.slider("Citric Acid", 0.0, 1.66, 0.32, 0.01,
                                 help="Adds freshness and flavor")
        residual_sugar = st.slider("Residual Sugar (g/L)", 0.6, 65.8, 5.4, 0.1,
                                    help="Sugar remaining after fermentation")
        ph = st.slider("pH", 2.72, 4.01, 3.22, 0.01,
                       help="Lower = more acidic")

    with col2:
        st.subheader("Sulfur, Salt & Alcohol")
        chlorides = st.slider("Chlorides", 0.009, 0.611, 0.056, 0.001,
                               help="Salt content in wine")
        free_so2 = st.slider("Free Sulfur Dioxide (mg/L)", 1.0, 289.0, 30.0, 1.0,
                              help="Free form of SO2 — prevents microbial growth")
        total_so2 = st.slider("Total Sulfur Dioxide (mg/L)", 6.0, 440.0, 115.0, 1.0,
                               help="Total amount of SO2")
        density = st.slider("Density", 0.987, 1.039, 0.995, 0.001,
                             help="Density of wine relative to water")
        sulphates = st.slider("Sulphates", 0.22, 2.0, 0.53, 0.01,
                               help="Wine additive that contributes to SO2 levels")
        alcohol = st.slider("Alcohol (%)", 8.0, 14.9, 10.5, 0.1,
                             help="Alcohol percentage by volume")

    # Build input
    input_data = pd.DataFrame([[
        fixed_acidity, volatile_acidity, citric_acid, residual_sugar,
        chlorides, free_so2, total_so2, density, ph, sulphates, alcohol
    ]], columns=feature_cols)

    st.markdown("---")

    if st.button("Predict Wine Quality", use_container_width=True, type="primary"):
        X = scaler.transform(input_data) if needs_scaling else input_data
        prediction = model.predict(X)[0]
        probability = model.predict_proba(X)[0]

        good_prob = probability[1]
        bad_prob = probability[0]

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            if prediction == 1:
                st.markdown(f"""
                <div class="good-wine">
                    <strong>Good Wine</strong> — Quality Score ≥ 6<br>
                    Confidence: {good_prob:.1%}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="bad-wine">
                    <strong>Bad Wine</strong> — Quality Score < 6<br>
                    Confidence: {bad_prob:.1%}
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            fig, ax = plt.subplots(figsize=(6, 1.5))
            ax.barh(['Bad', 'Good'], [bad_prob, good_prob],
                    color=['#C0392B', '#27AE60'], alpha=0.85, edgecolor='white')
            ax.set_xlim(0, 1)
            ax.set_xlabel('Probability')
            ax.set_title('Prediction Confidence', fontweight='bold')
            for i, v in enumerate([bad_prob, good_prob]):
                ax.text(v + 0.01, i, f'{v:.1%}', va='center', fontweight='bold')
            ax.grid(axis='x', alpha=0.3)
            st.pyplot(fig)

# ============================================================================
# PAGE: FEATURE IMPORTANCE
# ============================================================================

elif page == "📊 Feature Importance":
    st.markdown('<div class="header-section"><h1>📊 Feature Importance</h1></div>',
                unsafe_allow_html=True)
    st.markdown("### Which chemical properties drive wine quality the most?")

    importances = model.feature_importances_
    fi_df = pd.DataFrame({
        'feature': feature_cols,
        'importance': importances
    }).sort_values('importance', ascending=True)

    fig, ax = plt.subplots(figsize=(10, 7))
    colors = ['#8B0000' if i >= len(fi_df) - 3 else '#C8A2C8' for i in range(len(fi_df))]
    ax.barh(fi_df['feature'], fi_df['importance'],
            color=colors, alpha=0.85, edgecolor='white', linewidth=1.5)
    ax.set_title(f'Feature Importance — {model_name}',
                 fontsize=15, fontweight='bold', pad=15)
    ax.set_xlabel('Importance Score', fontsize=12)
    ax.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)

    top3 = fi_df.nlargest(3, 'importance')

    col1, col2, col3 = st.columns(3)
    for col, (_, row) in zip([col1, col2, col3], top3.iterrows()):
        with col:
            st.metric(row['feature'].title(), f"{row['importance']:.3f}")

    st.markdown("""
    <div class="insight-box">
    <strong>💡 Key Insight:</strong> Alcohol content is consistently the strongest predictor of
    wine quality — higher alcohol wines tend to score better. Volatile acidity is the strongest
    <em>negative</em> driver; high levels produce a vinegar-like taste that lowers scores.
    Sulphates and density round out the top predictors.
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Full Feature Rankings")
    fi_table = fi_df.sort_values('importance', ascending=False).copy()
    fi_table.columns = ['Feature', 'Importance Score']
    fi_table['Importance Score'] = fi_table['Importance Score'].round(4)
    st.dataframe(fi_table, use_container_width=True, hide_index=True)

# ============================================================================
# PAGE: MODEL PERFORMANCE
# ============================================================================

elif page == "📈 Model Performance":
    st.markdown('<div class="header-section"><h1>📈 Model Performance</h1></div>',
                unsafe_allow_html=True)
    st.markdown("### How well does each model predict wine quality?")

    results = {
        'Logistic Regression': {'train_accuracy': 0.7420, 'test_accuracy': 0.7338,
                                 'precision': 0.7624, 'recall': 0.8420, 'f1': 0.8002, 'roc_auc': 0.8045},
        'Random Forest':       {'train_accuracy': 1.0000, 'test_accuracy': 0.8377,
                                 'precision': 0.8525, 'recall': 0.8991, 'f1': 0.8752, 'roc_auc': 0.9044},
        'SVM':                 {'train_accuracy': 0.7931, 'test_accuracy': 0.7785,
                                 'precision': 0.7930, 'recall': 0.8797, 'f1': 0.8341, 'roc_auc': 0.8394},
        'XGBoost':             {'train_accuracy': 0.9865, 'test_accuracy': 0.8162,
                                 'precision': 0.8380, 'recall': 0.8797, 'f1': 0.8583, 'roc_auc': 0.8843},
    }

    results_df = pd.DataFrame(results).round(4)

    col1, col2, col3, col4 = st.columns(4)
    for col, (mname, mresults) in zip([col1, col2, col3, col4], results.items()):
        with col:
            is_best = mname == 'Random Forest'
            st.metric(
                label=f"{'★ ' if is_best else ''}{mname}",
                value=f"{mresults['test_accuracy']:.1%}",
                delta=f"F1: {mresults['f1']:.3f}"
            )

    st.subheader("Full Comparison")
    st.dataframe(results_df.style.highlight_max(axis=1, color='#eafaf1'), use_container_width=True)

    st.markdown("---")
    st.subheader("ROC-AUC Comparison")

    fig, ax = plt.subplots(figsize=(10, 5))
    model_names = list(results.keys())
    roc_scores = [results[m]['roc_auc'] for m in model_names]
    colors = ['#8B0000' if m == 'Random Forest' else '#C8A2C8' for m in model_names]
    bars = ax.bar(model_names, roc_scores, color=colors, alpha=0.85, edgecolor='white', linewidth=2)
    ax.set_ylim(0.75, 0.95)
    ax.set_title('ROC-AUC by Model', fontsize=14, fontweight='bold')
    ax.set_ylabel('ROC-AUC Score')
    for bar, score in zip(bars, roc_scores):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.003,
                f'{score:.4f}', ha='center', fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)

    st.markdown("""
    <div class="insight-box">
    <strong>⚠️ Overfitting Note:</strong> Random Forest achieves 100% training accuracy —
    it memorized the training data. Despite this, it still generalizes well (83.8% test accuracy,
    ROC-AUC 0.90). XGBoost shows similar overfitting (98.6% train).
    Logistic Regression and SVM are the most stable models with minimal train/test gap.
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# PAGE: ABOUT
# ============================================================================

elif page == "💡 About":
    st.markdown('<div class="header-section"><h1>💡 About This Project</h1></div>',
                unsafe_allow_html=True)

    st.markdown("""
    ## Methodology

    ### Data
    - **Source:** UCI Wine Quality Dataset
    - **Size:** 6,497 wines (1,599 red + 4,898 white)
    - **Features:** 11 physicochemical properties
    - **Target:** Quality score (3–9) → binarized as Good (≥6) vs Bad (<6)

    ### Models Trained
    | Model | Test Accuracy | ROC-AUC |
    |---|---|---|
    | Logistic Regression | 73.4% | 0.80 |
    | SVM | 77.9% | 0.84 |
    | XGBoost | 81.6% | 0.88 |
    | **Random Forest** | **83.8%** | **0.90** |

    ### Why Random Forest?
    Random Forest won on both test accuracy and ROC-AUC. Tree-based models handle
    non-linear relationships between chemical properties naturally without requiring
    feature scaling.

    ### Limitations
    - Binary classification loses nuance between scores 6–9
    - Random Forest is overfit (1.0 training accuracy) — tuning with GridSearchCV would improve reliability
    - No grape variety, region, or vintage data — chemistry alone has limits

    ---

    ## Feature Glossary

    | Feature | Description |
    |---|---|
    | Fixed Acidity | Tartaric, malic, citric acids |
    | Volatile Acidity | Acetic acid — high levels = vinegar taste |
    | Citric Acid | Adds freshness, found in small quantities |
    | Residual Sugar | Sugar after fermentation stops |
    | Chlorides | Salt content |
    | Free SO₂ | Prevents microbial growth and oxidation |
    | Total SO₂ | Free + bound SO₂ |
    | Density | Relative to water — correlates with alcohol/sugar |
    | pH | Acidity scale — most wines between 3.0–3.5 |
    | Sulphates | Additive contributing to SO₂ |
    | Alcohol | % by volume |

    ---

    **Author:** Jorge Reyes-Ornelas
    **Data Source:** UCI Machine Learning Repository — Wine Quality Dataset
    **Tools:** Python, scikit-learn, XGBoost, Streamlit, pandas, matplotlib

    *Bridging data science, wine operations, and predictive modeling.*
    """)

# FOOTER
st.markdown("""
---
*Wine Quality Predictor • Random Forest Classifier • ROC-AUC: 0.90*
""")
