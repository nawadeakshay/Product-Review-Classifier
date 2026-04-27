# ============================================================
# preprocessing.py
# PURPOSE: Text cleaning + RoBERTa tokenization + Dataset class
# ============================================================

import re
import pandas as pd
import torch
from torch.utils.data import Dataset
from transformers import RobertaTokenizer
from sklearn.model_selection import train_test_split

# Maximum number of tokens per review (most reviews are shorter)
MAX_LEN = 128

# Load the pre-trained RoBERTa tokenizer from HuggingFace
TOKENIZER = RobertaTokenizer.from_pretrained("roberta-base")


def clean_text(text: str) -> str:
    """
    Clean raw review text by removing noise.
    Input:  "Great app!!! 😊 Visit http://spam.com"
    Output: "great app"
    """
    text = str(text)                            # Ensure input is a string
    text = text.lower()                         # Convert to lowercase
    text = re.sub(r"http\S+", "", text)         # Remove URLs
    text = re.sub(r"<.*?>", "", text)           # Remove HTML tags like <br>
    text = re.sub(r"[^\x00-\x7F]+", "", text)  # Remove emojis and non-ASCII
    text = re.sub(r"[^a-zA-Z0-9\s.,!?']", "", text)  # Keep only useful chars
    text = re.sub(r"\s+", " ", text).strip()   # Collapse multiple spaces
    return text


def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Apply cleaning to every review in the dataset."""
    df = df.copy()                                  # Don't modify original
    df["clean_text"] = df["review_text"].apply(clean_text)
    df = df.drop_duplicates(subset=["clean_text"]) # Remove exact duplicates
    df = df[df["clean_text"].str.len() > 5]       # Remove very short reviews
    df = df.reset_index(drop=True)
    print(f"[INFO] After cleaning: {len(df)} reviews")
    return df


def split_data(df: pd.DataFrame, label_col: str):
    """
    Split data into train (70%), validation (15%), test (15%).
    Uses stratified split to preserve class ratios.
    """
    X = df["clean_text"].values     # Input texts
    y = df[label_col].values           # Labels (integers)
    
    # First split: train vs. temp (val+test)
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, stratify=y, random_state=42
    )
    # Second split: val vs. test (50/50 of the 30% temp)
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=42
    )
    
    print(f"Train: {len(X_train)} | Val: {len(X_val)} | Test: {len(X_test)}")
    return (X_train, y_train), (X_val, y_val), (X_test, y_test)


class ReviewDataset(Dataset):
    """
    PyTorch Dataset class for review data.
    Converts text + label into tokenized tensors.
    This is required by PyTorch DataLoader for batching.
    """
    def __init__(self, texts, labels):
        self.texts = texts    # List of clean text strings
        self.labels = labels  # List of integer labels
    
    def __len__(self):
        return len(self.texts)  # Total number of samples
    
    def __getitem__(self, idx):
        """
        For each sample, tokenize the text and return tensors.
        Called automatically by DataLoader for each batch.
        """
        text = self.texts[idx]   # Get text at position idx
        label = self.labels[idx] # Get corresponding label
        
        # Tokenize: convert text to input_ids, attention_mask
        encoding = TOKENIZER(
            text,
            max_length=MAX_LEN,         # Truncate/pad to 128 tokens
            padding="max_length",       # Pad shorter texts with zeros
            truncation=True,            # Cut longer texts at 128 tokens
            return_tensors="pt"         # Return PyTorch tensors
        )
        
        return {
            "input_ids": encoding["input_ids"].squeeze(),     # Token IDs
            "attention_mask": encoding["attention_mask"].squeeze(),  # 1 for real tokens, 0 for padding
            "labels": torch.tensor(label, dtype=torch.long)  # Ground truth label
        }


# --- Test this file directly ---
if __name__ == "__main__":
    sample = "App crashes on login every single time!!! 😡 "
    print(clean_text(sample))  # Expected: "app crashes on login every single time"