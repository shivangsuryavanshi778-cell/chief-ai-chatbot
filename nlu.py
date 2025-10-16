"""
nlu.py
- Lightweight rule-based NLU with confidence scoring and small ML stub fallback.
- Exposes parse_message(text) -> dict(intent, entities, confidence, normalized_text)
"""

import re
from datetime import datetime

# Simple rule-based intents and patterns
INTENT_PATTERNS = {
    "greeting": [r"\bhi\b", r"\bhello\b", r"\bhey\b", r"\bgreetings\b"],
    "help": [r"\bhelp\b", r"\bsupport\b", r"\bassist\b"],
    "hours": [r"\b(open|close|hours|timings)\b"],
    "pricing": [r"\b(price|cost|fee|pricing)\b"],
    "faq_order_status": [r"\b(order status|where is my order|track order)\b"],
}

ENTITY_PATTERNS = {
    "date": r"(\b\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?\b|\btomorrow\b|\btoday\b|\bnext week\b)",
    "email": r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)",
    "phone": r"(\+?\d{7,15})"
}

CONFIDENCE_HIGH = 0.9
CONFIDENCE_MED = 0.6
CONFIDENCE_LOW = 0.35

def normalize_text(text: str) -> str:
    text = text.strip()
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s/@\+\-\.]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text

def rule_based_intent(text: str):
    for intent, patterns in INTENT_PATTERNS.items():
        for p in patterns:
            if re.search(p, text):
                return intent, CONFIDENCE_HIGH
    return None, 0.0

def extract_entities(text: str):
    entities = {}
    for name, pattern in ENTITY_PATTERNS.items():
        m = re.search(pattern, text)
        if m:
            entities[name] = m.group(0)
    return entities

def simple_ml_fallback(text: str):
    # Stubbed classifier: returns generic 'unknown' low confidence
    # Replace with real model if user configures one
    return "unknown", CONFIDENCE_LOW

def parse_message(raw_text: str):
    norm = normalize_text(raw_text)
    intent, conf = rule_based_intent(norm)
    if not intent:
        intent, conf = simple_ml_fallback(norm)

    entities = extract_entities(norm)
    # If entities found, slightly bump confidence
    if entities and conf < CONFIDENCE_MED:
        conf = min(0.75, conf + 0.15)

    return {
        "intent": intent,
        "entities": entities,
        "confidence": conf,
        "normalized_text": norm
    }
