# =============================================================================
# The Solar Paradox: Why the World's Sunniest Countries Have the Least Solar Power
# A Sociological Analysis of Global Solar Inequality
# Author: Jorge Reyes-Ornelas
# Version 2.0 — Sharper Questions, Regional Analysis, Structural Framing
# =============================================================================

# =============================================================================
# SECTION 0: LIBRARIES AND CONFIGURATION
# =============================================================================

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import numpy as np
import os

# Plot styling
sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (12, 6)
plt.rcParams["font.size"] = 12

# Region color palette for consistent use across all plots
REGION_PALETTE = {
    "North America": "#2980B9",
    "Europe":        "#16A085",
    "Oceania":       "#8E44AD",
    "Asia":          "#E67E22",
    "South America": "#27AE60",
    "Africa":        "#C0392B",
    "Middle East":   "#F39C12"
}

# Output folder for saving plots
OUTPUT_DIR = "output_plots"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# =============================================================================
# SECTION 1: LOAD AND INSPECT DATA
# =============================================================================

def load_data(filepath):
    """
    Load the solar dataset and print a structural summary.
    Returns the raw DataFrame.
    """
    df = pd.read_csv(filepath)

    print("=" * 60)
    print("DATASET OVERVIEW")
    print("=" * 60)
    print(f"Shape:            {df.shape}")
    print(f"Countries:        {df['Country'].nunique()}")
    print(f"Regions:          {df['Region'].unique().tolist()}")
    print(f"\nMissing Values:\n{df.isnull().sum()}")
    print("=" * 60)

    return df


# =============================================================================
# SECTION 2: COUNTRY-LEVEL AGGREGATION
# =============================================================================

def aggregate_by_country(df):
    """
    Collapse dataset to one row per country.
    Calculates mean values for all key metrics.
    Engineers an Efficiency Score and Adoption Gap.
    Returns a country-level DataFrame.
    """
    country_df = (
        df.groupby(["Country", "Region"])[[
            "Solar_Installations_Count",
            "Annual_Sunlight_Hours",
            "GHI_kWh_per_m2",
            "Avg_Annual_Production_kWh",
            "Electricity_Price_USD_per_kWh",
            "Avg_System_Cost_USD",
            "Payback_Period_Years",
            "ROI_Percentage",
            "Estimated_Annual_Savings_USD",
            "CO2_Reduction_Tons_per_Year",
            "Solar_Viability_Score"
        ]]
        .mean()
        .reset_index()
    )

    # Efficiency Score: kWh produced per installation
    country_df["Efficiency_Score"] = (
        country_df["Avg_Annual_Production_kWh"] /
        country_df["Solar_Installations_Count"]
    )

    # Adoption Gap: solar potential relative to installations
    # Higher score = more potential being wasted
    country_df["Adoption_Gap"] = (
        country_df["GHI_kWh_per_m2"] /
        (country_df["Solar_Installations_Count"] + 1)
    ) * 1000

    print(f"\nCountries in dataset: {len(country_df)}")
    return country_df


# =============================================================================
# SECTION 3: ESTABLISHING THE PARADOX
# =============================================================================

def plot_paradox(country_df):
    """
    Scatter plot of solar potential (GHI) vs. solar adoption (installations).
    Color coded by region to reveal the structural inequality pattern.
    """
    fig, ax = plt.subplots(figsize=(13, 8))

    for region, group in country_df.groupby("Region"):
        ax.scatter(
            group["GHI_kWh_per_m2"],
            group["Solar_Installations_Count"],
            label=region,
            color=REGION_PALETTE.get(region, "#7F8C8D"),
            alpha=0.85,
            s=100,
            zorder=3
        )
        for _, row in group.iterrows():
            ax.annotate(
                row["Country"],
                (row["GHI_kWh_per_m2"], row["Solar_Installations_Count"]),
                fontsize=7.5,
                alpha=0.8,
                xytext=(5, 5),
                textcoords="offset points"
            )

    ax.set_title(
        "The Solar Paradox: Potential vs. Adoption by Country",
        fontsize=16, fontweight="bold"
    )
    ax.set_xlabel("Solar Potential — GHI (kWh per m²)", fontsize=13)
    ax.set_ylabel("Solar Installations Count", fontsize=13)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.legend(title="Region", bbox_to_anchor=(1.01, 1), loc="upper left")

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/01_solar_paradox.png", dpi=150, bbox_inches="tight")
    plt.show()
    print(f"Plot saved → {OUTPUT_DIR}/01_solar_paradox.png")


# =============================================================================
# SECTION 4: THE ROI PARADOX
# Are high-potential countries being held back by system costs?
# =============================================================================

