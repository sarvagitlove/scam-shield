import re
import os
import json
from typing import List, Optional

PII_PATTERNS = {
    "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "phone": r"\b\d{10}\b|\(\d{3}\)\s?\d{3}-\d{4}",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "credit_card": r"\b(?:\d[ -]*?){13,16}\b",
    "bank_account": r"\b\d{9,12}\b",
    "dob": r"\b(?:\d{2}[/-]\d{2}[/-]\d{4})\b",
    "passport": r"\b[A-Z0-9]{6,9}\b",
    "address": r"\d{1,5}\s\w+(\s\w+){1,4},?\s?[A-Z]{2}\s?\d{5}"
}

PII_GUIDANCE = {
    "email": "Change your email password and enable 2FA; check account recovery settings.",
    "phone": "Contact your carrier to enable fraud alerts and watch for SIM-swap attempts.",
    "bank_account": "Immediately notify your bank, close compromised accounts, and enable fraud monitoring.",
    "credit_card": "Cancel the card, request a new number, monitor statements, and enable fraud alerts.",
    "ssn": "File a fraud alert with Experian/Equifax/TransUnion, request a credit freeze, and report to SSA/FTC.",
    "dob": "Be cautious of identity theft; combined with other leaks it increases risk.",
    "passport": "Report to the passport office/government, request a reissue, and monitor travel records.",
    "address": "Enable mail forwarding alerts, consider USPS Informed Delivery, and watch for fake accounts."
}


def heuristic_scan(text: str) -> (float, List[str]):
    text_lower = text.lower()
    reasons = []
    score = 100

    suspicious_keywords = ["urgent", "immediately", "act now", "verify", "click here", "password", "wire", "zelle", "venmo", "western union", "transfer"]
    money_keywords = ["payment", "send", "transfer", "pay", "bank", "account", "ssn", "social security"]

    for kw in suspicious_keywords:
        if kw in text_lower:
            reasons.append(f"Found suspicious keyword: {kw}")
            score -= 10

    for kw in money_keywords:
        if kw in text_lower:
            reasons.append(f"Contains money-related word: {kw}")
            score -= 8

    # Links
    if re.search(r"https?://", text_lower):
        reasons.append("Contains link(s)")
        score -= 15

    # Contact patterns
    if re.search(PII_PATTERNS["phone"], text):
        reasons.append("Includes phone number pattern")
        score -= 5

    if re.search(PII_PATTERNS["email"], text):
        reasons.append("Includes email address")
        score -= 5

    # Excessive urgency or all-caps
    if re.search(r"\b(now|today|urgent|asap)\b", text_lower):
        reasons.append("Urgency language detected")
        score -= 10

    score = max(0, min(100, score))
    return score, reasons


def call_openai_model(text: str) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {
            "model_score": 30.0 if "zelle" in text.lower() or "venmo" in text.lower() else 80.0,
            "reasons": ["Model detected patterns consistent with scam"],
            "recommended_action": "Do not respond; block sender and report the message."
        }
    try:
        import openai
        openai.api_key = api_key
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        # Try Responses API
        try:
            resp = openai.responses.create(
                model=model,
                input=(
                    "Analyze the following message for scam/fraud risk and return a JSON object with keys: "
                    "model_score (0-100), reasons (array of strings), recommended_action (short string).\nMessage:\n" + text
                ),
                temperature=0.2,
                max_output_tokens=500,
            )

            content = ""
            if hasattr(resp, "output"):
                for item in resp.output:
                    if isinstance(item, dict):
                        # content can be a list of dicts
                        for c in item.get("content", []):
                            if isinstance(c, dict) and "text" in c:
                                content += c["text"]
                            elif isinstance(c, str):
                                content += c
                    elif isinstance(item, str):
                        content += item
            else:
                content = str(resp)

            try:
                parsed = json.loads(content)
                return parsed
            except Exception:
                import re as _re
                m = _re.search(r"\{[\s\S]*\}", content)
                if m:
                    try:
                        return json.loads(m.group(0))
                    except Exception:
                        pass
                return {"model_score": 50.0, "reasons": ["OpenAI returned unparsable response; see content"], "recommended_action": content[:400]}

        except Exception:
            # Fallback to ChatCompletion if Responses not available
            try:
                resp = openai.ChatCompletion.create(
                    model=model,
                    messages=[{"role": "user", "content": text}],
                    max_tokens=300,
                    temperature=0.2,
                )
                content = resp["choices"][0]["message"]["content"]
                try:
                    parsed = json.loads(content)
                    return parsed
                except Exception:
                    return {"model_score": 50.0, "reasons": ["OpenAI returned unparsable response; see content"], "recommended_action": content[:400]}
            except Exception as e2:
                return {"model_score": 50.0, "reasons": [f"OpenAI call failed: {str(e2)}"], "recommended_action": "Use heuristic guidance."}
    except Exception as e:
        return {"model_score": 50.0, "reasons": [f"OpenAI call failed: {str(e)}"], "recommended_action": "Use heuristic guidance."}


def analyze_text(text: str) -> dict:
    heuristic_score, reasons = heuristic_scan(text)
    model_score = None
    if os.getenv("OPENAI_API_KEY"):
        model_out = call_openai_model(text)
        model_score = model_out.get("model_score")
        reasons += model_out.get("reasons", [])
        recommended_action = model_out.get("recommended_action")
        trust_score = round(0.6 * model_score + 0.4 * heuristic_score, 2)
    else:
        recommended_action = "Follow heuristic guidance: be cautious, do not share more info, block sender."
        trust_score = round(heuristic_score, 2)

    return {
        "trust_score": trust_score,
        "heuristic_score": round(heuristic_score, 2),
        "model_score": model_score,
        "reasons": reasons,
        "recommended_action": recommended_action,
    }


def recovery_analysis(conversation_text: str) -> dict:
    detected = []
    what_to_do = []

    for key, pattern in PII_PATTERNS.items():
        if re.search(pattern, conversation_text):
            detected.append(key)
            what_to_do.append(PII_GUIDANCE.get(key, "Review and take appropriate action."))

    risk_level = "Low"
    if any(k in detected for k in ["ssn", "credit_card", "bank_account"]):
        risk_level = "High"
    elif len(detected) >= 2:
        risk_level = "Medium"

    output = {
        "detected_pii": detected,
        "risk_level": risk_level,
        "what_to_do": what_to_do,
        "documentation": "Scam incident report with detected risks and recovery steps."
    }
    return output
