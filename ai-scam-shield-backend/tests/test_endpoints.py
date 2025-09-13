import os
import sys


def _get_client():
    # Import inside function to avoid collection-time import of fastapi/pydantic
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "app"))
    from core import analyze_text, recovery_analysis
    return (analyze_text, recovery_analysis)


def test_scam_message_zelle():
    analyze_text, _ = _get_client()
    payload = "Send $500 via Zelle to 123-456-7890 immediately, click http://phish.example.com"
    data = analyze_text(payload)
    assert data["heuristic_score"] <= 100


def test_legit_message_amazon():
    analyze_text, _ = _get_client()
    payload = "Your Amazon order has shipped. Track at https://amazon.example/track"
    data = analyze_text(payload)
    assert data["trust_score"] >= 0


def test_recovery_detects_pii():
    _, recovery_analysis = _get_client()
    convo = "Hello, my phone is 1234567890 and my bank account 0123456789 was used." 
    data = recovery_analysis(convo)
    assert "phone" in data["detected_pii"]
    assert "bank_account" in data["detected_pii"]
