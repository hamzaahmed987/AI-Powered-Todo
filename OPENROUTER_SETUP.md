# OpenRouter Setup Guide

## What Changed

Your Todo App has been updated to use **OpenRouter with Qwen models** instead of Gemini. This gives you **unlimited free AI access** without rate limits!

### Benefits:
- ✅ **Unlimited free requests** - No 1500 req/day limit like Gemini
- ✅ **High-quality Qwen models** - 72B parameters, excellent performance
- ✅ **No payment required** - Completely free tier
- ✅ **Easy setup** - Just get an API key and paste it

## Files Updated

```
backend/app/agents/
├── openrouter_client.py        [NEW] - OpenRouter API configuration
├── agent.py                     [UPDATED] - Now uses OpenRouter
└── gemini_client.py            [DEPRECATED] - No longer used

.env                             [UPDATED] - OpenRouter API key config
.env.example                     [UPDATED] - Documentation
```

## Quick Setup (5 minutes)

### Step 1: Get OpenRouter API Key

1. Go to **https://openrouter.ai**
2. Click **"Sign up"** (free, no payment required)
3. Create account with email
4. Go to **https://openrouter.ai/keys**
5. Click **"Create new API key"**
6. Copy the generated API key

### Step 2: Update Your .env File

Open `backend/.env` and replace this line:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

With your actual API key:

```env
OPENROUTER_API_KEY=sk-or-v1-abc123xyz...  # Paste your key here
```

That's it! 🎉

## Configuration Options

### Default Model (Recommended)

The app uses **qwen/qwen-2.5-72b-instruct** by default - excellent balance of quality and speed.

```env
# In .env file
OPENROUTER_MODEL=qwen/qwen-2.5-72b-instruct
```

### Alternative Models (All Free!)

You can switch to any of these models:

```env
# Reasoning model - great for complex tasks
OPENROUTER_MODEL=qwen/qwq-32b

# Lightweight & fast
OPENROUTER_MODEL=qwen/qwen-1.5-0.5b-chat

# Browse all models at: https://openrouter.ai/models
```

## How to Use

Once configured, your backend will automatically:

1. ✅ Parse natural language task commands
2. ✅ Create, update, and delete tasks intelligently
3. ✅ Suggest priorities based on task description
4. ✅ Handle unlimited requests (no rate limiting!)

Example usage in chat:
- "Create a task to buy groceries with high priority"
- "Mark the airport task as completed"
- "Delete the project meeting task"

## Troubleshooting

### Issue: "OPENROUTER_API_KEY environment variable not set"

**Solution:** Make sure you:
1. Opened the correct `.env` file (should be in `backend/` directory)
2. Replaced `your_openrouter_api_key_here` with your actual key
3. Saved the file
4. Restarted the backend server

### Issue: "Invalid API key"

**Solution:**
1. Verify the key is correct (copy from https://openrouter.ai/keys)
2. Make sure there are no extra spaces before/after the key
3. Create a new API key if the old one was revoked

### Issue: Model not working

**Solution:**
1. Check https://openrouter.ai/models for available models
2. Verify model name format: `vendor/model-name`
3. Ensure the model is free (most Qwen models are)

## API Rate Limits

OpenRouter's free tier has **no strict rate limits** unlike Gemini. However:

- **Recommended:** Keep requests to 1-5 per minute for stability
- **Maximum burst:** Up to 100 requests in a minute
- **No daily limit:** Make as many requests as you want!

## Comparison: Gemini vs OpenRouter

| Feature | Gemini | OpenRouter |
|---------|--------|-----------|
| **Free Tier** | 1500 req/day | Unlimited |
| **Model Quality** | Excellent | Excellent (Qwen 72B) |
| **Setup Time** | 2 min | 3 min |
| **Rate Limits** | Strict | None |
| **Payment Required** | Eventually | Never |

## What's the Same

Everything else in your app remains unchanged:

- ✅ Frontend (React, Next.js) - unchanged
- ✅ Database (PostgreSQL/Neon) - unchanged
- ✅ Task management features - unchanged
- ✅ Task tools (create, update, delete) - unchanged

Only the LLM provider switched from Gemini → OpenRouter.

## Getting Help

- **OpenRouter Issues:** https://openrouter.ai/docs
- **OpenRouter Status:** https://status.openrouter.ai
- **Models List:** https://openrouter.ai/models
- **Community:** https://github.com/OpenRouterTeam/openrouter-js

## Next Steps

1. ✅ Get API key from https://openrouter.ai/keys
2. ✅ Update `backend/.env` with your key
3. ✅ Restart backend server
4. ✅ Test with a task creation via chat

Your app is now ready for **unlimited free AI-powered task management**! 🚀