def plot_roi_paradox(country_df):
    """
    Horizontal bar chart of average ROI percentage by region.
    The question: which regions get the BEST return on solar investment
    yet still have the lowest adoption?
    Africa and Middle East leading in ROI but lagging in installations
    is the structural inequality argument in numbers.
    """
    region_roi = (
        country_df.groupby("Region")[["ROI_Percentage", "Solar_Installations_Count"]]
        .mean()
        .reset_index()
        .sort_values("ROI_Percentage", ascending=True)
    )

    fig, ax = plt.subplots(figsize=(12, 6))

    bars = ax.barh(
        region_roi["Region"],
        region_roi["ROI_Percentage"],
        color=[REGION_PALETTE.get(r, "#7F8C8D") for r in region_roi["Region"]],
        alpha=0.85,
        edgecolor="white"
    )

    # Annotate bars with average installations count
    for bar, (_, row) in zip(bars, region_roi.iterrows()):
        ax.text(
            bar.get_width() + 0.1,
            bar.get_y() + bar.get_height() / 2,
            f"{int(row['Solar_Installations_Count']):,} installs",
            va="center", fontsize=9, color="#2C3E50"
        )

    ax.set_title(
        "The ROI Paradox: Best Returns, Lowest Adoption\n"
        "Africa and Middle East lead in solar ROI — yet installation counts tell a different story",
        fontsize=14, fontweight="bold"
    )
    ax.set_xlabel("Average ROI (%)", fontsize=12)
    ax.set_ylabel("Region", fontsize=12)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/02_roi_paradox.png", dpi=150, bbox_inches="tight")
    plt.show()
    print(f"Plot saved → {OUTPUT_DIR}/02_roi_paradox.png")


# =============================================================================
# SECTION 5: THE PAYBACK INEQUALITY
# Where does solar take the longest to pay off?
# =============================================================================

def plot_payback_inequality(country_df):
    """
    Scatter plot of GHI vs. Payback Period by region.
    High GHI + long payback = structural inequality.
    Countries in the top-right quadrant are the most disadvantaged.
    """
    fig, ax = plt.subplots(figsize=(12, 7))

    for region, group in country_df.groupby("Region"):
        ax.scatter(
            group["GHI_kWh_per_m2"],
            group["Payback_Period_Years"],
            label=region,
            color=REGION_PALETTE.get(region, "#7F8C8D"),
            alpha=0.85,
            s=100,
            zorder=3
        )
        for _, row in group.iterrows():
            ax.annotate(
                row["Country"],
                (row["GHI_kWh_per_m2"], row["Payback_Period_Years"]),
                fontsize=7.5,
                alpha=0.8,
                xytext=(5, 5),
                textcoords="offset points"
            )

    ax.axvline(country_df["GHI_kWh_per_m2"].median(), color="gray",
               linestyle="--", alpha=0.5, label="Median GHI")
    ax.axhline(country_df["Payback_Period_Years"].median(), color="gray",
               linestyle=":", alpha=0.5, label="Median Payback")

    ax.set_title(
        "The Payback Inequality: Solar Potential vs. Years to Break Even\n"
        "Top-right quadrant = high sun, long wait — the most structurally disadvantaged",
        fontsize=14, fontweight="bold"
    )
    ax.set_xlabel("Solar Potential — GHI (kWh per m²)", fontsize=13)
    ax.set_ylabel("Payback Period (Years)", fontsize=13)
    ax.legend(title="Region", bbox_to_anchor=(1.01, 1), loc="upper left")

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/03_payback_inequality.png", dpi=150, bbox_inches="tight")
    plt.show()
    print(f"Plot saved → {OUTPUT_DIR}/03_payback_inequality.png")


# =============================================================================
# SECTION 6: THE REGIONAL ADOPTION GAP
# Which regions are most underperforming relative to their potential?
# =============================================================================

def plot_adoption_gap(country_df):
    """
    Horizontal bar chart of average Adoption Gap score by region.
    Higher score = more solar potential being wasted.
    """
    region_gap = (
        country_df.groupby("Region")["Adoption_Gap"]
        .mean()
        .reset_index()
        .sort_values("Adoption_Gap", ascending=True)
    )

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.barh(
        region_gap["Region"],
        region_gap["Adoption_Gap"],
        color=[REGION_PALETTE.get(r, "#7F8C8D") for r in region_gap["Region"]],
        alpha=0.85,
        edgecolor="white"
    )

    ax.set_title(
        "The Adoption Gap: Wasted Solar Potential by Region\n"
        "(Higher score = more potential going unused)",
        fontsize=15, fontweight="bold"
    )
    ax.set_xlabel("Adoption Gap Score", fontsize=12)
    ax.set_ylabel("Region", fontsize=12)

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/04_adoption_gap.png", dpi=150)
    plt.show()
    print(f"Plot saved → {OUTPUT_DIR}/04_adoption_gap.png")


