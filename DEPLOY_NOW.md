# 🚀 Deploy Creator Growth Radar - Complete Guide

All code fixes are complete and pushed to GitHub. Follow these exact steps to deploy.

---

## ✅ STEP 1: Deploy Backend to Railway

### Option A: Using Railway CLI (Recommended)

```bash
# Navigate to project
cd creator-growth-radar

# Login to Railway (opens browser)
railway login

# Link or create project
railway init

# Add backend as the root directory for this service
# In Railway dashboard: Settings → Root Directory → Set to "backend"

# Deploy
railway up

# Set environment variable for demo mode (optional - makes demos reliable without API keys)
railway variables set DEMO_MODE=true

# OR set your RapidAPI key for real scraping
railway variables set RAPIDAPI_KEY=your_key_here

# Get your backend URL
railway domain
```

### Option B: Railway Dashboard (Manual)

1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub repo"
3. Select `ceyre-boop/creator-growth-radar`
4. **CRITICAL**: In project Settings:
   - **Root Directory**: `backend`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Click "Deploy"
6. Go to Variables tab and add:
   - `DEMO_MODE=true` (for reliable demos without API keys)
   - OR `RAPIDAPI_KEY=your_key_here` (for real TikTok scraping)
7. Click "Generate Domain" to get your URL

### Your Backend URL Will Be:
```
https://creator-growth-radar-xxxx.up.railway.app
```

### Test Backend:
```
https://YOUR-RAILWAY-URL.up.railway.app/analyze?username=charli_damelio
```

---

## ✅ STEP 2: Deploy Frontend to Vercel

### Option A: Using Vercel CLI

```bash
# Navigate to frontend
cd creator-growth-radar/frontend

# Login to Vercel
vercel login

# Deploy with backend URL
vercel --prod --env BACKEND_URL=https://YOUR-RAILWAY-URL.up.railway.app

# Or update app.js manually with the backend URL before deploying
```

### Option B: Vercel Dashboard (Manual)

1. Go to https://vercel.com
2. Click "Add New" → "Project"
3. Import `ceyre-boop/creator-growth-radar`
4. **Configure Build**:
   - **Framework Preset**: Other
   - **Root Directory**: `frontend`
   - **Build Command**: (leave empty)
   - **Output Directory**: (leave empty)
5. **Add Environment Variable**:
   - Name: `BACKEND_URL`
   - Value: `https://YOUR-RAILWAY-URL.up.railway.app`
6. Click "Deploy"

### Alternative: Update app.js Before Deploy

Edit `frontend/app.js` line 10:
```javascript
let BACKEND_URL = 'https://YOUR-RAILWAY-URL.up.railway.app';
```

Then deploy the frontend folder to Vercel.

### Your Frontend URL Will Be:
```
https://creator-growth-radar-xxxx.vercel.app
```

---

## ✅ STEP 3: Test the Full Flow

1. Open your Vercel frontend URL on your phone
2. Enter a TikTok username (e.g., `charli_damelio`, `khaby.lame`)
3. Click ANALYZE
4. Verify you see:
   - Follower count
   - Avg views (last 10 posts)
   - Engagement rate
   - Posting frequency
   - Three animated score cards (Growth Velocity, Viral Probability, Brand Deal Readiness)

---

## 🎯 Quality Checklist

- [ ] Backend responds at `/analyze?username=charli_damelio`
- [ ] Frontend loads on mobile
- [ ] Input box is full-width
- [ ] Analyze button works
- [ ] Loading radar animation shows
- [ ] Results display with animated score cards
- [ ] Scores are 0-100 with green/yellow/red colors
- [ ] Error handling shows clean messages (no blank screens)
- [ ] Demo mode badge shows when DEMO_MODE=true

---

## 🔧 Troubleshooting

### Railway Build Fails
- Ensure Root Directory is set to `backend` (not root)
- Check Build Logs for Python version issues
- Verify `requirements.txt` exists in `/backend`

### Frontend Can't Connect to Backend
- Update `BACKEND_URL` in `frontend/app.js`
- Check CORS is enabled (already configured in backend)
- Verify Railway service is running (not crashed)

### TikTok Scraping Returns No Data
- Enable `DEMO_MODE=true` for reliable demo data
- Or add your `RAPIDAPI_KEY` for real scraping

---

## 📊 Demo Mode

With `DEMO_MODE=true`, the backend returns realistic, deterministic fake data:
- Same username always returns same scores (consistent demos)
- No API dependencies
- Perfect for CEO presentations
- Shows "⚡ Demo Mode" badge on results

---

## 🎬 CEO Pitch Ready

Once deployed, the product is ready for:
- Opening on mobile phone
- Typing any creator name
- Getting instant, authoritative-looking scores
- Zero explanation needed - value is immediately obvious

**Tagline**: "Know who's about to blow up. Before everyone else does."
