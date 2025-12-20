# Railway Setup Instructions

## Quick Fix for Build Error

If you're seeing the error: `"/requirements.txt": not found`, follow these steps:

### Option 1: Configure in Railway Dashboard (Recommended)

1. Go to your Railway project
2. Click on your service
3. Go to **Settings** → **Service Source**
4. Set:
   - **Root Directory**: `backend`
   - **Dockerfile Path**: `Dockerfile` (or leave blank)
   - **Build Command**: Leave default
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT --workers 2`

5. Save and redeploy

### Option 2: Use Railway's Auto-Detection

1. In Railway dashboard, go to your service settings
2. Change **Source** to use **Nixpacks** (instead of Docker)
3. Set **Root Directory** to `backend`
4. Railway will auto-detect it's a Python app and use requirements.txt

### Option 3: Move Dockerfile to Root (Alternative)

If the above doesn't work, you can move the Dockerfile to the project root and update paths:

1. Move `backend/Dockerfile` to root `Dockerfile`
2. Update Dockerfile to reference `backend/requirements.txt`:
   ```dockerfile
   COPY backend/requirements.txt .
   COPY backend /app
   ```

But **Option 1** above should work and is cleaner.

---

## Current Configuration

Your `railway.json` is configured correctly:
- `dockerfilePath`: `backend/Dockerfile`
- `dockerContext`: `backend`

The issue is Railway needs the **Root Directory** set in the dashboard to match the context.

