# PostgreSQL Setup on Railway

## Overview

Your application is already configured to work with PostgreSQL! The code automatically detects whether you're using SQLite or PostgreSQL based on the `DATABASE_URL` environment variable.

## Benefits of PostgreSQL

- **Better Performance**: Faster queries, better concurrency
- **Data Persistence**: Data survives container restarts
- **Production Ready**: Industry standard for production applications
- **Better Scalability**: Handles multiple concurrent connections better

## Step-by-Step Setup

### Step 1: Add PostgreSQL Database in Railway

1. **Go to Railway Dashboard**
   - Open https://railway.app
   - Select your project (the one containing "Aesthetic-Evaluator")

2. **Add Database Service**
   - Click the **"+ New"** button (or **"+ Add Service"**)
   - Select **"Database"** from the dropdown
   - Choose **"Add PostgreSQL"**

3. **Wait for Provisioning**
   - Railway will automatically provision a PostgreSQL database
   - This takes ~30-60 seconds
   - You'll see a new service appear in your project

### Step 2: Link Database to Your Backend

Railway automatically sets the `DATABASE_URL` environment variable for you, but you need to connect it:

1. **Open Your Backend Service**
   - Click on "Aesthetic-Evaluator" service (your backend)

2. **Go to Variables Tab**
   - Click the **"Variables"** tab

3. **Verify DATABASE_URL is Set**
   - Railway should automatically add `DATABASE_URL` with the PostgreSQL connection string
   - It will look like: `postgresql://postgres:password@hostname:port/railway`
   - **If it's not there**: Click "Reference Variable" and select `${{Postgres.DATABASE_URL}}` (where "Postgres" is your database service name)

4. **If DATABASE_URL Already Exists (SQLite)**
   - Delete the old `DATABASE_URL` variable (the SQLite one)
   - Railway will automatically provide the PostgreSQL one via service references

### Step 3: Restart Backend Service

1. **Railway will automatically restart** when you change environment variables
2. **Or manually restart**: 
   - Go to "Aesthetic-Evaluator" service
   - Click the three dots (⋯) menu
   - Select "Restart"

### Step 4: Verify Database Tables Are Created

1. **Check Logs**
   - Go to "Aesthetic-Evaluator" service → **"Logs"** tab
   - Look for: `"Database initialized"` in the startup logs
   - No errors should appear

2. **Test the Application**
   - Visit: `https://aesthetic-evaluator.up.railway.app/health`
   - Should return: `{"status":"healthy"}`
   - Try uploading a file to ensure database operations work

## Database Connection Details

Railway automatically manages:
- ✅ Database URL (connection string)
- ✅ Database credentials (username, password)
- ✅ Database host and port
- ✅ Database name

**You don't need to manually configure anything!** Railway handles all the connection details.

## What Happens During Migration

When your backend starts with the PostgreSQL `DATABASE_URL`:

1. **SQLAlchemy detects** it's PostgreSQL (not SQLite)
2. **Tables are automatically created** via `Base.metadata.create_all()`
3. **All existing code works** - no code changes needed!

## Troubleshooting

### Database Connection Errors

If you see errors in the logs:

1. **Check DATABASE_URL exists**
   - Railway Dashboard → Backend Service → Variables
   - Ensure `DATABASE_URL` is present
   - Should start with `postgresql://` (not `sqlite://`)

2. **Verify Database Service is Running**
   - Check that PostgreSQL service shows "Running" status
   - If not, click on it and check logs

3. **Check Database Reference**
   - If using service references, ensure the reference syntax is correct
   - Format: `${{ServiceName.DATABASE_URL}}`

### Tables Not Created

- Check backend logs for "Database initialized" message
- Look for any SQL errors
- Try restarting the backend service

### Migration from SQLite

**Important:** Your SQLite data won't automatically migrate to PostgreSQL. If you have important data:

1. Export data from SQLite (if needed)
2. Add PostgreSQL (new data will go to PostgreSQL)
3. Old SQLite data will remain in the SQLite file but won't be used

For a fresh deployment (like yours), this is fine - PostgreSQL will start fresh.

## Cost Impact

PostgreSQL on Railway:
- **Included in free tier** for small databases
- Typically uses ~$0.50-$2/month depending on usage
- Check Railway dashboard for actual usage

## Next Steps After Setup

1. ✅ Verify health endpoint works
2. ✅ Test file upload (creates a database session)
3. ✅ Test analysis (updates database session)
4. ✅ Check Railway logs for any database errors

---

## Quick Reference

**Railway Dashboard:** https://railway.app

**Your Services:**
- Backend: Aesthetic-Evaluator
- Database: PostgreSQL (new service)

**Database URL Format:**
```
postgresql://postgres:password@hostname:port/railway
```

**Verify Setup:**
- Backend logs show: "Database initialized"
- Health endpoint works: `/health`
- File upload works (creates session in database)

