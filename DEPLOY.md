# TABOOST Radar - Deployment Guide

## ✅ Local Status (COMPLETE)

- [x] SQLite database implemented (`backend/taboost.db` - 32KB)
- [x] API key authentication enabled
- [x] All 15 endpoints passing tests
- [x] Git initialized and committed
- [x] `.env` file created with API key
- [x] Frontend `config.js` configured

---

## 🔑 API Key (SAVE THIS)

```
TABOOST_API_KEY=tb_sk_live_a8f3b2c1d4e5f6g7h8i9j0k1l2m3n4o5
```

**Important:** This key is in `backend/.env` (gitignored) and `public/config.js`. Update `config.js` for production.

---

## 🚀 Step 1: Push to GitHub

```bash
cd C:\Users\Admin\clawd\taboost-radar

# Create a new repo on GitHub (taboost-radar or your preferred name)
# Then run:
git remote add origin https://github.com/YOUR_USERNAME/taboost-radar.git
git branch -M main
git push -u origin main
```

---

## 🚂 Step 2: Deploy Backend to Railway

1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your `taboost-radar` repo
4. **Important Settings:**
   - **Root Directory:** `backend`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables:**
     - `TABOOST_API_KEY` = `tb_sk_live_a8f3b2c1d4e5f6g7h8i9j0k1l2m3n4o5`
     - `PORT` = (Railway sets this automatically, usually 10000)

5. Deploy and wait for it to go live
6. Copy your Railway URL (format: `https://xxxx.up.railway.app`)

**Test:** `curl https://xxxx.up.railway.app/health` should return `{"status":"ok","service":"taboost-api"}`

---

## 🌐 Step 3: Deploy Frontends to Netlify

### Option A: Netlify CLI (Recommended)

```bash
# Install Netlify CLI if you haven't
npm install -g netlify-cli

# Deploy
cd C:\Users\Admin\clawd\taboost-radar\public
netlify deploy --prod
```

### Option B: Netlify UI

1. Go to https://netlify.com
2. Click "Add new site" → "Deploy manually"
3. Drag and drop the `public/` folder
4. After deploy, go to Site Settings → Build & Deploy → Environment
5. **Note:** The `netlify.toml` has a placeholder `TABOOST_BACKEND_URL`

### Update netlify.toml with Railway URL

After you get your Railway URL, update `public/netlify.toml`:

```toml
[[redirects]]
from = "/api/*"
to = "https://YOUR-RAILWAY-URL.up.railway.app/api/:splat"
status = 200
force = true
```

Also update `public/config.js`:

```js
const BACKEND_URL = 'https://YOUR-RAILWAY-URL.up.railway.app';
```

---

## 🧪 Step 4: Final End-to-End Test

Update `test-connection.js` environment variables:

```bash
set BACKEND_URL=https://YOUR-RAILWAY-URL.up.railway.app
set TABOOST_API_KEY=tb_sk_live_a8f3b2c1d4e5f6g7h8i9j0k1l2m3n4o5
node test-connection.js
```

All 15 tests should pass.

---

## 📁 File Structure

```
taboost-radar/
├── backend/
│   ├── main.py              # FastAPI server with SQLite
│   ├── requirements.txt     # Python deps
│   ├── .env                 # API key (gitignored)
│   ├── .gitignore           # Don't commit .env or .db
│   └── taboost.db           # SQLite database (gitignored)
├── public/
│   ├── config.js            # Frontend config (update BACKEND_URL for prod)
│   ├── api.js               # API layer with mock fallbacks
│   ├── creator-earnings-radar.html   # Creator view
│   ├── taboost-dashboard.html        # Agency dashboard
│   └── netlify.toml         # Netlify config with redirects
├── .gitignore               # Root gitignore
├── test-connection.js       # API test script
├── API_CONTRACT.md          # API documentation
├── README.md                # Project readme
└── DEPLOY.md                # This file
```

---

## 🔒 Security Notes

1. **API Key:** The current key is for development. Generate a new one for production:
   ```python
   import secrets
   print(secrets.token_urlsafe(32))
   ```

2. **CORS:** Currently allows all origins (`*`). For production, update `main.py`:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://your-netlify-site.netlify.app"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

3. **Database:** SQLite is fine for development and small production use. For scale, migrate to PostgreSQL.

---

## 📊 Quick Stats Endpoint

Test the CEO dashboard summary:

```bash
curl -H "X-API-Key: tb_sk_live_a8f3b2c1d4e5f6g7h8i9j0k1l2m3n4o5" \
  https://YOUR-RAILWAY-URL.up.railway.app/api/stats
```

Returns:
```json
{
  "totalCreators": 6,
  "totalEarningsLogged": 4,
  "totalEarningsAmount": 504.85,
  "ytdTotal": 504.85,
  "taxYear": 2026
}
```

---

## ✅ Deployment Checklist

- [ ] Push to GitHub
- [ ] Deploy backend to Railway
- [ ] Set Railway environment variable (TABOOST_API_KEY)
- [ ] Test Railway health endpoint
- [ ] Update `public/config.js` with Railway URL
- [ ] Update `public/netlify.toml` with Railway URL
- [ ] Deploy `public/` to Netlify
- [ ] Run final test with live URLs
- [ ] Share URLs with Colin

---

**Questions?** Check `API_CONTRACT.md` for full API docs or `README.md` for setup instructions.
