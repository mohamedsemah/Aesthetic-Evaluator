# Debugging CORS Issue

## Step 1: Check Browser Console

1. Open your Vercel frontend: `https://aesthetic-evaluator.vercel.app`
2. Press **F12** to open Developer Tools
3. Go to **Console** tab
4. Try to upload a file
5. Look for errors - copy the EXACT error message

## Step 2: Check Network Tab

1. In Developer Tools, go to **Network** tab
2. Try to upload a file
3. Look for the failed request (it will be red)
4. Click on it
5. Check:
   - **Request URL**: What URL is it trying to hit?
   - **Request Method**: Should be POST
   - **Status Code**: What error code? (403, 404, 500, etc.)
   - **Response Headers**: Look for `Access-Control-Allow-Origin`
   - **Request Headers**: Check the `Origin` header

## Step 3: Verify Railway Environment Variables

In Railway Dashboard → Variables tab, check:

1. **ALLOWED_ORIGINS** should be:
   ```
   https://aesthetic-evaluator.vercel.app,https://aesthetic-evaluator-git-main-mohamedsemahs-projects.vercel.app,https://aesthetic-evaluator-ge37nkxeb-mohamedsemahs-projects.vercel.app
   ```

2. **No trailing slashes** in the URLs
3. **All URLs use https://** (not http://)

## Step 4: Verify Vercel Environment Variable

In Vercel Dashboard → Settings → Environment Variables:

1. **REACT_APP_API_URL** should be:
   ```
   https://aesthetic-evaluator.up.railway.app
   ```

2. **No trailing slash** at the end
3. Make sure it's set for **Production**, **Preview**, and **Development** environments

## Step 5: Test Backend Directly

Test if the backend is accessible:

1. Open in browser: `https://aesthetic-evaluator.up.railway.app/health`
   - Should return: `{"status":"healthy"}`

2. Test CORS with curl (run in terminal):
   ```bash
   curl -X OPTIONS https://aesthetic-evaluator.up.railway.app/upload \
     -H "Origin: https://aesthetic-evaluator.vercel.app" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -v
   ```
   
   Look for `Access-Control-Allow-Origin` in the response headers.

## Step 6: Check Railway Logs

In Railway Dashboard → Your service → Logs tab:

1. Look for any errors
2. Look for CORS-related messages
3. Check if the service restarted after you changed ALLOWED_ORIGINS

## Step 7: Hard Refresh Frontend

After making changes:

1. Clear browser cache: **Ctrl+Shift+Delete** (or Cmd+Shift+Delete on Mac)
2. Hard refresh: **Ctrl+Shift+R** (or Cmd+Shift+R)
3. Or open in Incognito/Private window

## Common Issues:

1. **"Failed to fetch"** - Usually means:
   - Backend is down
   - CORS not configured
   - Wrong API URL

2. **CORS error in console** - Means:
   - ALLOWED_ORIGINS doesn't include your frontend URL
   - URL has trailing slash or wrong protocol

3. **404 Not Found** - Means:
   - REACT_APP_API_URL is wrong
   - Backend endpoint doesn't exist

4. **Network timeout** - Means:
   - Backend is not responding
   - Check Railway logs

## What to Report Back:

Please provide:
1. The EXACT error message from browser console
2. The Request URL from Network tab
3. The Status Code from Network tab
4. Whether `/health` endpoint works in browser
5. Whether you've verified ALLOWED_ORIGINS in Railway
6. Whether you've verified REACT_APP_API_URL in Vercel

