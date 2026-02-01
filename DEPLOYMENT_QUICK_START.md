# Deployment Quick Start - 15 Minutes

Fast-track guide to deploy your Todo App to Vercel (backend) + GitHub Pages (frontend).

---

## 🎯 What You Get

| Service | URL | Setup Time | Cost |
|---------|-----|------------|------|
| **Backend (FastAPI)** | `https://your-project.vercel.app` | 3 min | FREE |
| **Frontend (Next.js)** | `https://yourusername.github.io` | 2 min | FREE |
| **Database (Neon)** | PostgreSQL serverless | 2 min | FREE tier |
| **AI Models** | OpenRouter/Gemini | 5 min | FREE tier |

**Total Setup Time:** 15 minutes | **Total Cost:** $0

---

## ⚡ Step 1: Backend to Vercel (3 minutes)

### 1.1 Create Vercel Account
- Go to https://vercel.com → Sign up with GitHub
- Click **New Project** → Select your repo
- Vercel auto-detects `vercel.json` in backend folder ✅

### 1.2 Set Environment Variables
In Vercel Dashboard → Settings → Environment Variables:

```
DATABASE_URL=postgresql://... (from Neon)
JWT_SECRET_KEY=any-random-secret-here
OPENROUTER_API_KEY=sk-or-... (from openrouter.ai)
ALLOWED_ORIGINS=http://localhost:3000,https://yourusername.github.io
ENVIRONMENT=production
```

### 1.3 Deploy
- Click **Deploy** button
- Wait 2-3 minutes
- Get your backend URL: `https://your-project.vercel.app`

✅ **Backend deployed!**

---

## ⚡ Step 2: Frontend to GitHub Pages (2 minutes)

### 2.1 Enable GitHub Pages
- Go to repo **Settings** → **Pages**
- Source: **GitHub Actions** (already configured)
- Click **Save**

### 2.2 Update Next.js Config
`frontend/next.config.ts` should have:

```typescript
const nextConfig: NextConfig = {
  output: "export",  // ← This enables static export
  images: { unoptimized: true },
};
```

### 2.3 Create `.env.production`
In `frontend/` folder, create `.env.production`:

```
NEXT_PUBLIC_API_URL=https://your-project.vercel.app/api/v1
```

(Replace with your actual Vercel backend URL)

### 2.4 Push to GitHub
```bash
git add .
git commit -m "Setup deployment"
git push origin main
```

**Wait for GitHub Actions to complete** (check Actions tab)

✅ **Frontend deployed to GitHub Pages!**

---

## 🧪 Step 3: Test Everything

### Test Backend
```bash
# Health check
curl https://your-project.vercel.app/health

# Should return: {"status": "ok"}
```

### Test Frontend
```bash
# Open in browser
https://yourusername.github.io
```

### Test Connection
1. Click "Sign In" on homepage
2. Create test account
3. Create test task via chat
4. Verify task appears in list

---

## 📊 Deployment Architecture

```
Your Computer (Development)
    ↓ (git push main)
    ↓
GitHub Repository
    ├─ Detects change
    ├─ Triggers GitHub Actions
    │
    ├─→ deploy-backend.yml
    │   ├ Installs Python deps
    │   ├ Runs tests (optional)
    │   └ Deploys to Vercel
    │       ↓
    │       BACKEND LIVE: https://your-project.vercel.app
    │
    └─→ deploy-frontend.yml
        ├ Installs Node deps
        ├ Builds Next.js
        └ Deploys to GitHub Pages
            ↓
            FRONTEND LIVE: https://yourusername.github.io
```

---

## 🗄️ Database Setup (Neon - 2 minutes)

### 3.1 Create Neon Account
- Go to https://neon.tech → Sign up (FREE!)
- Create new project
- Copy connection string

### 3.2 Set DATABASE_URL
```
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require
```

Add this to Vercel environment variables.

### 3.3 Run Migrations (Optional)
```bash
# Locally (one time)
cd backend
python -m alembic upgrade head
```

---

## 🤖 AI Setup (OpenRouter - 2 minutes)

### Choose Your AI Provider

**Option A: OpenRouter (Recommended)**
1. Sign up: https://openrouter.ai
2. Get API key from https://openrouter.ai/keys
3. Copy to Vercel: `OPENROUTER_API_KEY=sk-or-...`

**Option B: Google Gemini (Free tier)**
1. Get API key: https://aistudio.google.com/app/apikey
2. Copy to Vercel: `GEMINI_API_KEY=...`

**Option C: OpenAI**
1. Get API key: https://platform.openai.com/account/api-keys
2. Copy to Vercel: `OPENAI_API_KEY=sk-...`

---

## ✅ Deployment Checklist

### Backend (Vercel)
- [ ] `backend/vercel.json` exists ✅
- [ ] `backend/api/index.py` exists ✅
- [ ] Vercel account created
- [ ] Repository linked to Vercel
- [ ] Environment variables set
- [ ] Vercel deployment complete
- [ ] Health check passes: `https://your-project.vercel.app/health`

### Frontend (GitHub Pages)
- [ ] GitHub Pages enabled
- [ ] `frontend/next.config.ts` has `output: "export"` ✅
- [ ] `frontend/.env.production` created
- [ ] `.github/workflows/deploy-frontend.yml` exists ✅
- [ ] GitHub Actions workflow completed
- [ ] Website loads at `https://yourusername.github.io`

### Database
- [ ] Neon account created
- [ ] `DATABASE_URL` set in Vercel
- [ ] Database connection works

### AI Provider
- [ ] API key obtained
- [ ] Set in Vercel environment variables
- [ ] Chat feature works

---

## 🚨 Troubleshooting

### Backend won't load
```bash
# Check health endpoint
curl https://your-project.vercel.app/health

# If 502 or error:
# 1. Check Vercel logs
# 2. Verify DATABASE_URL is correct
# 3. Verify API keys are set
```

### Frontend shows blank page
```bash
# Check browser console (F12)
# If API errors:
# 1. Verify NEXT_PUBLIC_API_URL in .env.production
# 2. Check if backend is live
# 3. Check CORS settings in backend
```

### API calls return 404
```bash
# Frontend uses wrong URL
# 1. Check NEXT_PUBLIC_API_URL in .env.production
# 2. Make sure backend is deployed first
# 3. Backend URL should be: https://your-project.vercel.app
```

---

## 📚 Full Documentation

For detailed instructions:
- **Complete Guide:** See `DEPLOYMENT_GUIDE.md`
- **GitHub Pages:** See `GITHUB_PAGES_SETUP.md`
- **All Configs:** See `DEPLOYMENT_CONFIG_SUMMARY.md`

---

## 🔐 Important URLs to Save

```
Backend Health:
https://your-project.vercel.app/health

API Docs (Swagger):
https://your-project.vercel.app/docs

Frontend:
https://yourusername.github.io

Vercel Dashboard:
https://vercel.com/dashboard

GitHub Settings:
https://github.com/your-repo/settings/pages

Neon Database:
https://console.neon.tech
```

---

## 🎉 You're Done!

After 15 minutes, you should have:

✅ Backend running on Vercel
✅ Frontend running on GitHub Pages
✅ Database connected
✅ AI features enabled
✅ Auto-deployment on every push

**Next Steps:**
1. Share your live site: `https://yourusername.github.io`
2. Create PRs to test auto-deployment
3. Monitor Vercel/GitHub Actions for issues

---

**Questions?** See `DEPLOYMENT_GUIDE.md` for detailed instructions.

**Last Updated:** 2025-12-11

**Status:** ✅ Ready for production
