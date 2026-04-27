# ============================================================
# model.py
# PURPOSE: Define the RoBERTa classification model architecture
# ============================================================

import torch
import torch.nn as nn
from transformers import RobertaModel

class RobertaClassifier(nn.Module):
    """
    Custom RoBERTa classifier.
    Inherits from nn.Module (required for all PyTorch models).
    
    Architecture:
      RoBERTa base → [CLS] token → Dropout → Linear → num_labels classes
    """
    def __init__(self, num_labels: int, dropout_rate: float = 0.3):
        super(RobertaClassifier, self).__init__()  # Initialize parent class
        
        # Load pre-trained RoBERTa-base from HuggingFace
        # This has 12 transformer layers, 768 hidden dims, 125M params
        self.roberta = RobertaModel.from_pretrained("roberta-base")
        
        # Dropout layer to prevent overfitting
        # Randomly sets 30% of neurons to zero during training
        self.dropout = nn.Dropout(p=dropout_rate)
        
        # Linear classification head
        # Takes the 768-dim [CLS] representation → outputs num_labels scores
        self.classifier = nn.Linear(768, num_labels)
    
    def forward(self, input_ids, attention_mask):
        """
        Forward pass: takes tokenized inputs → returns class scores (logits).
        Called automatically by PyTorch during training.
        """
        # Pass tokens through RoBERTa encoder
        # outputs.last_hidden_state shape: (batch_size, seq_len, 768)
        outputs = self.roberta(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        
        # Extract [CLS] token representation (index 0 = first token = [CLS])
        # CLS token summarizes the meaning of the whole sentence
        cls_output = outputs.last_hidden_state[:, 0, :]  # shape: (batch, 768)
        
        # Apply dropout to prevent overfitting
        dropped = self.dropout(cls_output)
        
        # Pass through linear layer to get class scores (logits)
        logits = self.classifier(dropped)  # shape: (batch, num_labels)
        
        return logits  # Raw scores (not probabilities yet)


def get_sentiment_model():
    """Returns a RoBERTa model for binary sentiment classification."""
    return RobertaClassifier(num_labels=2)  # 0=Negative, 1=Positive


def get_bug_model():
    """Returns a RoBERTa model for 4-class bug category classification."""
    return RobertaClassifier(num_labels=4)  # 0=Audio, 1=Login, 2=UI, 3=Other


def save_model(model, path: str):
    """Save model weights to disk."""
    torch.save(model.state_dict(), path)
    print(f"[INFO] Model saved to {path}")


def load_model(model, path: str, device):
    """Load saved model weights from disk."""
    model.load_state_dict(torch.load(path, map_location=device))
    model.to(device)
    print(f"[INFO] Model loaded from {path}")
    return model


# --- Quick test ---
if __name__ == "__main__":
    model = get_sentiment_model()
    total_params = sum(p.numel() for p in model.parameters())
    print(f"Total parameters: {total_params:,}")
    # Expected: ~125,000,000 (125 million)