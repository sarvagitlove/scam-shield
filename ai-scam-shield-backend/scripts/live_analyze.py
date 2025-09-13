import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app")))
from core import analyze_text

def main():
    sample = "Send $500 via Zelle to 123-456-7890 immediately, click http://phish.example.com"
    out = analyze_text(sample)
    # redact model_score if present? we'll show it
    import json
    print(json.dumps(out, indent=2))

if __name__ == '__main__':
    main()
