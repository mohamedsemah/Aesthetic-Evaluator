# Production Deployment Checklist

## ✅ Completed Steps

- [x] Backend deployed to Railway
- [x] Frontend deployed to Vercel
- [x] CORS configured (with Vercel regex pattern)
- [x] Environment variables set
- [x] File upload tested and working

## 🔧 Critical Next Steps

### 1. Set Up PostgreSQL Database (Recommended)

Currently using SQLite. For production, PostgreSQL is recommended for:
- Better performance
- Concurrent access
- Data persistence
- Railway provides managed PostgreSQL

**Steps:**
1. In Railway Dashboard → Your Project
2. Click "+ New" → Select "Database" → Choose "PostgreSQL"
3. Railway will automatically set `DATABASE_URL` environment variable
4. Restart your backend service
5. Database tables will be created automatically on first run

**Note:** Your app will work fine with SQLite for now, but PostgreSQL is better for production.

### 2. Generate Secure SECRET_KEY

Your `SECRET_KEY` should be a random secure string (minimum 32 characters).

**Generate one:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Set in Railway:**
1. Railway Dashboard → Your Service → Variables
2. Add/Update `SECRET_KEY` with the generated value
3. Service will restart automatically

### 3. Verify All Environment Variables

In Railway → Variables tab, ensure these are set:

**Required:**
- [ ] `SECRET_KEY` - Secure random key (32+ chars)
- [ ] `ALLOWED_ORIGINS` - At least your production Vercel URL
- [ ] At least ONE LLM API key (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc.)

**Optional but Recommended:**
- [ ] `DATABASE_URL` - Auto-set if you add PostgreSQL
- [ ] `SENTRY_DSN` - For error tracking
- [ ] `LOG_LEVEL` - Set to `INFO` or `WARNING` for production

## 🧪 Testing Checklist

Test all features end-to-end:

- [x] File upload
- [ ] File analysis (after upload, click "Analyze")
- [ ] Analysis results display
- [ ] Remediation suggestions (if applicable)
- [ ] Session persistence (refresh page, check if session persists)
- [ ] Multiple file upload
- [ ] Large file handling (test with ~10MB file)

## 📊 Optional Enhancements

### Error Tracking (Sentry)

1. Sign up at https://sentry.io (free tier available)
2. Create a new project (FastAPI/Python)
3. Copy the DSN
4. Add to Railway → Variables: `SENTRY_DSN=your_dsn_here`
5. Add `SENTRY_ENVIRONMENT=production`
6. Service will restart and start tracking errors

### Custom Domain (Optional)

**Vercel:**
1. Vercel Dashboard → Your Project → Settings → Domains
2. Add your custom domain
3. Follow DNS configuration instructions
4. Update Railway `ALLOWED_ORIGINS` to include your custom domain

**Railway:**
1. Railway Dashboard → Your Service → Settings → Networking
2. Click "+ Custom Domain"
3. Add your custom domain
4. Update Vercel `REACT_APP_API_URL` to use your custom domain

### Monitoring

**Railway:**
- Built-in metrics dashboard
- Logs view for debugging
- Monitor CPU, Memory, Network usage

**Vercel:**
- Built-in analytics
- Speed Insights (optional)
- Web Analytics (optional)

## 🔒 Security Recommendations

- [ ] Set `SECRET_KEY` to a secure random value (see step 2 above)
- [ ] Consider enabling `AUTH_REQUIRED=True` if you want API authentication
- [ ] Review rate limiting settings (currently 60 req/min, 1000 req/hour)
- [ ] Monitor Railway usage for unexpected costs
- [ ] Set up Sentry for error tracking
- [ ] Review file upload limits (currently 50MB per file, 500MB total)

## 💰 Cost Monitoring

**Railway Free Tier:**
- $5 credit/month
- Typically enough for low-medium traffic
- Monitor usage in Railway dashboard

**When to Upgrade:**
- High traffic (>1000 requests/day)
- Large file processing
- Multiple concurrent users

**Cost Optimization:**
- Monitor LLM API usage (major cost driver)
- Implement caching to reduce duplicate API calls
- Review and optimize file size limits

## 📝 Documentation

Update your README with:
- [ ] Production URL
- [ ] How to deploy updates
- [ ] Environment variable requirements
- [ ] Known limitations
- [ ] Support/contact information

## 🚀 Deployment Updates

Both platforms auto-deploy on git push:

**Railway:** 
- Auto-deploys on push to `main` branch
- Check Railway dashboard for deployment status

**Vercel:**
- Auto-deploys on push (creates preview + production)
- Production uses `main` branch
- Check Vercel dashboard for deployment status

## 🆘 Support & Troubleshooting

If issues arise:

1. **Check Railway Logs:**
   - Railway Dashboard → Your Service → Logs
   - Look for errors, stack traces

2. **Check Vercel Logs:**
   - Vercel Dashboard → Your Project → Deployments → Click deployment → Runtime Logs

3. **Test Backend Directly:**
   - Visit: `https://aesthetic-evaluator.up.railway.app/health`
   - Should return: `{"status":"healthy"}`

4. **Check Browser Console:**
   - F12 → Console tab
   - Look for errors, CORS issues

5. **Verify Environment Variables:**
   - Railway → Variables tab
   - Vercel → Settings → Environment Variables

---

## Quick Reference

**Your URLs:**
- Frontend: `https://aesthetic-evaluator.vercel.app`
- Backend: `https://aesthetic-evaluator.up.railway.app`
- Backend Health: `https://aesthetic-evaluator.up.railway.app/health`
- API Docs: `https://aesthetic-evaluator.up.railway.app/docs`

**Environment Variables:**
- Railway: Project → Service → Variables
- Vercel: Project → Settings → Environment Variables

