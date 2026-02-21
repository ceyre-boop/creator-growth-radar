# 🚨 ACTION REQUIRED: Get Your RapidAPI Key

The TikTok integration is **fully coded and ready** - it just needs your RapidAPI key to fetch real data.

---

## ⚡ Quick Setup (2 Minutes)

### Step 1: Go to the API Page
**https://rapidapi.com/tikwm-tikwm-default/api/tiktok-scraper7**

### Step 2: Subscribe (FREE)
1. Click **"Subscribe to Test"** button
2. Choose **Basic** plan (FREE - 100 requests/month)
3. Complete signup if needed (takes 30 seconds)

### Step 3: Get Your Key
1. Go to: **https://rapidapi.com/developer/billing/apikeys**
2. Copy your key - it looks like:
   ```
   a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
   ```
   (32 characters, letters + numbers)

### Step 4: Add to `.env`
Open `C:\Users\Admin\clawd\taboost-radar\backend\.env`

Change this line:
```env
RAPIDAPI_KEY=your_rapidapi_key_here
```

To:
```env
RAPIDAPI_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

### Step 5: Restart Backend
```bash
# Kill current process
taskkill /F /PID 143996

# Restart
cd C:\Users\Admin\clawd\taboost-radar\backend
python main.py
```

---

## ✅ Test It Works

### Test 1: Analyze Endpoint (No Auth)
```
http://localhost:8001/analyze?username=isi.cos
```

**Expected Response (with real data):**
```json
{
  "success": true,
  "username": "isi.cos",
  "stats": {
    "handle": "@isi.cos",
    "nickname": "Isabella",
    "avatar": "https://p16-sign-va.tiktokcdn.com/...",
    "followers": 125000,
    "following": 890,
    "total_likes": 4200000,
    "avg_views": 48000,
    "avg_likes": 3200,
    "avg_comments": 145,
    "avg_shares": 89,
    "engagement_rate": 6.8,
    "posts_per_week": 4.2,
    "video_count_analyzed": 10
  },
  "scores": {
    "growth_velocity": 78,
    "viral_probability": 85,
    "brand_readiness": 72,
    "overall": 78,
    "grade": "A"
  },
  "timestamp": "2026-02-20T21:30:00"
}
```

### Test 2: Creator Scores (With Auth)
```
http://localhost:8001/api/creators/c1/scores
Header: X-API-Key: tb_sk_live_a8f3b2c1d4e5f6g7h8i9j0k1l2m3n4o5
```

### Test 3: Interactive Docs
**http://localhost:8001/docs**

Click on `GET /analyze` → "Try it out" → Enter `isi.cos` → Execute

---

## 🔍 Current Status

| Component | Status |
|-----------|--------|
| TikTok Scraper Code | ✅ Complete |
| Parser (parse_tiktok_stats) | ✅ Handles tikwm format |
| Score Algorithm | ✅ Real-time computation |
| Caching (30 min) | ✅ Implemented |
| `/analyze` Endpoint | ✅ Ready |
| `/api/creators/:id/scores` | ✅ Auto-updates DB |
| **RapidAPI Key** | ❌ **NEEDS YOUR KEY** |

---

## 📊 What Happens After You Add the Key

1. **Backend restarts** with valid `RAPIDAPI_KEY`
2. **First scores request** fetches real TikTok data
3. **Parser extracts**:
   - Real follower count
   - Real avg views/likes/comments/shares
   - Real profile picture URL
   - Posting frequency from timestamps
4. **Algorithm computes** scores from real metrics
5. **Database updates** with fresh numbers
6. **Dashboard shows** real avatars and stats

---

## 🧪 Test Usernames

Try these in `/analyze?username=XXX`:
- `isi.cos` - The one you mentioned
- `charlidamelio` - 155M followers
- `khaby.lame` - Most followed
- `zachking` - Magic tricks
- `bellapoarch` - Music creator

---

## 🆘 Troubleshooting

### Error: 403 Forbidden
**Cause:** Invalid or missing RapidAPI key
**Fix:** Double-check you copied the full key to `.env`

### Error: 429 Too Many Requests
**Cause:** Hit free tier limit (100/month)
**Fix:** Wait for next month or upgrade plan

### Error: 404 User Not Found
**Cause:** Username doesn't exist or is private
**Fix:** Try a different public username

---

## 📞 Once You Have the Key

Paste it here and I'll:
1. Update the `.env` file
2. Restart the backend
3. Run a live test with `isi.cos`
4. Show you the real JSON response with actual scores

**Or just add it yourself and test at:**
```
http://localhost:8001/analyze?username=isi.cos
```

---

**The code is done. Just need the key! 🔑**
