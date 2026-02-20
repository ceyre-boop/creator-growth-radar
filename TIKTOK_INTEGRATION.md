# TikTok Integration - Real-Time Creator Scores

## ✅ What's Implemented

The backend now fetches **real TikTok data** via RapidAPI to compute creator scores dynamically.

### New Endpoints

| Endpoint | Auth | Description |
|----------|------|-------------|
| `GET /analyze?username=@handle` | ❌ No | Test endpoint - returns real stats + scores for any TikTok username |
| `GET /api/creators/:id/scores` | ✅ Yes | Returns scores computed from real TikTok data (cached 30 min) |
| `GET /api/creators/:id/scores?refresh=true` | ✅ Yes | Force refresh TikTok data (bypass cache) |

### Score Algorithm (Real Data)

Scores are computed from actual TikTok metrics:

```
Growth Velocity = (engagement × 4) + (avg_views/followers × 40) + (posts_per_week × 4)
Viral Probability = (view_ratio × 60) + (engagement × 2.5) + (share_ratio × 200)
Brand Readiness = follower_tier_score + (engagement × 3.5) + (posts_per_week × 3) + bonuses
```

**Data fetched from TikTok:**
- `followers` - Total follower count
- `avg_views` - Average play count across last 10 videos
- `avg_likes` - Average digg count
- `avg_comments` - Average comment count  
- `avg_shares` - Average share count
- `engagement_rate` - (likes + comments + shares) / followers × 100
- `posts_per_week` - Calculated from video timestamps

---

## 🔑 Required: Get Your RapidAPI Key

The TikTok scraper requires a RapidAPI key. Here's how to get one:

### Step 1: Go to RapidAPI
Visit: https://rapidapi.com/tikwm-tikwm-default/api/tiktok-scraper7

### Step 2: Subscribe
1. Click **"Subscribe to Test"** or **"Subscribe"**
2. Choose a plan (Basic tier is **FREE** - 100 requests/month)
3. Complete signup if needed

### Step 3: Get Your Key
1. Go to https://rapidapi.com/developer/billing/apikeys
2. Copy your **X-RapidAPI-Key** (looks like: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`)

### Step 4: Add to .env
Edit `backend/.env`:
```env
RAPIDAPI_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
RAPIDAPI_HOST=tiktok-scraper7.p.rapidapi.com
```

### Step 5: Restart Backend
```bash
cd C:\Users\Admin\clawd\taboost-radar\backend
# Kill existing process, then:
python main.py
```

---

## 🧪 Test It Works

### Test 1: Analyze Endpoint (No Auth)
```bash
curl "http://localhost:8001/analyze?username=charlidamelio"
```

Expected response:
```json
{
  "success": true,
  "username": "charlidamelio",
  "stats": {
    "handle": "@charlidamelio",
    "nickname": "charli d'amelio",
    "avatar": "https://...",
    "followers": 155000000,
    "avg_views": 8500000,
    "engagement_rate": 4.2,
    "posts_per_week": 3.5
  },
  "scores": {
    "growth_velocity": 78,
    "viral_probability": 85,
    "brand_readiness": 92,
    "overall": 85,
    "grade": "S"
  }
}
```

### Test 2: Creator Scores Endpoint (With Auth)
```bash
curl -H "X-API-Key: tb_sk_live_a8f3b2c1d4e5f6g7h8i9j0k1l2m3n4o5" \
  "http://localhost:8001/api/creators/c1/scores"
```

### Test 3: Force Refresh
```bash
curl -H "X-API-Key: tb_sk_live_a8f3b2c1d4e5f6g7h8i9j0k1l2m3n4o5" \
  "http://localhost:8001/api/creators/c1/scores?refresh=true"
```

---

## 📊 Caching

To avoid hitting RapidAPI limits:
- Results are cached for **30 minutes** per username
- Cache is in-memory (resets on server restart)
- Use `?refresh=true` to bypass cache

---

## 🔄 Auto-Update on Scores Request

When you call `/api/creators/:id/scores`:
1. Backend looks up creator's TikTok handle from DB
2. Fetches real data from TikTok API (or uses cache)
3. Computes fresh scores
4. **Updates the creator's DB record** with new followers, avg_views, engagement
5. Returns scores + raw stats

This means the dashboard always shows recent data after a scores request.

---

## 🛠️ Fallback Behavior

If RapidAPI key is missing or API fails:
- Returns stored scores from database
- Includes `fallback: true` in response
- Includes error message
- Frontend continues working (no crash)

---

## 📝 Sample Test Usernames

Try these in the `/analyze` endpoint:
- `@charlidamelio` - 155M followers, mega star
- `@khaby.lame` - Most followed on TikTok
- `@bellapoarch` - Music creator
- `@zachking` - Magic tricks
- `@spencerx` - Beatboxer
- `@isi.cos` - The one you mentioned

---

## 🚀 Next Steps

1. **Get RapidAPI key** (see above)
2. **Add to `.env`**
3. **Restart backend**
4. **Test with `/analyze?username=isi.cos`**
5. **Watch scores update with real data!**

Once working, the dashboard will show:
- ✅ Real profile pictures from TikTok
- ✅ Real follower counts
- ✅ Real engagement rates
- ✅ Scores computed from actual performance

---

## 📦 Files Changed

- `backend/main.py` - Added TikTok scraper, parser, score computation
- `backend/requirements.txt` - Added `httpx` for async HTTP
- `backend/.env` - Added `RAPIDAPI_KEY` placeholder

---

**Questions?** Test the `/analyze` endpoint first - it's the fastest way to verify everything works!
