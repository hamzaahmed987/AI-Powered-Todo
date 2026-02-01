# Vercel Deployment Guide for Mobile App Backend

This guide will help you deploy your FastAPI backend to Vercel and connect it to your React Native mobile app.

## Prerequisites

1. A Vercel account (sign up at https://vercel.com)
2. Vercel CLI installed: `npm install -g vercel`
3. Your backend code ready to deploy
4. Database (Neon PostgreSQL) set up

## Step 1: Prepare Your Backend

Your backend is already configured for Vercel with:
- ✅ `vercel.json` - Vercel configuration file
- ✅ `api/index.py` - Serverless function entry point
- ✅ CORS configured for mobile apps

## Step 2: Set Up Environment Variables on Vercel

You need to add these environment variables in your Vercel project settings:

### Required Variables:

1. **DATABASE_URL**
   - Your Neon PostgreSQL connection string
   - Example: `postgresql://user:password@ep-xxx.aws.neon.tech/dbname?sslmode=require`
   - Get from: https://console.neon.tech

2. **OPENROUTER_API_KEY**
   - Your OpenRouter API key for AI features
   - Get from: https://openrouter.ai/keys

3. **JWT_SECRET_KEY**
   - A secure random string for JWT token signing
   - Generate with: `openssl rand -hex 32`

### Optional Variables (with defaults):

- `OPENROUTER_MODEL` - Default: `qwen/qwen-2.5-72b-instruct`
- `JWT_ALGORITHM` - Default: `HS256`
- `JWT_EXPIRATION_HOURS` - Default: `24`
- `ALLOWED_ORIGINS` - Default: `*` (allows all origins for mobile apps)
- `ENVIRONMENT` - Set to: `production`
- `LOG_LEVEL` - Default: `INFO`

## Step 3: Deploy to Vercel

### Option A: Deploy via Vercel CLI

1. Navigate to your backend directory:
   ```bash
   cd /home/noman-khan/Desktop/mobile/backend
   ```

2. Login to Vercel:
   ```bash
   vercel login
   ```

3. Deploy:
   ```bash
   vercel
   ```

4. Follow the prompts:
   - Set up and deploy? **Yes**
   - Which scope? **Your account**
   - Link to existing project? **No**
   - What's your project's name? **your-app-name**
   - In which directory is your code located? **.**
   - Want to override settings? **No**

5. Add environment variables:
   ```bash
   vercel env add DATABASE_URL
   vercel env add OPENROUTER_API_KEY
   vercel env add JWT_SECRET_KEY
   ```

6. Deploy to production:
   ```bash
   vercel --prod
   ```

### Option B: Deploy via Vercel Dashboard

1. Go to https://vercel.com/new
2. Import your Git repository
3. Configure project:
   - **Framework Preset**: Other
   - **Root Directory**: `backend`
4. Add environment variables in Settings → Environment Variables
5. Click **Deploy**

## Step 4: Get Your Vercel URL

After deployment, Vercel will give you a URL like:
```
https://your-app-name.vercel.app
```

## Step 5: Update Your Mobile App

Update the mobile app configuration to use your Vercel URL:

**File:** `/home/noman-khan/Desktop/mobile/myapp/src/api/config.ts`

```typescript
const VERCEL_API_URL = 'https://your-app-name.vercel.app';
```

Replace `your-app-name` with your actual Vercel project name.

## Step 6: Test Your Deployment

### Test the API:

1. Visit your Vercel URL in a browser:
   ```
   https://your-app-name.vercel.app
   ```

2. Check the health endpoint:
   ```
   https://your-app-name.vercel.app/health
   ```

3. View API documentation:
   ```
   https://your-app-name.vercel.app/docs
   ```

### Test from Mobile App:

1. Build your app in production mode:
   ```bash
   cd /home/noman-khan/Desktop/mobile/myapp
   npm run android --mode=release
   # or
   npm run ios --mode=release
   ```

2. Try logging in or making API requests

## Troubleshooting

### CORS Errors
- **Issue**: Mobile app can't connect due to CORS
- **Solution**: Verify `ALLOWED_ORIGINS=*` is set in Vercel environment variables

### Database Connection Errors
- **Issue**: "Database connection failed"
- **Solution**:
  - Check DATABASE_URL is correctly set in Vercel
  - Ensure Neon database is active and accessible
  - Verify the connection string includes `?sslmode=require`

### AI Features Not Working
- **Issue**: Chat/AI features fail
- **Solution**:
  - Verify OPENROUTER_API_KEY is set correctly
  - Check OpenRouter account has credits
  - Review Vercel function logs for errors

### Deployment Fails
- **Issue**: Build or deployment errors
- **Solution**:
  - Check Vercel build logs
  - Ensure `requirements.txt` includes all dependencies
  - Verify Python version compatibility (3.12+)

## View Logs

Check your Vercel deployment logs:
```bash
vercel logs <deployment-url>
```

Or view them in the Vercel dashboard under your project → Deployments → [Select deployment] → Runtime Logs

## Update Deployment

To update your backend after making changes:

```bash
cd /home/noman-khan/Desktop/mobile/backend
vercel --prod
```

## CORS Configuration

Your backend is configured to allow mobile app requests:
- **ALLOWED_ORIGINS**: Set to `*` by default
- **Mobile apps**: Don't send Origin headers, so `*` is required
- **Security**: Consider implementing API key authentication for additional security

## Environment-Specific Configuration

Your app automatically switches between environments:
- **Development (__DEV__=true)**: Uses `http://10.0.2.2:8000` (Android emulator)
- **Production (__DEV__=false)**: Uses your Vercel URL

## Next Steps

1. ✅ Deploy backend to Vercel
2. ✅ Update mobile app config with Vercel URL
3. ✅ Test all API endpoints from mobile app
4. ✅ Monitor Vercel logs for any issues
5. Consider setting up:
   - Custom domain
   - API rate limiting
   - Error monitoring (Sentry)
   - Analytics

## Support

- Vercel Documentation: https://vercel.com/docs
- FastAPI Documentation: https://fastapi.tiangolo.com
- Neon Documentation: https://neon.tech/docs

## Summary Checklist

- [ ] Vercel account created
- [ ] Environment variables configured in Vercel
- [ ] Backend deployed to Vercel
- [ ] Vercel URL obtained
- [ ] Mobile app config updated with Vercel URL
- [ ] Health endpoint tested
- [ ] Mobile app tested in production mode
- [ ] All features working (auth, tasks, AI chat)
