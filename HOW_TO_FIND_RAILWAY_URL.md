# How to Find Your Railway Public URL

The `.railway.internal` domain is only accessible within Railway's network. You need the **public URL**.

## Method 1: Railway Dashboard (Easiest)

1. Go to your Railway project dashboard
2. Click on your **"Aesthetic-Evaluator"** service
3. Look for one of these tabs/sections:
   - **"Settings"** → Scroll down to **"Networking"** or **"Domains"**
   - **"Variables"** tab → Look for **"RAILWAY_PUBLIC_DOMAIN"** (if set)
   - The URL might be shown in the service header/card

4. You should see a public URL like:
   - `https://aesthetic-evaluator-production-xxxx.up.railway.app`
   - Or `https://your-service-name.up.railway.app`

## Method 2: Generate Public Domain

If you don't see a public URL:

1. In Railway dashboard → Your service → **Settings**
2. Scroll to **"Networking"** or **"Generate Domain"**
3. Click **"Generate Domain"** or **"Public Domain"**
4. Railway will generate a URL like: `https://your-service-name.up.railway.app`

## Method 3: Check Service Settings

1. Service → **Settings** → Look for **"Domains"** section
2. Click **"Generate Domain"** if no domain exists
3. Copy the generated URL

## The URL Format

Railway public URLs typically look like:
- `https://aesthetic-evaluator-production-xxxx.up.railway.app`
- `https://wholesome-miracle-production-xxxx.up.railway.app`
- `https://your-project-name.up.railway.app`

The `.railway.internal` URL is **internal only** and won't work from your browser.

## Test Your Public URL

Once you have the public URL, test:
- Health: `https://your-public-url/health`
- API Docs: `https://your-public-url/docs`

