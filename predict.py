# ============================================================
# predict.py
# PURPOSE: Run inference + generate Excel + auto-open file
# ============================================================

import torch
import pandas as pd
import os
import subprocess
import sys

from data_loader import load_data, validate_columns
from preprocessing import preprocess_dataframe, ReviewDataset
from model import get_sentiment_model

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# ================================
# GET NEXT FILE NAME (prediction_1,2,3...)
# ================================
def get_next_filename(folder="outputs"):
    existing_files = os.listdir(folder)

    numbers = []

    for file in existing_files:
        if file.startswith("prediction_") and file.endswith(".xlsx"):
            try:
                num = int(file.split("_")[1].split(".")[0])
                numbers.append(num)
            except:
                pass

    next_num = max(numbers) + 1 if numbers else 1

    return os.path.join(folder, f"prediction_{next_num}.xlsx")


# ================================
# LOAD MODEL
# ================================
def load_model(model, path):
    model.load_state_dict(torch.load(path, map_location=DEVICE))
    model.to(DEVICE)
    model.eval()
    print(f"[INFO] Model loaded from {path}")
    return model


# ================================
# PREDICT FUNCTION
# ================================
def predict(model, dataset):
    predictions = []

    loader = torch.utils.data.DataLoader(dataset, batch_size=16)

    with torch.no_grad():
        for batch in loader:
            input_ids = batch["input_ids"].to(DEVICE)
            attention_mask = batch["attention_mask"].to(DEVICE)

            logits = model(input_ids, attention_mask)
            preds = torch.argmax(logits, dim=1)

            predictions.extend(preds.cpu().numpy())

    return predictions


# ================================
# RULE-BASED BUG CLASSIFIER
# ================================
def rule_based_bug(text):
    text = text.lower()

    if "login" in text or "sign in" in text:
        return "Login"
    elif "audio" in text or "sound" in text:
        return "Audio"
    elif "button" in text or "screen" in text or "ui" in text:
        return "UI"
    else:
        return "Other"


# ================================
# MAIN PIPELINE
# ================================
if __name__ == "__main__":

    print("[INFO] Starting prediction pipeline...")

    # Load and preprocess data
    df = load_data("data/reviews.csv")
    df = validate_columns(df)
    df = preprocess_dataframe(df)

    texts = df["clean_text"].values

    # ================================
    # SENTIMENT PREDICTION
    # ================================
    sentiment_model = load_model(get_sentiment_model(), "models/sentiment_model.pt")

    dummy_labels = [0] * len(texts)
    dataset = ReviewDataset(texts, dummy_labels)

    sentiment_preds = predict(sentiment_model, dataset)

    df["predicted_sentiment"] = [
        "Positive" if p == 1 else "Negative" for p in sentiment_preds
    ]

    # ================================
    # BUG PREDICTION
    # ================================
    bug_predictions = []

    for text, sentiment in zip(df["review_text"], df["predicted_sentiment"]):
        if sentiment == "Negative":
            bug_predictions.append(rule_based_bug(text))
        else:
            bug_predictions.append("N/A")

    df["predicted_bug_category"] = bug_predictions

    # ================================
    # SAVE OUTPUT
    # ================================
    os.makedirs("outputs", exist_ok=True)

    output_path = get_next_filename("outputs")

    df[["review_text", "predicted_sentiment", "predicted_bug_category"]].to_excel(
        output_path, index=False
    )

    print(f"[INFO] Excel report saved to {output_path}")

    # ================================
    # AUTO OPEN EXCEL
    # ================================
    try:
        if sys.platform == "win32":
            subprocess.Popen(["start", output_path], shell=True)
        else:
            subprocess.Popen(["open", output_path])
    except Exception:
        print("[WARNING] Could not open Excel automatically")

    print("\n[DONE] Classification complete!")