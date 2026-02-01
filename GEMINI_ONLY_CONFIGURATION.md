# Gemini-Only Configuration for OpenAI Agents SDK
## No OpenAI API Key Required

**Date**: December 9, 2025
**Reference**: OpenAI Agents SDK v0.1.0 Context7 Documentation
**Status**: ⚠️ CRITICAL ISSUE FOUND - Needs Immediate Fix

---

## The Issue

Current implementation **requires an OpenAI API key** because OpenAI Agents SDK enables tracing by default, which tries to export traces to OpenAI's dashboard.

According to official Context7 documentation, if you're using **only Gemini API without OpenAI**, you must **disable tracing**.

---

## Official Context7 Documentation

### Pattern 1: Gemini-Only WITHOUT Tracing (Your Use Case)

Source: Context7 - `/openai/openai-agents-python/llms.txt`

```python
import asyncio
from agents import Agent, Runner, set_tracing_disabled
from agents.extensions.models.litellm_model import LitellmModel

# CRITICAL: Disable tracing if you're NOT using OpenAI API key
set_tracing_disabled(disabled=True)

async def main():
    # Use Google Gemini via LiteLLM (NO OpenAI API key needed)
    gemini_agent = Agent(
        name="Gemini Assistant",
        model=LitellmModel(
            model="gemini/gemini-2.0-flash",
            api_key="your-gemini-key"  # Only Gemini key needed
        )
    )

    result = await Runner.run(gemini_agent, "Explain quantum computing.")
    print(result.final_output)

asyncio.run(main())
```

**Key Points:**
- ✅ `set_tracing_disabled(disabled=True)` - **REQUIRED** for Gemini-only
- ✅ Only `GEMINI_API_KEY` environment variable needed
- ✅ No `OPENAI_API_KEY` required
- ✅ No OpenAI account required

---

### Pattern 2: Gemini WITH Tracing to OpenAI Dashboard (NOT Your Case)

Source: Context7 - `/openai/openai-agents-python/llms.txt`

```python
import os
from agents import set_tracing_export_api_key, Agent, Runner
from agents.extensions.models.litellm_model import LitellmModel

# If you want tracing, you need OpenAI API key (but NOT for the model)
tracing_api_key = os.environ["OPENAI_API_KEY"]
set_tracing_export_api_key(tracing_api_key)

model = LitellmModel(
    model="gemini/gemini-2.0-flash",  # Model uses Gemini
    api_key="your-gemini-key"
)

agent = Agent(
    name="Assistant",
    model=model,
)
```

**When to use:** Only if you want to monitor agent execution in OpenAI dashboard AND have an OpenAI account.

---

## Your Current Implementation Issue

**File**: `backend/app/services/ai_service.py`

**Current Code** (PROBLEM):
```python
from agents import Agent, Runner, ModelSettings  # ❌ Missing set_tracing_disabled
from agents.extensions.models.litellm_model import LitellmModel

# No tracing disabled call = tries to use OpenAI API for tracing
model = LitellmModel(
    model="gemini/gemini-2.0-flash",
    api_key=GEMINI_API_KEY,
)

agent = Agent(
    name="TaskAnalyzer",
    model=model,
    model_settings=ModelSettings(temperature=0.3),
)
```

**Problem**: OpenAI Agents SDK will attempt to export tracing data to OpenAI backend, which requires an `OPENAI_API_KEY` environment variable. This will cause:
- ❌ Error if `OPENAI_API_KEY` is not set
- ❌ Unnecessary API calls to OpenAI
- ❌ Potential cost even if you're not using OpenAI models

---

## Required Fix

### Fix: Add `set_tracing_disabled(True)` Call

**File**: `backend/app/services/ai_service.py`

**Change 1 - Update imports (line 17)**:
```python
# OLD
from agents import Agent, Runner, ModelSettings

# NEW
from agents import Agent, Runner, ModelSettings, set_tracing_disabled
```

**Change 2 - Call set_tracing_disabled at module level (after imports)**:

Add this line at the very top of the module, right after imports (around line 24):
```python
# Disable tracing since we're using Gemini API, not OpenAI
set_tracing_disabled(disabled=True)
```

