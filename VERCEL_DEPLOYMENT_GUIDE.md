# Vercel Frontend Deployment Guide

This guide walks you through deploying the Next.js frontend on Vercel.

---

## Prerequisites

- GitHub account with the repository connected
- Vercel account (free tier available at vercel.com)
- Backend API running (on Vercel or another host)

---

## Quick Start (5 minutes)

### Step 1: Connect GitHub to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Sign in with GitHub
3. Click **"Import Project"**
4. Select your **AI-Powered-Todo** repository
5. Click **"Import"**

### Step 2: Configure Project Settings

Vercel will auto-detect Next.js. On the import screen:

- **Framework Preset:** Next.js (auto-detected ✓)
- **Root Directory:** `frontend`
- **Build Command:** `npm run build` (auto-filled ✓)
- **Install Command:** `npm install` (auto-filled ✓)
- **Output Directory:** `.next` (auto-filled ✓)

Click **"Deploy"** — deployment starts automatically!

### Step 3: Set Environment Variables

After deployment, configure production environment variables:

1. Go to your Vercel project dashboard
2. Click **Settings** → **Environment Variables**
3. Add:
   ```
   NEXT_PUBLIC_API_URL: https://your-backend.vercel.app/api/v1
   NEXT_PUBLIC_APP_ENV: production
   NEXT_PUBLIC_APP_NAME: AI Todo App
   ```

4. Click **"Save"**
5. Go to **Deployments** → Click latest → **Redeploy** to apply env vars

Your site is now live at: `https://your-project-name.vercel.app`

---

## Step-by-Step Deployment

### Using Vercel CLI (Alternative)

If you prefer command line:

```bash
# 1. Install Vercel CLI
npm i -g vercel

# 2. Navigate to frontend directory
cd frontend

# 3. Deploy
vercel --prod

# 4. Follow prompts
#    - Link to existing project? → no (first time)
#    - Project name? → ai-powered-todo-frontend
#    - Directory? → ./
#    - Build command? → npm run build
#    - Output directory? → .next
```

### Automatic Deployments

Once connected, Vercel automatically deploys when you:
- Push to `001-todo-cli` branch
- Or any branch you configured

**Preview deployments** for pull requests are also automatic!

---

## Configuration Files

### vercel.json

Already configured in `frontend/vercel.json`:

```json
{
  "buildCommand": "npm run build",
  "installCommand": "npm install",
  "framework": "nextjs",
  "nodeVersion": "18.x"
}
```

### .env Files

**Local Development** (`.env.local`):
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

**Production** (`.env.production` + Vercel dashboard):
```
NEXT_PUBLIC_API_URL=https://your-backend.vercel.app/api/v1
```

**Example** (`.env.example`):
- Reference for all available variables
- Commit this to git (no secrets)

---

## Environment Variables

### Required for Production

Set these in **Vercel Dashboard → Settings → Environment Variables**:

| Variable | Value | Example |
|----------|-------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `https://todo-backend.vercel.app/api/v1` |
| `NEXT_PUBLIC_APP_ENV` | Environment | `production` |
| `NEXT_PUBLIC_APP_NAME` | App name | `AI Todo App` |

### How to Set Them

1. Open your Vercel project
2. **Settings** → **Environment Variables**
3. Click **"Add New"**
4. Enter name and value
5. Select environments (Production, Preview, Development)
6. Click **"Save"**

---

## Troubleshooting

### Build Fails with "Cannot find module"

**Solution:** Ensure all dependencies are in `package.json`:
```bash
cd frontend
npm install --save missing-package
npm run build  # Test locally
```

### Environment Variables Not Working

**Solution:**
1. Check variable is set in Vercel dashboard
2. Variable must start with `NEXT_PUBLIC_` for browser access
3. Redeploy after adding variables (Settings → Deployments → Redeploy)

### API Calls Returning 404

**Solution:**
```bash
# Verify backend URL
curl https://your-backend.vercel.app/api/v1/health

# Should return valid response. If not:
# 1. Check backend is deployed and running
# 2. Update NEXT_PUBLIC_API_URL in Vercel dashboard
# 3. Redeploy frontend
```

