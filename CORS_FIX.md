# CORS Configuration Fix

## Your URLs

**Frontend (Vercel):**
- Primary: `https://aesthetic-evaluator.vercel.app`
- Main branch: `https://aesthetic-evaluator-git-main-mohamedsemahs-projects.vercel.app`
- Deployment: `https://aesthetic-evaluator-ge37nkxeb-mohamedsemahs-projects.vercel.app`

**Backend (Railway):**
- `https://aesthetic-evaluator.up.railway.app`

## Step 1: Update Railway ALLOWED_ORIGINS

In Railway Dashboard → Aesthetic-Evaluator service → **Variables** tab:

Add or update `ALLOWED_ORIGINS` with this value:

```
https://aesthetic-evaluator.vercel.app,https://aesthetic-evaluator-git-main-mohamedsemahs-projects.vercel.app,https://aesthetic-evaluator-ge37nkxeb-mohamedsemahs-projects.vercel.app
```

**Steps:**
1. Go to Railway → Your service → Variables tab
2. Find `ALLOWED_ORIGINS` (or click "New Variable" to add it)
3. Paste the value above
4. Click Save
5. Railway will automatically restart (wait ~30 seconds)

## Step 2: Verify Vercel Environment Variable

In Vercel Dashboard → Your project → **Settings** → **Environment Variables**:

**Check if `REACT_APP_API_URL` exists:**
- If it exists: Verify it's set to `https://aesthetic-evaluator.up.railway.app`
- If it doesn't exist: Add it:
  - Key: `REACT_APP_API_URL`
  - Value: `https://aesthetic-evaluator.up.railway.app`
  - Environments: Select Production, Preview, and Development
  - Click Save

**Important:** If you just added/changed it, you MUST redeploy:
1. Go to Deployments tab
2. Click the three dots (⋯) on the latest deployment
3. Click "Redeploy"
4. Wait for deployment to complete

## Step 3: Test

After both are configured:
1. Hard refresh your browser (Ctrl+Shift+R or Cmd+Shift+R)
2. Visit: `https://aesthetic-evaluator.vercel.app`
3. Try uploading a file

## Verification

To verify everything is configured correctly:

**Check Railway Variables:**
- `ALLOWED_ORIGINS` should contain all three Vercel URLs above

**Check Vercel Environment Variables:**
- `REACT_APP_API_URL` should be `https://aesthetic-evaluator.up.railway.app`

**Test Backend:**
- Visit: `https://aesthetic-evaluator.up.railway.app/health`
- Should return: `{"status":"healthy"}`

**Test Frontend:**
- Visit: `https://aesthetic-evaluator.vercel.app`
- Open browser console (F12)
- Check if there are any CORS errors
- Try uploading a file

