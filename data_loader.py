# ============================================================
# data_loader.py
# PURPOSE: Load, inspect, and adapt dataset for model training
# ============================================================

import pandas as pd
import os


def load_data(file_path: str) -> pd.DataFrame:
    """
    Load dataset from CSV or Excel.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset not found: {file_path}")

    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".csv":
        df = pd.read_csv(file_path)
    elif extension in [".xlsx", ".xls"]:
        df = pd.read_excel(file_path)
    else:
        raise ValueError("Unsupported file format. Use CSV or Excel.")

    print(f"[INFO] Loaded {len(df)} rows from {file_path}")
    inspect_data(df)

    return df


def inspect_data(df: pd.DataFrame) -> None:
    """
    Print dataset summary.
    """
    print("\n--- Dataset Summary ---")
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")

    print("\nMissing Values:")
    print(df.isnull().sum())
    print("----------------------\n")


def adapt_amazon_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert Amazon dataset format to project-required format.
    """
    df = df.copy()

    # Rename reviewText → review_text
    if "reviewText" in df.columns:
        df = df.rename(columns={"reviewText": "review_text"})

    # Create sentiment_label from rating (overall)
    if "overall" in df.columns:
        df["sentiment_label"] = df["overall"].apply(
            lambda x: 1 if x >= 3 else 0
        )

    # Create bug_category (only for negative reviews)
    if "sentiment_label" in df.columns:
        df["bug_category"] = df["sentiment_label"].apply(
            lambda x: "Other" if x == 0 else None
        )

    return df


def validate_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate required columns and clean dataset.
    """
    # First adapt dataset if needed
    df = adapt_amazon_dataset(df)

    required_cols = ["review_text", "sentiment_label"]

    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Remove empty reviews
    original_len = len(df)

    df = df.dropna(subset=["review_text"])
    df = df[df["review_text"].astype(str).str.strip() != ""]

    removed = original_len - len(df)
    if removed > 0:
        print(f"[WARN] Removed {removed} empty reviews")

    df = df.reset_index(drop=True)

    print(f"[INFO] Final dataset size: {len(df)}")

    return df


# ============================================================
# TEST RUN
# ============================================================
if __name__ == "__main__":
    df = load_data("data/reviews.csv")
    df = validate_columns(df)
    print(df.head())