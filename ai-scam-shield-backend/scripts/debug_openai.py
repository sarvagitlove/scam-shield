import os
import json
try:
    import openai
except Exception as e:
    print('openai import failed:', e)
    raise

openai.api_key = os.getenv('OPENAI_API_KEY')
model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
text = "Analyze the following message for scam/fraud risk and return a JSON object with keys: model_score (0-100), reasons (array), recommended_action. Message:\nSend $500 via Zelle to 123-456-7890 immediately, click http://phish.example.com"

try:
    resp = openai.responses.create(model=model, input=text, temperature=0.2, max_output_tokens=500)
    print('response type:', type(resp))
    # Print top-level keys and small preview of textual output if present
    if hasattr(resp, 'output'):
        print('output length:', len(resp.output))
        # show first 600 chars of rendered text
        out_text = ''
        for item in resp.output:
            if isinstance(item, dict):
                for c in item.get('content', []):
                    if isinstance(c, dict) and 'text' in c:
                        out_text += c['text']
                    elif isinstance(c, str):
                        out_text += c
            elif isinstance(item, str):
                out_text += item
        print('output_preview:', out_text[:600])
    else:
        print('no output attribute on response; resp repr:', repr(resp)[:800])
except Exception as e:
    print('OpenAI call raised exception:', e)
    import traceback
    traceback.print_exc()