### Images Not Loading

**Solution:** Vercel automatically optimizes images. If still broken:
```typescript
// frontend/next.config.ts
images: {
  remotePatterns: [
    { protocol: "https", hostname: "your-domain.com" },
  ],
}
```

---

## Monitoring & Logs

### View Build Logs

1. Vercel dashboard → **Deployments**
2. Click deployment to view logs
3. Expand sections to see build output

### Runtime Logs

1. **Deployments** → click deployment
2. **Logs** tab
3. Select **Runtime Logs** to see production errors

---

## Custom Domain (Optional)

### Add Custom Domain

1. Vercel dashboard → **Settings** → **Domains**
2. Click **"Add Domain"**
3. Enter your domain (e.g., `todo.example.com`)
4. Update DNS records (Vercel provides instructions)
5. Wait for DNS propagation (usually 5-30 minutes)

### Using apex domain (example.com)

1. Add `example.com`
2. Add `www.example.com` as alias
3. Update DNS:
   ```
   example.com    A       76.76.19.165
   www.example.com CNAME  cname.vercel-dns.com
   ```

---

## Performance Tips

### Optimize Build Time

1. **Reduce dependencies:** Remove unused packages
   ```bash
   npm ls  # List all dependencies
   ```

2. **Enable caching:** Vercel caches automatically

3. **Code splitting:** Next.js does this automatically

### Optimize Production

1. **Image optimization:** Vercel handles automatically
2. **Compression:** Enabled by default
3. **Edge caching:** Vercel CDN (no config needed)

---

## Preview URLs

Every push creates a unique preview URL:

- **Main branch** → `https://your-project.vercel.app`
- **Pull requests** → `https://your-project-pr-123.vercel.app`
- **Feature branches** → `https://your-project-feature.vercel.app`

Share preview URLs for feedback before merging!

---

## Rollback to Previous Deployment

1. **Deployments** → find old deployment
2. Click **"..."** → **"Promote to Production"**
3. Confirms rollback and deploys old version

---

## GitHub Integration

### Auto-Deploy Configuration

Already configured! When you:
- **Push to main/001-todo-cli** → Auto-deploys to production
- **Open pull request** → Creates preview deployment
- **Push to PR** → Updates preview

### Disable Auto-Deploy

1. **Settings** → **Git** → **Deploy on Push**
2. Toggle **Off**
3. Manual deploys via **Deployments → Redeploy**

---

## Database & API

### Backend API

- Hosted separately (e.g., Render, Railway, Vercel)
- Set `NEXT_PUBLIC_API_URL` in environment variables
- Ensure CORS allows Vercel domain

### Database Connection

Frontend doesn't connect directly to database. All queries go through backend API.

---

## Security Best Practices

### Environment Variables

- ✅ Use `NEXT_PUBLIC_` prefix only for public values
- ❌ Never commit `.env.local`
- ❌ Never hardcode API keys
- ✅ Use Vercel dashboard for secrets

### CORS Configuration

Backend must allow Vercel domain:

```python
# Backend (FastAPI example)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-vercel-domain.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Deployment Checklist

- [ ] GitHub repo connected to Vercel
- [ ] Project imported on Vercel dashboard
- [ ] Build succeeds locally (`npm run build`)
- [ ] Environment variables set in Vercel dashboard
- [ ] `NEXT_PUBLIC_API_URL` points to correct backend
- [ ] Backend CORS allows Vercel domain
- [ ] First deployment completed
- [ ] Site loads at `https://your-project.vercel.app`
- [ ] API calls work (check Network tab in DevTools)
- [ ] No 404 or CORS errors

---

## Next Steps

1. **Deploy:** Follow Quick Start above
2. **Test:** Visit your Vercel URL and test features
3. **Monitor:** Check logs if issues occur
4. **Iterate:** Push changes → Auto-deploys
5. **Scale:** Add custom domain, enable analytics, etc.

---

**Status:** ✅ Ready for Vercel deployment

Last updated: 2025-12-11