**Complete updated section** (lines 15-30):
```python
# Lazy imports to avoid errors if packages not installed
try:
    from agents import Agent, Runner, ModelSettings, set_tracing_disabled
    from agents.extensions.models.litellm_model import LitellmModel
    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False
    logger.warning("OpenAI Agents SDK not installed. AI features will be disabled.")

# Disable tracing since we're using only Gemini API (no OpenAI)
set_tracing_disabled(disabled=True)

# Gemini API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
```

---

## Environment Variable Update

### config.py - Remove OpenAI API Key Requirement

**Current config.py** (PROBLEM):
```python
if not self.gemini_api_key and not self.is_development:
    raise ValueError("GEMINI_API_KEY must be set for non-development environments")
```

This is correct, but we should NOT require OPENAI_API_KEY anymore.

### .env.example - NO OpenAI API Key Section

Your `.env.example` is already correct - it uses only `GEMINI_API_KEY`:

```bash
# Google Gemini Configuration
GEMINI_API_KEY=AIzaSy[YOUR_GEMINI_API_KEY_HERE]
```

✅ **No `OPENAI_API_KEY` section needed**

---

## Configuration Checklist

After applying fixes:

- [ ] `ai_service.py` imports `set_tracing_disabled`
- [ ] `set_tracing_disabled(disabled=True)` called at module level
- [ ] `.env` file has `GEMINI_API_KEY` set
- [ ] `.env` file does NOT have `OPENAI_API_KEY`
- [ ] `config.py` requires `GEMINI_API_KEY` only
- [ ] No `OPENAI_API_KEY` in environment variables
- [ ] No OpenAI account or API key needed

---

## Testing Without OpenAI API Key

### Test 1: Verify tracing is disabled

```bash
cd backend
uv run python -c "
from agents import get_trace_provider
print('Tracing disabled:', get_trace_provider()._disabled)
"
```

Expected output:
```
Tracing disabled: True
```

### Test 2: Test with only GEMINI_API_KEY

```bash
# Make sure OPENAI_API_KEY is NOT set
unset OPENAI_API_KEY  # On Windows: set OPENAI_API_KEY=

# Set only GEMINI_API_KEY
export GEMINI_API_KEY="AIzaSy..."

# Start backend
uv run uvicorn app.main:app --reload
```

Should start without errors ✓

### Test 3: Create task with AI suggestion

```bash
# Should work without OPENAI_API_KEY set
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"title": "Test task", "description": "Test"}'
```

Should create task and generate AI suggestions ✓

---

## Why Tracing is Disabled

| Feature | With Tracing | Without Tracing |
|---------|--------------|-----------------|
| **OpenAI API Key** | ✅ Required | ❌ Not needed |
| **Gemini API Key** | ✅ Required | ✅ Required |
| **OpenAI Account** | ✅ Required | ❌ Not needed |
| **Trace Visibility** | ✅ Dashboard | ❌ Not available |
| **Cost** | $ (potential) | FREE (Gemini free tier) |
| **Complexity** | Higher | Simpler |

**For your use case**: Disable tracing to use only Gemini API without OpenAI.

---

## Future: Enable Tracing (Optional)

If in the future you want to monitor agent execution:

```python
from agents import set_tracing_export_api_key
import os

# Only if you have OpenAI account AND want tracing
openai_key = os.getenv("OPENAI_API_KEY")
if openai_key:
    set_tracing_export_api_key(openai_key)
    # set_tracing_disabled(False)  # Enable tracing
```

But this is **optional** - your system works perfectly without it.

---

## Summary

**Your current implementation with the fix**:

✅ Uses **only Gemini API**
✅ No OpenAI API key required
✅ No OpenAI account required
✅ Free tier Gemini (1500 requests/day)
✅ Simple configuration
✅ Fully compliant with OpenAI Agents SDK documentation

**One-line fix**: Add `set_tracing_disabled(disabled=True)` to `ai_service.py`

---

## References

- **OpenAI Agents SDK**: Configure OpenAI Agents with LiteLLM for Multiple LLM Providers
- **Context7 Documentation**: `/openai/openai-agents-python/llms.txt`
- **Official Source**: https://github.com/openai/openai-agents-python/blob/main/docs/models/litellm.md
