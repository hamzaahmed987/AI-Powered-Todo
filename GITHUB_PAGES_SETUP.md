# GitHub Pages Deployment Setup

This guide configures your Next.js frontend for automatic deployment to GitHub Pages.

---

## Files Created

✅ `.github/workflows/deploy-frontend.yml` - GitHub Actions workflow for auto-deployment

---

## Quick Setup (5 minutes)

### Step 1: Enable GitHub Pages

1. Go to **GitHub repo** → **Settings** → **Pages**
2. Under "Build and deployment":
   - **Source:** Select "GitHub Actions"
   - Click **Save**

### Step 2: Configure Next.js for Static Export

Update `frontend/next.config.ts`:

```typescript
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export", // Enable static export
  assetPrefix: process.env.ASSET_PREFIX || "", // For subdirectory deployments
  images: {
    unoptimized: true, // Required for static export
  },
};

export default nextConfig;
```

### Step 3: Update Build Script in package.json

Ensure your `frontend/package.json` has:

```json
{
  "scripts": {
    "build": "next build",
    "start": "next start",
    "dev": "next dev"
  }
}
```

### Step 4: Set Production API URL

Create `frontend/.env.production`:

```
NEXT_PUBLIC_API_URL=https://your-vercel-backend.vercel.app/api/v1
```

Or GitHub Actions will use the secret (already configured).

### Step 5: Push to GitHub

```bash
git add .
git commit -m "Configure GitHub Pages deployment"
git push origin main
```

**Wait for the workflow to complete!** Check under GitHub → Actions

---

## Deployment Workflow

When you push to `main`:

```
Push to main
    ↓
GitHub Actions Trigger
    ├─ Node.js setup
    ├─ npm install
    ├─ npm run build
    ├─ Static export
    └─ Deploy to GitHub Pages
    ↓
Live at: https://yourusername.github.io/Todo-App
```

---

## Configuration Details

### Option A: Root Repository Deploy (Simple)

If deploying to `https://yourusername.github.io`:

```typescript
// frontend/next.config.ts
const nextConfig: NextConfig = {
  output: "export",
  images: { unoptimized: true },
};
```

### Option B: Repository Subdirectory (Recommended)

If deploying to `https://yourusername.github.io/Todo-App`:

1. Update `next.config.ts`:

```typescript
const nextConfig: NextConfig = {
  output: "export",
  basePath: "/Todo-App",      // Repository name
  assetPrefix: "/Todo-App/",  // Repository name
  images: { unoptimized: true },
};
```

2. Update `.github/workflows/deploy-frontend.yml`:

```yaml
- name: Build frontend
  working-directory: frontend
  env:
    ASSET_PREFIX: /Todo-App  # Add this
```

3. Update API URL in `frontend/.env.production`:

```
NEXT_PUBLIC_API_URL=https://your-vercel-backend.vercel.app/api/v1
```

---

## Environment Variables

### GitHub Secrets (Optional)

If you want to use GitHub Secrets instead of `.env.production`:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add:
   ```
   NEXT_PUBLIC_API_URL=https://your-vercel-backend.vercel.app/api/v1
   ```

3. Update workflow to use it:

```yaml
- name: Build frontend
  env:
    NEXT_PUBLIC_API_URL: ${{ secrets.NEXT_PUBLIC_API_URL }}
```

---

## Troubleshooting

### Issue: "Cannot find module" errors

**Solution:** Ensure all dependencies are in `package.json` and reinstall:

```bash
cd frontend
npm install
npm run build
```

### Issue: Assets loading from wrong path

**Solution:** Check `basePath` and `assetPrefix` match your deployment URL:

```typescript
// For https://yourusername.github.io/Todo-App
basePath: "/Todo-App",
assetPrefix: "/Todo-App/",
```

### Issue: API calls 404 error

**Solution:** Verify `NEXT_PUBLIC_API_URL` points to Vercel backend:

```bash
# Should return valid response
curl https://your-vercel-backend.vercel.app/api/v1/health
```

### Issue: Styles not loading

**Solution:** Ensure CSS imports are correct and bundle is built. Check:

```bash
cd frontend
npm run build  # Should complete without errors
```

### Issue: GitHub Actions workflow fails

**Solution:** Check workflow logs:

1. Go to **Actions** → **Deploy Frontend to GitHub Pages**
2. Click the failed run
3. Expand logs and look for error messages
4. Common issues:
   - `npm install` failed → check package.json syntax
   - `npm run build` failed → run locally to test
   - Deployment failed → check GitHub Pages settings

---

## Manual Deploy (if Actions fails)

You can manually deploy using Vercel instead:

### Using Vercel (Simpler Alternative)

1. Install Vercel CLI:
   ```bash
   npm i -g vercel
   ```

2. In `frontend/` directory:
   ```bash
   vercel --prod
   ```

3. Follow prompts and your site deploys immediately

---

## Performance Tips

### Optimize Build Time

1. **Use next/image for images:**
   ```jsx
   import Image from "next/image";
   <Image src="/pic.jpg" alt="" width={100} height={100} />
   ```

2. **Code splitting (Next.js does automatically)** - No config needed

3. **Static generation:**
   ```typescript
   // pages/dashboard/page.tsx
   export const revalidate = 3600; // Revalidate every hour
   ```

### Optimize Bundle Size

```bash
# Analyze bundle
npm install --save-dev @next/bundle-analyzer
```

Update `next.config.ts`:

```typescript
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
})

export default withBundleAnalyzer(nextConfig)
```

Run:
```bash
ANALYZE=true npm run build
```

---

## Custom Domain (Optional)

### Using GitHub Pages Custom Domain

1. Buy domain (GoDaddy, Namecheap, etc.)
2. GitHub Settings → Pages → Custom domain
3. Enter your domain: `example.com`
4. Update DNS records (GitHub provides instructions)
5. Enable HTTPS (auto-provisioned with Let's Encrypt)

### Using Vercel Instead (Simpler)

If GitHub Pages is too complex, deploy frontend on Vercel too:

```bash
cd frontend
vercel --prod
```

---

## Verification Checklist

- [ ] GitHub Pages enabled in repository settings
- [ ] `next.config.ts` configured with `output: "export"`
- [ ] `.github/workflows/deploy-frontend.yml` exists
- [ ] `frontend/package.json` has correct build script
- [ ] `.env.production` has correct API URL
- [ ] Can run `npm run build` locally without errors
- [ ] Pushed changes to main branch
- [ ] GitHub Actions workflow completed successfully
- [ ] Website loads at `https://yourusername.github.io/Todo-App`
- [ ] API calls go to Vercel backend (check Network tab)

---

## Next Steps

1. **Enable GitHub Pages** (Settings → Pages)
2. **Push code** to trigger auto-deployment
3. **Monitor Actions tab** for workflow status
4. **Visit your deployment** and test it
5. **Set production API URL** once Vercel backend is live

---

**Status:** ✅ GitHub Pages deployment ready

Last updated: 2025-12-11
