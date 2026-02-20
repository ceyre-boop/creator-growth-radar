# 🚀 Deployment Guide

## Quick Deploy (5 minutes)

### Step 1: Deploy Backend to Railway

1. **Go to Railway**: https://railway.app
2. **Sign up/Login** (GitHub login is easiest)
3. **New Project** → **Deploy from GitHub repo**
4. **Select your repo**: `creator-growth-radar`
5. **Configure**:
   - Root Directory: `backend`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. **Add Environment Variable**:
   - Click your project → Variables
   - Add: `RAPIDAPI_KEY` = your RapidAPI key
7. **Deploy!** Railway will auto-detect Python and deploy

**Get your backend URL:**
- After deployment, click **Settings** → **Domains**
- Copy the URL (e.g., `https://creator-growth-radar-production.up.railway.app`)

### Step 2: Deploy Frontend to Vercel

1. **Go to Vercel**: https://vercel.com
2. **Sign up/Login** (GitHub login is easiest)
3. **Add New** → **Project**
4. **Import your repo**: `creator-growth-radar`
5. **Configure**:
   - Framework Preset: `Other`
   - Root Directory: `frontend`
   - Build Command: (leave empty)
   - Output Directory: (leave empty)
6. **Before deploying**, update `frontend/app.js`:
   ```javascript
   const BACKEND_URL = 'YOUR_RAILWAY_URL_HERE';
   ```
   Or set as environment variable in Vercel dashboard
7. **Deploy!**

**Get your frontend URL:**
- After deployment, Vercel gives you a URL (e.g., `https://creator-growth-radar.vercel.app`)

### Step 3: Get a RapidAPI Key (if you don't have one)

1. **Go to RapidAPI**: https://rapidapi.com
2. **Sign up** (free)
3. **Search for**: "TikTok Scraper" or "TikTok Scraper7"
4. **Subscribe to free tier** (~100 requests/month)
5. **Copy your API key** from the dashboard
6. **Add to Railway** as `RAPIDAPI_KEY` environment variable

## Alternative: Use Netlify for Frontend

If you prefer Netlify over Vercel:

1. **Go to Netlify**: https://netlify.com
2. **Drag and drop** the `frontend` folder
3. **Or connect GitHub** repo with root directory `frontend`
4. **Set environment variable**: `BACKEND_URL` = your Railway URL

## Testing Your Deployment

1. **Visit your frontend URL**
2. **Enter a TikTok username** (e.g., `charlidamelio`, `khaby.lame`)
3. **Click ANALYZE**
4. **Check the results!**

## Troubleshooting

### Backend returns 404 or error
- Check Railway logs for errors
- Verify `RAPIDAPI_KEY` is set correctly
- Test API directly: `https://your-railway-url.up.railway.app/analyze?username=charlidamelio`

### Frontend shows network error
- Check browser console for CORS errors
- Verify `BACKEND_URL` in `app.js` is correct
- Make sure Railway backend is running (free tier sleeps after 15min)

### "Could not find TikTok profile"
- Username might be incorrect (no @ symbol)
- Account might be private
- RapidAPI quota might be exhausted

## Costs

| Service | Cost | Notes |
|---------|------|-------|
| Railway | $0 | Free tier, sleeps after 15min inactivity |
| Vercel | $0 | Free tier, always on |
| RapidAPI | $0 | Free tier, ~100 requests/month |
| **Total** | **$0** | Perfect for MVP! |

## Upgrading Later

- **Railway**: $5/month for always-on backend
- **RapidAPI**: $10-30/month for more requests
- **Domain**: $10/year for custom domain

---

**Need help?** Check the main README.md or open an issue on GitHub.
