"""
pytest unit tests for nlu.parse_message
"""

from nlu import parse_message

def test_greeting_intent():
    r = parse_message("Hey there!")
    assert r["intent"] == "greeting"
    assert r["confidence"] >= 0.8

def test_hours_intent():
    r = parse_message("What are your hours?")
    assert r["intent"] == "hours"

def test_entity_date():
    r = parse_message("I need support on 12/10/2025")
    assert "date" in r["entities"]
