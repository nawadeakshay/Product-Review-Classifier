# ============================================================
# train.py
# PURPOSE: Train sentiment + bug classification models
# ============================================================

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm import tqdm

from data_loader import load_data, validate_columns
from preprocessing import preprocess_dataframe, split_data, ReviewDataset
from model import get_sentiment_model, get_bug_model

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

BATCH_SIZE = 16
EPOCHS = 3
LEARNING_RATE = 2e-5


# ================================
# TRAIN ONE EPOCH
# ================================
def train_epoch(model, data_loader, optimizer, loss_fn):
    model.train()
    total_loss = 0

    for batch in tqdm(data_loader, desc="Training"):
        input_ids = batch["input_ids"].to(DEVICE)
        attention_mask = batch["attention_mask"].to(DEVICE)
        labels = batch["labels"].to(DEVICE)

        optimizer.zero_grad()

        logits = model(input_ids, attention_mask)

        loss = loss_fn(logits, labels)
        loss.backward()

        optimizer.step()

        total_loss += loss.item()

    return total_loss / len(data_loader)


# ================================
# VALIDATION
# ================================
def eval_model(model, data_loader, loss_fn):
    model.eval()
    total_loss = 0

    with torch.no_grad():
        for batch in tqdm(data_loader, desc="Validation"):
            input_ids = batch["input_ids"].to(DEVICE)
            attention_mask = batch["attention_mask"].to(DEVICE)
            labels = batch["labels"].to(DEVICE)

            logits = model(input_ids, attention_mask)

            loss = loss_fn(logits, labels)
            total_loss += loss.item()

    return total_loss / len(data_loader)


# ================================
# TRAIN FUNCTION
# ================================
def train_model(model, train_ds, val_ds, save_path, class_weights=None):
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE)

    model = model.to(DEVICE)

    optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE)

    # FIXED: Handle class weights safely
    if class_weights is not None:
        loss_fn = nn.CrossEntropyLoss(weight=class_weights.to(DEVICE))
    else:
        loss_fn = nn.CrossEntropyLoss()

    for epoch in range(EPOCHS):
        print(f"\n=== Epoch {epoch+1}/{EPOCHS} ===")

        train_loss = train_epoch(model, train_loader, optimizer, loss_fn)
        val_loss = eval_model(model, val_loader, loss_fn)

        print(f"Train Loss: {train_loss:.4f}")
        print(f"Val Loss: {val_loss:.4f}")

    torch.save(model.state_dict(), save_path)
    print(f"[INFO] Model saved to {save_path}")


# ================================
# MAIN PIPELINE
# ================================
if __name__ == "__main__":

    # Load data
    df = load_data("data/reviews.csv")
    df = validate_columns(df)

    df = preprocess_dataframe(df)

    # ================================
    # SENTIMENT MODEL
    # ================================
    print("\n[TRAINING] Sentiment Classifier")

    (X_train, y_train), (X_val, y_val), _ = split_data(df, "sentiment_label")

    train_ds = ReviewDataset(X_train, y_train)
    val_ds = ReviewDataset(X_val, y_val)

    sentiment_model = get_sentiment_model()

    # Use class weights ONLY for sentiment
    class_counts = torch.bincount(torch.tensor(y_train))
    weights = 1.0 / class_counts.float()

    train_model(
        sentiment_model,
        train_ds,
        val_ds,
        "models/sentiment_model.pt",
        weights
    )

    # ================================
    # BUG MODEL
    # ================================
    print("\n[TRAINING] Bug Classifier")

    # Filter only negative reviews
    bug_df = df[df["sentiment_label"] == 0]

    # If not enough data → skip safely
    if len(bug_df) < 10:
        print("[WARNING] Not enough data for bug classification. Skipping...")
    else:
        bug_df["bug_category"] = bug_df["bug_category"].fillna("Other")

        # Encode labels
        label_map = {"Audio": 0, "Login": 1, "UI": 2, "Other": 3}
        bug_df["bug_label"] = bug_df["bug_category"].map(label_map)

        (X_train2, y_train2), (X_val2, y_val2), _ = split_data(bug_df, "bug_label")

        train_ds2 = ReviewDataset(X_train2, y_train2)
        val_ds2 = ReviewDataset(X_val2, y_val2)

        bug_model = get_bug_model()

        # IMPORTANT FIX: No class weights here
        train_model(
            bug_model,
            train_ds2,
            val_ds2,
            "models/bugtype_model.pt",
            class_weights=None
        )