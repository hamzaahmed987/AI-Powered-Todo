# LiteLLM Parameter Dropping Fix - Gemini Integration

## Problem Statement

The OpenAI Agents SDK automatically sends the `extra_headers` parameter containing `User-Agent: Agents/Python 0.1.0` when making API calls. However, Google Gemini doesn't support this parameter, resulting in:

```
litellm.exceptions.UnsupportedParamsError:
gemini does not support parameters: {'extra_headers': {'User-Agent': 'Agents/Python 0.1.0'}}
```

## Root Cause

- ✅ OpenAI Agents SDK works with OpenAI models (which support `extra_headers`)
- ❌ Gemini doesn't support `extra_headers` parameter
- ❌ LiteLLM was not configured to drop unsupported parameters
- ❌ Error occurred when SDK tried to pass this to Gemini

## Solution (Per Official LiteLLM Docs)

Enable LiteLLM's parameter dropping feature globally by setting:

```python
import litellm
litellm.drop_params = True
```

This tells LiteLLM to **automatically drop any parameters not supported by the target provider** (Gemini in this case).

## Changes Made

### File: `app/agents/agent.py`

```python
import litellm

# Configure LiteLLM to drop unsupported parameters (like extra_headers from Agents SDK)
# Gemini doesn't support all parameters that OpenAI Agents SDK sends
litellm.drop_params = True
```

**Added at**: Lines 12, 20-22

### File: `app/services/ai_service.py`

```python
try:
    import litellm  # ← Added import
    from agents import Agent, Runner, ModelSettings, set_tracing_disabled
    from agents.extensions.models.litellm_model import LitellmModel
    AGENTS_AVAILABLE = True
except ImportError:
    ...

# Configure LiteLLM to drop unsupported parameters
litellm.drop_params = True  # ← Added at module level
```

**Added at**: Lines 17, 29-31

## How It Works

### Before (❌ Error)
```
OpenAI Agents SDK
    ↓
agent.run("user message")
    ↓
SDK sends: {
    "model": "gemini/gemini-2.0-flash",
    "messages": [...],
    "extra_headers": {"User-Agent": "Agents/Python 0.1.0"}  ← Gemini doesn't support
}
    ↓
LiteLLM tries to pass to Gemini API
    ↓
Gemini rejects: "UnsupportedParamsError: extra_headers not supported"
```

### After (✅ Working)
```
OpenAI Agents SDK
    ↓
agent.run("user message")
    ↓
SDK sends: {
    "model": "gemini/gemini-2.0-flash",
    "messages": [...],
    "extra_headers": {"User-Agent": "Agents/Python 0.1.0"}
}
    ↓
LiteLLM receives (with drop_params=True)
    ↓
LiteLLM filters: "extra_headers not supported by Gemini, dropping it"
    ↓
LiteLLM passes to Gemini API: {
    "model": "gemini/gemini-2.0-flash",
    "messages": [...]
}
    ↓
Gemini accepts and responds ✅
```

## Parameters Affected

LiteLLM will automatically drop these unsupported parameters for Gemini:
- `extra_headers` - Custom HTTP headers
- `temperature` (if not supported)
- `top_p` (if not supported)
- Any other OpenAI-specific parameters not supported by Gemini

## Alternative Approaches (Not Recommended)

### 1. Per-Request Dropping
```python
response = litellm.completion(
    model="gemini/gemini-2.0-flash",
    messages=[...],
    drop_params=True  # For this call only
)
```
Less recommended - affects individual calls only.

### 2. Specific Parameter Dropping
```python
response = litellm.completion(
    model="gemini/gemini-2.0-flash",
    messages=[...],
    additional_drop_params=["extra_headers"]  # Drop only this
)
```
Less recommended - requires manual parameter tracking.

## Official Documentation

- **Source**: LiteLLM official documentation (via context7)
- **Feature**: Drop Params Guide
- **Repository**: https://github.com/berriai/litellm

## Benefits of This Fix

✅ Single line change solves the issue
✅ Automatically handles all unsupported parameters
✅ No need to modify SDK or Agent code
✅ Works with any provider's parameter limitations
✅ Official LiteLLM recommended approach
✅ Safe operation - only drops unsupported params
✅ Future-proof for other providers

## Testing

After applying this fix:

```bash
# Start backend
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Should start without UnsupportedParamsError
# Should see logs: "Task Manager Assistant" agent initialized
# Should be able to call /agent/chat endpoint without errors
```

## Related Issues

This fix addresses:
- ❌ "gemini does not support parameters: {'extra_headers': ...}"
- ❌ Any other parameter compatibility issues between OpenAI Agents SDK and Gemini
- ❌ Future parameter mismatches with other providers

## Impact on Functionality

✅ **No negative impact**
- Agent functionality unchanged
- Message processing unchanged
- Tool execution unchanged
- Only filters out unsupported parameters

❌ **Parameters dropped**
- `extra_headers` with User-Agent info (not used by Gemini anyway)
- Any other Gemini-unsupported parameters

## Configuration Summary

| Setting | Value | Purpose |
|---------|-------|---------|
| `litellm.drop_params` | `True` | Drop unsupported parameters |
| Module | `agent.py`, `ai_service.py` | Applied at module load time |
| Scope | Global | Applies to all LiteLLM calls |
| Impact | Parameter filtering only | No functional impact |

## Rollback

If needed to disable:
```python
litellm.drop_params = False
```

But this is not recommended - parameters will be unsupported again.

## Files Modified

- ✅ `app/agents/agent.py` - Added litellm import and drop_params setting
- ✅ `app/services/ai_service.py` - Added litellm import and drop_params setting

## Summary

One simple configuration fixes the entire parameter incompatibility issue:

```python
import litellm
litellm.drop_params = True
```

This allows OpenAI Agents SDK to work seamlessly with Google Gemini by automatically dropping unsupported parameters.

🎉 **Issue Resolved!**
