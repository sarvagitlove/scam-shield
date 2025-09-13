# AI Scam & Fraud Shield

This workspace contains two folders:

- `ai-scam-shield-backend` - FastAPI backend
- `ai-scam-shield-frontend` - Vite + React frontend

Basic run steps (Windows PowerShell):

Backend:
```powershell
python -m pip install -r .\ai-scam-shield-backend\requirements.txt
# set your OpenAI key if you have one:
# $env:OPENAI_API_KEY = 'sk-...'
uvicorn ai-scam-shield-backend.app.main:app --reload --port 8000
```

Frontend:
```powershell
cd .\ai-scam-shield-frontend
npm install
npm run dev
```
