# 🚀 Quick Start Guide - 5 Minutes to Live

## Option A: Deploy Now (Recommended)

### Step 1: Login to Services (2 min)

Open two terminal windows:

**Terminal 1 - Railway:**
```bash
cd creator-growth-radar/backend
railway login
```
Follow the browser prompt to authenticate.

**Terminal 2 - Vercel:**
```bash
cd creator-growth-radar/frontend
vercel login
```
Follow the browser prompt to authenticate.

### Step 2: Get RapidAPI Key (1 min)

1. Go to https://rapidapi.com
2. Sign up (free)
3. Search for "TikTok Scraper" or "TikTok Scraper7"
4. Subscribe to the free tier
5. Copy your API key

### Step 3: Deploy Backend (1 min)

```bash
cd creator-growth-radar/backend

# Initialize Railway project
railway init

# Set your RapidAPI key
railway variables set RAPIDAPI_KEY=your_key_here

# Deploy
railway up --detach
```

**Copy your Railway URL** from the output (looks like: `https://xxx-production.up.railway.app`)

### Step 4: Update Frontend (30 sec)

Open `frontend/app.js` and find this line:
```javascript
const BACKEND_URL = 'https://creator-growth-radar-production.up.railway.app';
```

Replace with your Railway URL from Step 3.

### Step 5: Deploy Frontend (1 min)

```bash
cd creator-growth-radar/frontend
vercel deploy --prod --yes
```

**Done!** Visit your Vercel URL and test it!

---

## Option B: Test Locally First

### Step 1: Install Dependencies

```bash
cd creator-growth-radar/backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
```

### Step 2: Run Test Suite

```bash
python test_local.py
```

You should see scores for 4 test creators.

### Step 3: Start Backend Server

```bash
# Set your RapidAPI key
set RAPIDAPI_KEY=your_key_here  # Windows
# export RAPIDAPI_KEY=your_key_here  # Mac/Linux

# Start server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Step 4: Test API

Open browser to: http://localhost:8000/docs

Click on `/analyze` → Try it out → Enter username: `charlidamelio` → Execute

### Step 5: Open Frontend

```bash
cd ../frontend
python -m http.server 3000
```

Visit: http://localhost:3000

---

## ✅ Verification Checklist

- [ ] Backend deployed to Railway
- [ ] Frontend deployed to Vercel
- [ ] RapidAPI key configured
- [ ] Can analyze a TikTok username
- [ ] Scores display correctly (0-100)
- [ ] Color indicators work (green/yellow/red)

---

## 🆘 Troubleshooting

**"Unauthorized" errors:**
- Run `railway login` or `vercel login` again

**"Could not find profile":**
- Username might be wrong (no @ symbol)
- Account might be private
- Check Railway logs for API errors

**Frontend shows network error:**
- Verify `BACKEND_URL` in `app.js` matches your Railway URL
- Railway free tier sleeps after 15min (wake it up by visiting the URL)

---

## 📞 Need Help?

1. Check Railway logs: `railway logs`
2. Check Vercel logs: `vercel logs`
3. Test API directly: `https://your-railway-url.up.railway.app/analyze?username=charlidamelio`

---

**You're almost there! Let's get this live! 🚀**
