# Gemini + OpenAI Agents SDK - Quick Start (5 minutes)

## TL;DR Setup

### 1. Get Gemini API Key (2 min)
```
https://aistudio.google.com
→ Click "Get API key"
→ Click "Create API key in new project"
→ Copy the key (AIzaSy...)
```

### 2. Set Environment Variable (1 min)
```bash
# Add to .env file
GOOGLE_API_KEY=AIzaSy[YOUR_KEY_HERE]
GEMINI_MODEL=gemini-2.0-flash
```

### 3. Start Backend (1 min)
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### 4. Test Agent (1 min)
Open: http://localhost:8000/docs
→ Click `/api/v1/agent/chat`
→ Try it out
→ Send message: `"Add a task called Buy groceries with high priority"`

---

## How It Works

```
Your Message
    ↓
OpenAI Agents SDK
    ↓
LiteLLM Provider (routes to Gemini)
    ↓
Gemini Model (gemini-2.0-flash)
    ↓
Task Tools (add/update/delete/get)
    ↓
Response
```

**Key Point**: Same Agent SDK, different model via LiteLLM prefix: `litellm/gemini-2.0-flash`

---

## Cost

- **Free Tier**: 1,500 requests/day - $0
- **Paid Tier**: ~$0.30/month for 3,000 requests
- **Comparison**: 10-16x cheaper than OpenAI GPT-4

---

## Common Tasks

### Change Model
Edit `.env`:
```bash
# Options:
# - gemini-2.0-flash (recommended, fastest)
# - gemini-1.5-pro (most capable)
# - gemini-1.5-flash (balanced)

GEMINI_MODEL=gemini-2.0-flash
```

### View API Docs
http://localhost:8000/docs

### Test with cURL
```bash
curl -X POST "http://localhost:8000/api/v1/agent/chat" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add task called Test"}'
```

### Example Agent Requests
- "Add a task called Buy groceries with high priority"
- "Mark my project task as completed"
- "Delete the old task from yesterday"
- "Show me details of my project task"

---

## Troubleshooting

| Error | Solution |
|-------|----------|
| GOOGLE_API_KEY not set | Add to .env: `GOOGLE_API_KEY=AIzaSy...` |
| Invalid API Key | Create new key at https://aistudio.google.com |
| Rate limit exceeded | Free tier: 1,500/day limit (waits 24h) |
| Module not found | Run: `pip install -r requirements.txt` |

---

## File Changes

✅ `backend/app/agents/agent.py` - Uses `litellm/gemini-2.0-flash`
✅ `.env.example` - Shows Gemini config
✅ `requirements.txt` - Includes litellm + google-generativeai

---

## Documentation

- Full setup: `GEMINI_OPENAI_AGENTS_SETUP.md`
- Agent quick ref: `AGENT_QUICK_REFERENCE.md`

---

**Status**: ✅ Ready to use - Free Gemini API via OpenAI Agents SDK
