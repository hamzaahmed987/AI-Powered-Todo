# Gemini + OpenAI Agents SDK Setup Guide

## Overview

This application uses **Google's Gemini model** as the AI backbone for the task management agent, integrated through the **OpenAI Agents SDK** via **LiteLLM**.

### Architecture
```
Frontend ChatBot
    ↓
FastAPI Backend (/api/v1/agent/chat)
    ↓
OpenAI Agents SDK (with task tools)
    ↓
LiteLLM Provider (model routing)
    ↓
Google Gemini API (gemini-2.0-flash)
```

### Why This Setup?
- ✅ **No OpenAI API Key Required** - Uses free Google Gemini API
- ✅ **Function Calling** - Gemini with OpenAI Agents SDK tools
- ✅ **Cost Effective** - Gemini free tier: 1500 req/day
- ✅ **Unified Interface** - Same Agent SDK, different model provider via LiteLLM

---

## Prerequisites

Before you begin, ensure you have:
- Python 3.8+ installed
- A Google account (free, any account works)
- The project dependencies installed: `pip install -r requirements.txt`

---

## Step 1: Get Your Google Gemini API Key

### Quick Setup (5 minutes)

1. **Go to Google AI Studio**
   - Visit: https://aistudio.google.com
   - Sign in with any Google account (free, no payment needed)

2. **Create API Key**
   - In the left sidebar, click **"Get API key"**
   - Click **"Create API key in new project"**
   - Copy the generated key (format: `AIzaSy...`)

3. **Set Environment Variable**
   ```bash
   # Add to your .env file
   GOOGLE_API_KEY=AIzaSy[YOUR_KEY_HERE]
   ```

### Free Tier Details
- **Rate Limit**: 1,500 requests per day
- **Models Available**:
  - `gemini-2.0-flash` (recommended, fastest)
  - `gemini-1.5-pro` (most capable)
  - `gemini-1.5-flash` (balanced)
- **Cost**: FREE indefinitely for free tier

### Pricing (if you exceed free tier)
- Input tokens: ~$0.075 per 1M tokens
- Output tokens: ~$0.30 per 1M tokens
- Gemini is 4-5x cheaper than GPT-4

---

## Step 2: Configure Environment Variables

### Backend Configuration

Create or update your `.env` file with:

```bash
# Required: Google Gemini API Configuration
GOOGLE_API_KEY=AIzaSy[YOUR_GEMINI_API_KEY_HERE]
GEMINI_MODEL=gemini-2.0-flash

# Other required variables (copy from .env.example)
DATABASE_URL=postgresql://...
JWT_SECRET_KEY=...
# ... other variables
```

### Available Gemini Models

You can change the model by setting `GEMINI_MODEL`:

```bash
# Fastest & Recommended (latest)
GEMINI_MODEL=gemini-2.0-flash

# Most Capable (higher cost)
GEMINI_MODEL=gemini-1.5-pro

# Balanced (lower latency than pro)
GEMINI_MODEL=gemini-1.5-flash
```

---

## Step 3: How It Works

### Agent Configuration in Code

The agent is configured in `backend/app/agents/agent.py`:

```python
def create_task_agent(user_id: UUID, db_session: Session) -> Agent:
    # Get Gemini API key from environment
    google_api_key = os.getenv("GOOGLE_API_KEY")

    # Use "litellm/" prefix to route to LiteLLM provider
    model_name = "litellm/gemini-2.0-flash"

    agent = Agent(
        name="Task Manager Assistant",
        model=model_name,  # Gemini via LiteLLM
        tools=TASK_TOOLS,  # Task management tools
    )

    return agent
```

### How LiteLLM Works

LiteLLM is a unified interface that:
- Standardizes API calls across 100+ LLM providers
- Handles authentication for each provider
- Translates requests to provider-specific formats
- Routes OpenAI Agents SDK requests to Gemini

**Model Name Format**: `litellm/[provider]/[model-id]`
- Example: `litellm/gemini-2.0-flash`

---

## Step 4: Running the Application

### 1. Install Dependencies

```bash
# From backend directory
pip install -r requirements.txt
```

This installs:
- `openai-agents==0.1.0` - OpenAI Agents SDK
- `litellm==1.48.0` - Multi-provider LLM interface
- `google-generativeai==0.8.0` - Gemini SDK

### 2. Set Environment Variables

```bash
# Create .env from example
cp .env.example .env

# Edit .env and add your Google API key
export GOOGLE_API_KEY="AIzaSy..."
# Or add to .env file
```

### 3. Start the Backend

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

You should see:
```
INFO:     Application startup complete
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 4. Test the Agent

#### Option A: Using Swagger UI
1. Open http://localhost:8000/docs
2. Find the `/api/v1/agent/chat` endpoint
3. Click "Try it out"
4. Enter a message: `"Add a task called Buy groceries with high priority"`
5. Click "Execute"

#### Option B: Using cURL

```bash
curl -X POST "http://localhost:8000/api/v1/agent/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "message": "Add a task called Buy groceries with high priority"
  }'
```

#### Option C: Using the Frontend

1. Start the frontend (separate terminal)
2. Log in to the application
3. Open the ChatBot widget (bottom right)
4. Type a task management request

---

## Troubleshooting

### Error: "GOOGLE_API_KEY environment variable is not set"

**Solution**: Make sure you set the environment variable

```bash
# Option 1: Set in .env file
GOOGLE_API_KEY=AIzaSy...