# =============================================================================
# SECTION 7: THE OUTLIERS — WHO IS PUNCHING ABOVE THEIR WEIGHT?
# =============================================================================

def plot_outliers(country_df):
    """
    Identifies countries with high GHI but above-average installations.
    These are the overperformers — countries beating structural odds.
    India is the key case study here.
    """
    median_ghi = country_df["GHI_kWh_per_m2"].median()
    median_installs = country_df["Solar_Installations_Count"].median()

    overperformers = country_df[
        (country_df["GHI_kWh_per_m2"] >= median_ghi) &
        (country_df["Solar_Installations_Count"] >= median_installs)
    ].copy()

    underperformers = country_df[
        (country_df["GHI_kWh_per_m2"] >= median_ghi) &
        (country_df["Solar_Installations_Count"] < median_installs)
    ].copy()

    fig, ax = plt.subplots(figsize=(13, 8))

    ax.scatter(
        underperformers["GHI_kWh_per_m2"],
        underperformers["Solar_Installations_Count"],
        color="#C0392B", alpha=0.8, s=100,
        label="Underperforming (high sun, low adoption)", zorder=3
    )
    ax.scatter(
        overperformers["GHI_kWh_per_m2"],
        overperformers["Solar_Installations_Count"],
        color="#27AE60", alpha=0.8, s=120,
        label="Overperforming (high sun, high adoption)", zorder=3
    )

    for _, row in pd.concat([overperformers, underperformers]).iterrows():
        ax.annotate(
            row["Country"],
            (row["GHI_kWh_per_m2"], row["Solar_Installations_Count"]),
            fontsize=8, alpha=0.85,
            xytext=(5, 5), textcoords="offset points"
        )

    ax.axvline(median_ghi, color="gray", linestyle="--", alpha=0.5, label="Median GHI")
    ax.axhline(median_installs, color="gray", linestyle=":", alpha=0.5, label="Median Installations")

    ax.set_title(
        "Beating the Odds: Overperformers vs. Underperformers\nAmong High Solar Potential Countries",
        fontsize=15, fontweight="bold"
    )
    ax.set_xlabel("Solar Potential — GHI (kWh per m²)", fontsize=13)
    ax.set_ylabel("Solar Installations Count", fontsize=13)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.legend(bbox_to_anchor=(1.01, 1), loc="upper left")

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/05_outliers.png", dpi=150, bbox_inches="tight")
    plt.show()
    print(f"Plot saved → {OUTPUT_DIR}/05_outliers.png")

    print("\nOverperformers (beating structural odds):")
    print(overperformers[["Country", "Region", "GHI_kWh_per_m2",
                           "Solar_Installations_Count",
                           "Payback_Period_Years"]].to_string(index=False))


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":

    # --- Load ---
    df = load_data("solar_energy_worldwide.csv")

    # --- Aggregate to country level ---
    country_df = aggregate_by_country(df)

    # --- Section 3: The Paradox ---
    print("\n" + "=" * 60)
    print("SECTION 3: ESTABLISHING THE PARADOX")
    print("Question: Does solar potential predict solar adoption?")
    print("=" * 60)
    plot_paradox(country_df)

    # --- Section 4: The Cost Barrier ---
    print("\n" + "=" * 60)
    print("SECTION 4: THE ROI PARADOX")
    print("Question: Which regions get the best ROI on solar yet still have the lowest adoption?")
    print("=" * 60)
    plot_roi_paradox(country_df)

    # --- Section 5: Payback Inequality ---
    print("\n" + "=" * 60)
    print("SECTION 5: THE PAYBACK INEQUALITY")
    print("Question: Where does solar take the longest to pay off?")
    print("=" * 60)
    plot_payback_inequality(country_df)

    # --- Section 6: Adoption Gap ---
    print("\n" + "=" * 60)
    print("SECTION 6: THE REGIONAL ADOPTION GAP")
    print("Question: Which regions are wasting the most solar potential?")
    print("=" * 60)
    plot_adoption_gap(country_df)

    # --- Section 7: Outliers ---
    print("\n" + "=" * 60)
    print("SECTION 7: THE OUTLIERS")
    print("Question: Which high-potential countries are beating structural odds?")
    print("=" * 60)
    plot_outliers(country_df)

    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print(f"All plots saved to: {OUTPUT_DIR}/")
    print("=" * 60)
