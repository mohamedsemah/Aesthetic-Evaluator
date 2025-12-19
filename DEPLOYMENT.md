# Deployment Guide

This application is configured for scalable, production-ready deployment using:
- **Backend**: Railway.app (with PostgreSQL)
- **Frontend**: Vercel
- **Database**: PostgreSQL (Railway managed)

## Quick Start Deployment

### Prerequisites

1. GitHub account
2. Railway.app account (free tier available)
3. Vercel account (free tier available)
4. At least one LLM API key (OpenAI, Anthropic, DeepSeek, or Replicate)

---

## Step 1: Deploy Backend (Railway)

### 1.1 Prepare Your Code

1. Push your code to GitHub
2. Ensure all files are committed:
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

### 1.2 Deploy on Railway

1. Go to [Railway.app](https://railway.app) and sign up/login
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway will auto-detect the `railway.json` configuration

### 1.3 Configure Environment Variables

In Railway dashboard, go to your service → Variables tab, add:

**Required Variables:**

```env
# Security - Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=your-super-secret-key-min-32-chars

# CORS - Will be set after frontend deployment
ALLOWED_ORIGINS=https://your-frontend-app.vercel.app

# At least one LLM API key required
OPENAI_API_KEY=sk-...
# OR
ANTHROPIC_API_KEY=sk-ant-...
# OR  
DEEPSEEK_API_KEY=...
# OR
REPLICATE_API_TOKEN=...

# Application Settings
DEBUG=False
LOG_LEVEL=INFO
AUTH_REQUIRED=False
```

**Database Setup:**

1. Click "New" → "Database" → "Add PostgreSQL"
2. Railway will automatically set `DATABASE_URL` environment variable
3. Your app will use this PostgreSQL database automatically

### 1.4 Deploy

1. Railway will automatically build and deploy
2. Note your deployment URL (e.g., `https://your-app.up.railway.app`)
3. Test: Visit `https://your-app.up.railway.app/health`

---

## Step 2: Deploy Frontend (Vercel)

### 2.1 Prepare Frontend

1. Ensure your code is pushed to GitHub
2. Frontend is already configured with `vercel.json`

### 2.2 Deploy on Vercel

1. Go to [Vercel.com](https://vercel.com) and sign up/login
2. Click "New Project" → "Import Git Repository"
3. Select your repository
4. Configure project:
   - **Framework Preset**: Create React App
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`

### 2.3 Set Environment Variables

In Vercel project settings → Environment Variables, add:

```env
REACT_APP_API_URL=https://your-backend-app.up.railway.app
```

**Important**: Replace with your actual Railway backend URL!

### 2.4 Deploy

1. Click "Deploy"
2. Vercel will build and deploy
3. Note your frontend URL (e.g., `https://your-app.vercel.app`)

### 2.5 Update Backend CORS

Go back to Railway → Variables, update:

```env
ALLOWED_ORIGINS=https://your-app.vercel.app,https://your-app-git-main.vercel.app
```

(Add all Vercel deployment URLs - preview and production)

---

## Step 3: Verify Deployment

### Test Backend
```bash
curl https://your-backend.up.railway.app/health
```

### Test Frontend
1. Visit your Vercel URL
2. Try uploading a file
3. Check browser console for errors

---

## Scaling Configuration

### Backend Scaling (Railway)

Railway automatically scales, but you can configure:

1. **Workers**: Set `WORKERS=2` (or higher) in Railway variables for more concurrent requests
2. **Resources**: Upgrade Railway plan for more CPU/RAM
3. **Database**: PostgreSQL handles connections automatically

### Frontend Scaling (Vercel)

Vercel automatically scales with their edge network. No configuration needed.

### Database Scaling

- Railway PostgreSQL handles up to 1GB on free tier
- Upgrade for more storage/connections
- Consider connection pooling for high traffic

---

## Monitoring & Maintenance

### Health Checks

- Backend: `https://your-backend.up.railway.app/health`
- Detailed: `https://your-backend.up.railway.app/health/detailed`

### Logs

- **Railway**: Dashboard → Deployments → Logs
- **Vercel**: Dashboard → Deployments → Logs

### Error Tracking (Optional)

1. Sign up at [Sentry.io](https://sentry.io)
2. Create a project
3. Get your DSN
4. Add to Railway variables:
   ```env
   SENTRY_DSN=https://...
   SENTRY_ENVIRONMENT=production
   ```

---

## Cost Estimation

### Free Tier (Starting Out)

- **Railway**: $5 free credit/month (covers small apps)
- **Vercel**: Free tier (generous limits)
- **PostgreSQL**: Included in Railway

### Growth Stage

- **Railway**: ~$10-20/month (moderate traffic)
- **Vercel**: Free tier usually sufficient
- **Total**: ~$10-20/month

### Scale Stage

- **Railway**: $50-200/month (high traffic)
- **Vercel Pro**: $20/month (if needed)
- **Total**: ~$70-220/month

---

## Security Checklist

- [x] SECRET_KEY is set and secure
- [x] ALLOWED_ORIGINS matches your frontend domain
- [x] Database credentials are secure (Railway manages this)
- [x] API keys are stored in environment variables (never in code)
- [x] HTTPS is enabled (automatic on Railway/Vercel)
- [ ] Consider enabling AUTH_REQUIRED=True for production
- [ ] Set up Sentry for error tracking
- [ ] Review rate limiting settings

---

## Troubleshooting

### Backend won't start

1. Check Railway logs
2. Verify all required environment variables are set
3. Check DATABASE_URL is correct
4. Ensure Dockerfile builds successfully

### Frontend can't connect to backend

1. Verify `REACT_APP_API_URL` is correct in Vercel
2. Check CORS settings in Railway (ALLOWED_ORIGINS)
3. Check browser console for CORS errors
4. Verify backend is running (check /health endpoint)

### Database connection issues

1. Verify PostgreSQL is provisioned in Railway
2. Check DATABASE_URL is set automatically
3. Restart backend service after adding database

### High costs

1. Monitor Railway usage dashboard
2. Optimize file upload limits
3. Consider implementing stricter rate limits
4. Review LLM API usage (major cost driver)

---

## Continuous Deployment

Both Railway and Vercel support automatic deployments:

- **Railway**: Automatically deploys on git push to main branch
- **Vercel**: Automatically deploys on git push (production + preview)

### Preview Deployments

- Vercel creates preview deployments for pull requests
- Remember to add preview URLs to ALLOWED_ORIGINS if needed

---

## Next Steps

1. ✅ Deploy backend to Railway
2. ✅ Deploy frontend to Vercel
3. ✅ Configure environment variables
4. ✅ Test the deployment
5. ⬜ Set up custom domain (optional)
6. ⬜ Configure Sentry (optional)
7. ⬜ Set up monitoring alerts (optional)
8. ⬜ Review and optimize costs

---

## Support

- Railway Docs: https://docs.railway.app
- Vercel Docs: https://vercel.com/docs
- Project Issues: Check GitHub issues or create new one

