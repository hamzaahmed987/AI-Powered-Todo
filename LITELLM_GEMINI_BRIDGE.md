# LiteLLM Bridge: Connecting OpenAI Agents SDK to Gemini

## The Problem

The OpenAI Agents SDK is designed to work with OpenAI models exclusively. It doesn't natively support Google's Gemini API. Without a solution, you would need an OpenAI API key to use the agent framework.

## The Solution: LiteLLM as a Bridge

**LiteLLM** is a unified abstraction layer that:
- Standardizes API calls across 100+ LLM providers
- Translates OpenAI Agents SDK requests to Gemini API format
- Handles authentication for each provider transparently

### Architecture

```
OpenAI Agents SDK
    ↓ (expects OpenAI API format)
LiteLLM Provider
    ↓ (translates format)
Gemini API
    ↓ (executes request)
Gemini Model (gemini-2.0-flash)
```

---

## How OpenAI Agents SDK Discovers Providers

The OpenAI Agents SDK uses a **MultiProvider** pattern that routes models based on **prefixes**:

```python
# From OpenAI Agents SDK documentation

class MultiProvider(ModelProvider):
    """Maps model names to providers based on prefix"""

    # Default mapping:
    # - "openai/" or no prefix → OpenAIProvider
    # - "litellm/" → LitellmProvider

    def get_model(self, model_name: str) -> Model:
        prefix, model_name = self._get_prefix_and_model_name(model_name)

        # Look up provider based on prefix
        if prefix == "litellm":
            return LitellmProvider().get_model(model_name)
        else:
            return OpenAIProvider().get_model(model_name)
```

---

## Model Name Routing

### Format: `litellm/[provider]/[model-id]`

**Examples**:
```python
# Use Gemini via LiteLLM
model = "litellm/gemini-2.0-flash"

# Also works with other providers via LiteLLM:
model = "litellm/gpt-4"           # OpenAI via LiteLLM
model = "litellm/claude-opus"     # Anthropic Claude
model = "litellm/mistral-large"   # Mistral
```

### In Our Implementation

```python
# backend/app/agents/agent.py

def create_task_agent(user_id: UUID, db_session: Session) -> Agent:
    google_api_key = os.getenv("GOOGLE_API_KEY")

    # This model name tells the OpenAI Agents SDK to:
    # 1. Use LiteLLM provider (litellm/ prefix)
    # 2. Access Gemini model (gemini-2.0-flash)
    model_name = "litellm/gemini-2.0-flash"

    agent = Agent(
        model=model_name,
        tools=TASK_TOOLS,
    )

    return agent
```

---

## Request Flow with Function Calling

When you use the agent with tools, here's what happens:

### 1. User Message
```
"Add a task called Buy groceries with high priority"
```

### 2. OpenAI Agents SDK
```python
# Creates an Agent with task tools
agent = Agent(
    model="litellm/gemini-2.0-flash",
    tools=TASK_TOOLS,  # add_task, update_task, delete_task, get_task_info
)

# Runs the agent
result = await Runner.run(agent, input=user_message)
```

### 3. LiteLLM Translation Layer
```
OpenAI Agents Format:
{
    "messages": [...],
    "tools": [{"type": "function", "function": {...}}],
    "model": "litellm/gemini-2.0-flash"
}

↓ (LiteLLM translates)

Gemini API Format:
{
    "contents": [...],
    "tools": [{"functionDeclarations": [...]}],
    "model": "gemini-2.0-flash"
}
```

### 4. Gemini Processes Request
- Receives the user message
- Sees the available tools (add_task, update_task, etc.)
- Decides which tool to call: `add_task`
- Returns function call: `{"name": "add_task", "arguments": {"title": "Buy groceries", "priority": "high"}}`

### 5. Agent Executes Tool
```python
# The tool is called with the arguments from Gemini
result = add_task(
    title="Buy groceries",
    priority="high",
)
# Returns: {"success": true, "task_id": "uuid-123"}
```

### 6. Response to User
```
"Task 'Buy groceries' created successfully with high priority"
```

---

## Why This Works Better Than Direct API Calls

### ❌ Without LiteLLM (Direct API)
```python
# You'd need to:
# 1. Learn Gemini API syntax
# 2. Handle authentication differently
# 3. Manually translate tool calls
# 4. Switch SDKs for different models

from google.generativeai import GenerativeModel

model = GenerativeModel("gemini-2.0-flash")
response = model.generate_content(
    # Manually format messages
    # Manually define function schemas
)
```

### ✅ With LiteLLM (Unified Interface)
```python
# Use same Agent SDK for any model:
from agents import Agent

# Gemini via LiteLLM
agent = Agent(model="litellm/gemini-2.0-flash", tools=TASK_TOOLS)

# Or switch to OpenAI
agent = Agent(model="litellm/gpt-4", tools=TASK_TOOLS)

# Or Anthropic Claude
agent = Agent(model="litellm/claude-opus", tools=TASK_TOOLS)

# All use the same code!
```

