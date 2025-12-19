# Quick Deployment Checklist

## 🚀 Fast Track Deployment

### Backend (Railway) - 5 minutes

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy on Railway**
   - Visit https://railway.app
   - New Project → Deploy from GitHub
   - Select your repo
   - Railway auto-detects configuration

3. **Add PostgreSQL Database**
   - Railway dashboard → New → Database → PostgreSQL
   - `DATABASE_URL` is set automatically

4. **Set Environment Variables** (Railway → Variables)
   ```env
   SECRET_KEY=<generate-with-python-secrets>
   ALLOWED_ORIGINS=https://your-frontend.vercel.app
   OPENAI_API_KEY=sk-...  # or other LLM key
   ```

5. **Deploy** - Railway does this automatically!

### Frontend (Vercel) - 3 minutes

1. **Deploy on Vercel**
   - Visit https://vercel.com
   - New Project → Import Git Repository
   - Select your repo
   - Root Directory: `frontend`

2. **Set Environment Variable**
   ```env
   REACT_APP_API_URL=https://your-backend.up.railway.app
   ```

3. **Update Backend CORS**
   - Railway → Variables → ALLOWED_ORIGINS
   - Add your Vercel URL

4. **Done!** 🎉

---

## 📋 Required Secrets

Generate SECRET_KEY:
```python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## ✅ Verification

- Backend: `https://your-backend.up.railway.app/health`
- Frontend: Visit your Vercel URL
- Test upload and analysis

---

## 📖 Full Guide

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions.

