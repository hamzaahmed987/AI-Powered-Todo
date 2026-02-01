# Deployment Guide - Vercel & GitHub Pages

This guide covers deploying the Todo App backend to **Vercel** and frontend to **GitHub Pages** from a single monorepo.

---

## Architecture Overview

```
Repository (Main Branch)
├── backend/              → Deploy to Vercel
│   ├── api/index.py     → Vercel entry point
│   ├── vercel.json      → Vercel config
│   ├── .vercelignore    → Files to exclude
│   └── requirements.txt  → Python dependencies
│
├── frontend/            → Deploy to GitHub Pages
│   ├── package.json     → Node dependencies
│   ├── next.config.ts   → Next.js config
│   └── app/             → Next.js app
│
└── .github/workflows/
    ├── deploy-backend.yml    → Auto-deploy backend
    └── deploy-frontend.yml   → Auto-deploy frontend
```

---

## Part 1: Backend Deployment (Vercel)

### Step 1: Prepare Backend for Vercel

✅ Already configured with:
- **`backend/vercel.json`** - Vercel configuration
- **`backend/api/index.py`** - Serverless function entry point
- **`backend/.vercelignore`** - Files to exclude from deployment

### Step 2: Create Vercel Account & Project

1. Go to [vercel.com](https://vercel.com) and sign up/login
2. Click **"Add New"** → **"Project"**
3. Import your GitHub repository (Panaversity Hackathon/Todo App)
4. Configure project settings:
   - **Framework Preset:** Other (Python)
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Output Directory:** (leave empty)

### Step 3: Set Environment Variables on Vercel

In Vercel Dashboard → Project Settings → Environment Variables, add:

```
DATABASE_URL=postgresql://user:password@host:5432/todo_db
OPENAI_API_KEY=your-api-key
GEMINI_API_KEY=your-api-key
OPENROUTER_API_KEY=your-api-key
JWT_SECRET=your-jwt-secret-key
ALLOWED_ORIGINS=https://yourusername.github.io,https://your-vercel-domain.vercel.app
```

### Step 4: Deploy to Vercel

**Option A: Manual Deploy (via Dashboard)**
1. In Vercel Dashboard, click **"Deploy"**
2. Wait for deployment to complete
3. Note your Vercel URL: `https://your-backend.vercel.app`

**Option B: Auto-Deploy (via GitHub Actions)**
- GitHub Actions workflow will auto-deploy when `backend/` changes
- Requires GitHub Secrets (see Step 5)

### Step 5: Get Vercel Credentials for GitHub Actions (Optional)

If using auto-deployment via GitHub Actions:

1. Go to Vercel Account Settings → **Tokens**
2. Create new token → copy it
3. Go to GitHub repo → Settings → **Secrets and variables** → **Actions**
4. Add these secrets:
   ```
   VERCEL_TOKEN=your-vercel-token
   VERCEL_ORG_ID=your-org-id (found in Vercel URL)
   VERCEL_PROJECT_ID=your-project-id (found in Vercel URL)
   ```

---

## Part 2: Frontend Deployment (GitHub Pages)

### Step 1: Enable GitHub Pages

1. Go to **GitHub repo** → **Settings** → **Pages**
2. Set source to:
   - **Source:** Deploy from a branch
   - **Branch:** `main` (or your main branch)
   - **Folder:** `/ (root)` → Change to `/frontend` if using subdirectory
3. Save

### Step 2: Configure Next.js for GitHub Pages

Update `frontend/next.config.ts`:

```typescript
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export", // Enable static export for GitHub Pages
  basePath: "/Todo-App", // Use your repo name (optional)
  assetPrefix: "/Todo-App/", // Use your repo name (optional)
  images: {
    unoptimized: true, // Required for static export
  },
};

export default nextConfig;
```

### Step 3: Update API URL for Production

Create `frontend/.env.production`:

```
NEXT_PUBLIC_API_URL=https://your-backend.vercel.app/api/v1
```

Or set it in GitHub Actions (already configured).

### Step 4: GitHub Actions Auto-Deploy

The workflow `.github/workflows/deploy-frontend.yml` automatically:
- ✅ Triggers on push to `main` branch
- ✅ Runs on changes to `frontend/` folder
- ✅ Builds Next.js app
- ✅ Deploys to GitHub Pages

**No manual setup needed!** Just push to trigger.

---

## Part 3: Environment Variables Setup

### Backend Environment Variables

Add to Vercel (and optionally `.env` file):

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/db_name

# JWT
JWT_SECRET=your-super-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS
ALLOWED_ORIGINS=https://yourusername.github.io,https://your-domain.vercel.app,http://localhost:3000

# OpenAI / Alternative AI Providers
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=your-gemini-key
OPENROUTER_API_KEY=your-openrouter-key
OPENROUTER_API_BASE=https://openrouter.ai/api/v1

# App Settings
DEBUG=false
APP_NAME=AI Todo App
APP_VERSION=0.1.0
```

### Frontend Environment Variables

Add to GitHub Actions secrets and `.env.production`:

```bash
NEXT_PUBLIC_API_URL=https://your-backend.vercel.app/api/v1
```

---

## Part 4: Database Setup

### Option A: Neon PostgreSQL (Recommended)

1. Go to [neon.tech](https://neon.tech)
2. Create free PostgreSQL database
3. Copy connection string: `postgresql://user:password@host:5432/db`
4. Set `DATABASE_URL` in Vercel environment variables
5. Run migrations on Vercel:
   ```bash
   # Via Vercel CLI
   vercel env pull
   python -m alembic upgrade head
   ```

### Option B: Supabase

1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Get connection string from Settings → Database
4. Add to Vercel environment variables

### Option C: Traditional PostgreSQL

Use your own hosted PostgreSQL service and add connection string to Vercel.

---

## Part 5: Testing Deployments

### Test Backend

```bash
# Test Vercel backend endpoint
curl https://your-backend.vercel.app/api/v1/health

# Should return: {"status": "ok"}
```

### Test Frontend

```bash
# After deployment, visit:
https://yourusername.github.io/Todo-App

# Or if using custom domain:
https://your-domain.com
```

---

## Part 6: Monitoring & Troubleshooting

### Check Logs

**Backend (Vercel):**
- Vercel Dashboard → Deployments → Select deployment → Logs

**Frontend (GitHub Pages):**
- GitHub → Actions → Select workflow → View logs

### Common Issues

#### Backend 502 Bad Gateway
- Check database connection (DATABASE_URL)
- Verify all environment variables are set
- Check Vercel logs for Python errors

#### Frontend Shows Blank Page
- Check browser console for API errors
- Verify `NEXT_PUBLIC_API_URL` points to correct Vercel domain
- Ensure CORS is configured in backend

#### CORS Errors
- Add frontend URL to `ALLOWED_ORIGINS` in backend
- Example: `https://yourusername.github.io`

---

## Part 7: Custom Domain (Optional)

### Frontend Custom Domain

1. Buy domain (GoDaddy, Namecheap, etc.)
2. GitHub Pages Settings → Custom domain
3. Add your domain and update DNS records

### Backend Custom Domain

1. In Vercel Dashboard → Project Settings → Domains
2. Add your custom domain
3. Follow DNS configuration instructions

---

## Part 8: Continuous Integration Checklist

- [ ] `backend/vercel.json` created ✅
- [ ] `backend/api/index.py` created ✅
- [ ] `backend/.vercelignore` created ✅
- [ ] `.github/workflows/deploy-backend.yml` created ✅
- [ ] `.github/workflows/deploy-frontend.yml` created ✅
- [ ] Vercel account created
- [ ] Vercel project linked to GitHub
- [ ] Environment variables set on Vercel
- [ ] GitHub Pages enabled
- [ ] `NEXT_PUBLIC_API_URL` configured in frontend
- [ ] Database provisioned (Neon/Supabase)
- [ ] GitHub Secrets set (if using auto-deploy)

---

## Quick Reference

| Component | Host | Entry Point | Config |
|-----------|------|-------------|--------|
| Backend | Vercel | `backend/api/index.py` | `backend/vercel.json` |
| Frontend | GitHub Pages | `frontend/` | `.github/workflows/deploy-frontend.yml` |
| Database | Neon/Supabase | External | `DATABASE_URL` env var |

---

## Deployment Workflow

```
Git Push to main
    ↓
GitHub Actions Trigger
    ├→ Backend Workflow
    │   ├ Run tests
    │   ├ Deploy to Vercel
    │   └ Get Vercel URL
    │
    └→ Frontend Workflow
        ├ Build Next.js
        ├ Export static files
        └ Deploy to GitHub Pages
    ↓
Live on Vercel + GitHub Pages
```

---

## Support & Resources

- [Vercel FastAPI Docs](https://vercel.com/docs/frameworks/fastapi)
- [GitHub Pages Docs](https://docs.github.com/en/pages)
- [Next.js Static Export](https://nextjs.org/docs/pages/building-your-application/deploying/static-exports)
- [Neon Database](https://neon.tech/docs)

---

## Next Steps

1. **Push your code** to GitHub
2. **Create Vercel project** and link repository
3. **Set environment variables** on Vercel dashboard
4. **Verify deployments** work correctly
5. **Update API URL** in frontend if needed
6. **Test full flow** (auth → tasks → chat)

---

**Status:** ✅ Deployment configuration ready for production

Last updated: 2025-12-11