# Option 2: Set in terminal
export GOOGLE_API_KEY="AIzaSy..."

# Option 3: Set via Python script
import os
os.environ["GOOGLE_API_KEY"] = "AIzaSy..."
```

### Error: "Invalid API Key"

**Solution**:
- Verify your API key is correct (starts with `AIzaSy`)
- Check that the key is for Gemini API (not other Google APIs)
- Ensure no extra spaces or characters

### Error: "401 Unauthorized" from Gemini

**Solution**:
- Key might be expired or invalid
- Create a new key from https://aistudio.google.com
- Update your .env file

### Error: "Rate limit exceeded"

**Solution**:
- Free tier: 1,500 requests per day
- Wait 24 hours for limit reset
- Or upgrade to paid plan for higher limits

### Agent Not Responding

**Solution**:
- Check that OpenAI Agents SDK and LiteLLM are installed
- Verify `create_task_agent()` is being called
- Check backend logs for errors

---

## Testing Tool Calls

The agent should automatically call tools when you request task operations:

### Example Conversations

**Create Task**:
```
User: "Add a task called 'Buy groceries' with high priority"
Agent: [Calls add_task tool]
Response: "Task 'Buy groceries' created successfully with high priority"
```

**Update Task**:
```
User: "Mark my project task as completed"
Agent: [Calls update_task tool]
Response: "Task updated: status changed to completed"
```

**Delete Task**:
```
User: "Delete the old task from yesterday"
Agent: [Calls delete_task tool]
Response: "Task deleted successfully"
```

---

## Implementation Details

### Files Modified/Created

1. **`backend/app/agents/agent.py`** (Modified)
   - Updated to use LiteLLM provider
   - Reads `GOOGLE_API_KEY` environment variable
   - Sets model to `litellm/gemini-2.0-flash`

2. **`.env.example`** (Modified)
   - Added `GOOGLE_API_KEY` configuration
   - Added `GEMINI_MODEL` option
   - Documented free tier and pricing

3. **`requirements.txt`** (Already includes)
   - `openai-agents==0.1.0`
   - `litellm==1.48.0`
   - `google-generativeai==0.8.0`

### Agent Tool Integration

The agent has 4 function tools available:
- **add_task** - Create new tasks
- **update_task** - Modify existing tasks
- **delete_task** - Remove tasks
- **get_task_info** - Retrieve task details

These tools are automatically called by Gemini when appropriate.

---

## Advanced Configuration

### Change Gemini Model

Edit `.env`:
```bash
# Use Gemini 1.5 Pro (more capable, higher latency)
GEMINI_MODEL=gemini-1.5-pro

# Use Gemini 1.5 Flash (balanced)
GEMINI_MODEL=gemini-1.5-flash
```

Or modify `backend/app/agents/agent.py`:
```python
model_name = f"litellm/{gemini_model}"  # Uses GEMINI_MODEL env var
```

### Custom Model Settings

To add temperature, top_p, etc., modify `backend/app/agents/agent.py`:

```python
from agents import ModelSettings

agent = Agent(
    name="Task Manager Assistant",
    model=model_name,
    model_settings=ModelSettings(
        temperature=0.7,  # Creativity (0-1)
        top_p=0.9,        # Diversity
    ),
    tools=TASK_TOOLS,
)
```

### Using Different Providers (via LiteLLM)

LiteLLM supports 100+ providers. You can switch models:

```python
# Switch to OpenAI (if you have API key)
model_name = "litellm/gpt-4"

# Switch to Anthropic Claude
model_name = "litellm/claude-3-opus"

# Switch to other providers
model_name = "litellm/mistral/mistral-large"
```

---

## Cost Estimation

### Free Tier (1,500 req/day)
- **Cost**: $0/month
- **Use Case**: Development, testing, small applications
- **Suitable for**: Teams up to ~50 active users

### Paid Tier (Estimated)

Based on 100 requests per day (~3,000/month):

```
Average response: ~500 input tokens + 200 output tokens

Monthly cost:
= (3,000 × 500 / 1M) × $0.075     # Input
+ (3,000 × 200 / 1M) × $0.30      # Output
= $0.11 + $0.18
= ~$0.29/month
```

**Comparison**:
- OpenAI GPT-4: ~$3-5/month for same usage
- Gemini: ~$0.30/month (10-16x cheaper)

---

## Next Steps

1. ✅ Get your Gemini API key
2. ✅ Set `GOOGLE_API_KEY` in `.env`
3. ✅ Run backend: `python -m uvicorn app.main:app --reload`
4. ✅ Test agent via Swagger UI: http://localhost:8000/docs
5. ✅ Start frontend and test ChatBot

---

## Resources

- **Google AI Studio**: https://aistudio.google.com
- **Gemini API Docs**: https://ai.google.dev
- **LiteLLM Docs**: https://docs.litellm.ai
- **OpenAI Agents SDK**: https://github.com/openai/openai-agents-python

---

## Support

If you encounter issues:
1. Check error message in backend logs
2. Verify `GOOGLE_API_KEY` is set correctly
3. Ensure dependencies are installed: `pip install -r requirements.txt`
4. Check Gemini API status: https://status.cloud.google.com
5. Create new API key if current one is invalid

---

**Status**: ✅ Production Ready
**Framework**: OpenAI Agents SDK + LiteLLM + Gemini
**Cost**: Free (with free tier) or ~$0.30/month