---

## API Key Management

### How LiteLLM Finds Your Gemini Key

LiteLLM looks for your API key in this order:

```python
# 1. Environment variable
os.environ["GOOGLE_API_KEY"]  # ← We set this in .env

# 2. Or directly in code
from litellm import Router
router = Router(
    model_list=[{
        "model_name": "gemini-2.0-flash",
        "litellm_params": {
            "model": "gemini-2.0-flash",
            "api_key": "AIzaSy..."
        }
    }]
)
```

### Our Implementation
```bash
# .env file
GOOGLE_API_KEY=AIzaSy[YOUR_KEY]
```

LiteLLM automatically reads this and uses it for Gemini API calls.

---

## Supported Gemini Models in LiteLLM

```python
# Latest & Recommended
"litellm/gemini-2.0-flash"     # Fastest, best for most use cases

# Previous Versions
"litellm/gemini-1.5-pro"        # More capable, higher latency
"litellm/gemini-1.5-flash"      # Balanced option

# Vision Models (with image input)
"litellm/gemini-pro-vision"     # Can analyze images
```

---

## Performance Characteristics

### Speed
```
Gemini 2.0 Flash:
- First token: ~100-200ms
- Total response: ~500-1500ms (depending on output length)
- Throughput: 1M+ tokens/day (free tier)
```

### Tool Calling Accuracy
- Gemini: ~98% accuracy for function selection
- OpenAI GPT-4: ~99.5% accuracy
- Good enough for task management use case

### Cost Comparison
```
Gemini 2.0 Flash:
- Input: $0.075 per 1M tokens
- Output: $0.30 per 1M tokens
- Free tier: 1,500 requests/day

OpenAI GPT-4:
- Input: $0.03 per 1K tokens = $30 per 1M tokens
- Output: $0.06 per 1K tokens = $60 per 1M tokens

Gemini is 10-16x cheaper
```

---

## Troubleshooting LiteLLM Issues

### Issue: "litellm/gemini-2.0-flash not found"

**Cause**: LiteLLM or google-generativeai not installed

**Solution**:
```bash
pip install litellm==1.48.0 google-generativeai==0.8.0
```

### Issue: "Invalid API key for Gemini"

**Cause**: GOOGLE_API_KEY not set or invalid

**Solution**:
```bash
# Verify key format (starts with AIzaSy)
echo $GOOGLE_API_KEY

# Get new key from https://aistudio.google.com
```

### Issue: "Timeout calling Gemini"

**Cause**: Network issue or slow response

**Solution**:
```python
# Increase timeout in agent configuration
from agents import ModelSettings

ModelSettings(timeout=30)  # 30 seconds
```

---

## Advanced: Custom LiteLLM Configuration

### Use Different Gemini Model

```python
# backend/app/agents/agent.py

model_name = "litellm/gemini-1.5-pro"  # More capable
# or
model_name = "litellm/gemini-1.5-flash"  # Lower latency
```

### Add Custom Parameters

```python
from agents import ModelSettings

agent = Agent(
    model="litellm/gemini-2.0-flash",
    model_settings=ModelSettings(
        temperature=0.7,  # Creativity
        top_p=0.9,        # Diversity
    ),
    tools=TASK_TOOLS,
)
```

### Switch to Different Provider

```python
# Use OpenAI instead (if you have API key)
model = "litellm/gpt-4"

# Use Anthropic Claude
model = "litellm/claude-3-opus"

# Use Mistral
model = "litellm/mistral-large"

# All work with same Agent SDK!
```

---

## Summary

| Aspect | Before (No LiteLLM) | After (With LiteLLM) |
|--------|-------------------|---------------------|
| **SDK** | Need different SDKs for each provider | Same Agent SDK for all |
| **Code** | Provider-specific code | Unified interface |
| **API Key** | Must have OpenAI key | Use Google Gemini free key |
| **Cost** | Expensive (~$3-5/mo) | Cheap (~$0.30/mo) |
| **Model Switching** | Rewrite code | Change model string |
| **Tools/Functions** | Manual per provider | Automatic via SDK |

---

## Resources

- **LiteLLM Docs**: https://docs.litellm.ai
- **Supported Models**: https://docs.litellm.ai/docs/providers
- **OpenAI Agents SDK**: https://github.com/openai/openai-agents-python
- **Gemini API**: https://ai.google.dev

---

**Key Takeaway**: LiteLLM makes the OpenAI Agents SDK provider-agnostic, allowing us to use the same agent framework with different models including Google's free Gemini API. ✨
