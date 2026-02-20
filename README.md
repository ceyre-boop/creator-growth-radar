# 📡 Creator Growth Radar

**Know who's about to blow up. Before everyone else does.**

Creator Growth Radar is a micro-SaaS that gives talent agencies and brand managers an instant, data-driven read on any TikTok creator's momentum — before they blow up and before their rates go up.

![Creator Growth Radar](https://img.shields.io/badge/status-live-success)
![License](https://img.shields.io/badge/license-MIT-blue)

## 🎯 What It Does

Enter a TikTok username and get instant analytics:

- **Profile Stats**: Followers, 24h change, avg views, engagement rate, posting frequency
- **Growth Velocity Score** (0-100): Measures momentum and follower growth trajectory
- **Viral Probability Score** (0-100): Likelihood of content reaching beyond current audience
- **Brand Deal Readiness Score** (0-100): Agency benchmark for sponsorship opportunities

All scores are color-coded (green/yellow/red) for fast decision-making.

## 🏗️ Architecture

```
creator-growth-radar/
├── backend/
│   ├── main.py           # FastAPI application
│   ├── scraper.py        # TikTok data fetching (RapidAPI + fallback)
│   ├── scorer.py         # Score computation algorithms
│   ├── requirements.txt  # Python dependencies
│   └── railway.json      # Railway deployment config
├── frontend/
│   ├── index.html        # Single page app
│   ├── style.css         # Mobile-first dark terminal styles
│   ├── app.js            # API calls + UI logic
│   └── vercel.json       # Vercel deployment config
└── README.md
```

## 🚀 Quick Start

### Backend (Local Development)

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export RAPIDAPI_KEY="your-rapidapi-key"

# Run the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000/docs` for the interactive API documentation.

### Frontend (Local Development)

```bash
cd frontend

# Update BACKEND_URL in app.js to point to your local backend
# Then open index.html in a browser or use a simple server:
python -m http.server 3000
```

Visit `http://localhost:3000`

## 📊 API Reference

### GET /analyze

Analyze a TikTok creator.

**Parameters:**
- `username` (required): TikTok username (without @)

**Example:**
```bash
curl "http://localhost:8000/analyze?username=charlidamelio"
```

**Response:**
```json
{
  "username": "charlidamelio",
  "followers": 154000000,
  "following": 1200,
  "total_likes": 11000000000,
  "total_videos": 2500,
  "verified": true,
  "follower_change_24h": 3080000,
  "avg_views_last_10": 4200000,
  "engagement_rate": 8.4,
  "posting_frequency_per_week": 4.2,
  "growth_velocity_score": 87,
  "viral_probability_score": 91,
  "brand_deal_readiness_score": 95,
  "score_breakdown": {
    "growth_velocity": {
      "raw": 87,
      "label": "Explosive",
      "color": "green"
    },
    "viral_probability": {
      "raw": 91,
      "label": "Very High",
      "color": "green"
    },
    "brand_deal_readiness": {
      "raw": 95,
      "label": "Ready Now",
      "color": "green"
    }
  }
}
```

## 🌐 Deployment

### Backend → Railway

1. Push your code to GitHub
2. Go to [Railway](https://railway.app) and create a new project
3. Connect your GitHub repository
4. Set the root directory to `backend`
5. Add environment variable: `RAPIDAPI_KEY`
6. Railway auto-detects Python and deploys

**Note:** Free tier spins down after 15min inactivity (cold start ~30s)

### Frontend → Vercel

1. Push your code to GitHub (or use the Vercel CLI)
2. Go to [Vercel](https://vercel.com) and import your repository
3. Set the root directory to `frontend`
4. Update `BACKEND_URL` in `app.js` to your Railway URL
5. Deploy!

**Alternative:** Drag and drop the `frontend` folder to Netlify

## 🔑 TikTok Data Sources

### Primary: RapidAPI TikTok Scraper

- **Service**: TikTok Scraper API on RapidAPI
- **Cost**: Free tier (~100 requests/month)
- **Reliability**: High
- **Setup**: Get API key at https://rapidapi.com

### Fallback: Direct HTML Scraping

- **Method**: BeautifulSoup + rotating user agents
- **Cost**: Free
- **Reliability**: Medium (may get blocked)
- **Use case**: When RapidAPI quota is exhausted

## 🧮 Score Algorithms

### Growth Velocity Score

Measures momentum based on:
- Follower count (log scale, 0-25 pts)
- Likes-to-follower ratio (0-25 pts)
- Posting frequency (0-25 pts)
- Avg views relative to followers (0-25 pts)

### Viral Probability Score

Measures content ceiling:
- Views-to-follower ratio >1.0 = viral reach (0-40 pts)
- Engagement rate vs industry benchmark (0-30 pts)
- Share rate (0-15 pts)
- Comment rate (0-15 pts)

### Brand Deal Readiness Score

What agencies care about:
- Follower milestones (10K, 50K, 100K, 1M) (0-40 pts)
- Engagement rate (3%+ benchmark) (0-30 pts)
- Posting consistency (0-15 pts)
- Verification status (0-10 pts)
- Historical performance bonus (0-5 pts)

## 💰 Costs at MVP Stage

| Service | Cost |
|---------|------|
| Railway backend | $0 (free tier) |
| Vercel frontend | $0 (free tier) |
| RapidAPI TikTok scraper | $0 (free tier, 100 req/mo) |
| Domain (optional) | ~$10/yr |
| **Total** | **$0–$10** |

## 📣 Agency Pitch

> "Creator Growth Radar gives talent agencies and brand managers an instant, data-driven read on any TikTok creator's momentum — before they blow up and before their rates go up. In under 10 seconds, you get a creator's growth velocity, viral probability, and brand deal readiness, scored 0-100 and color-coded for fast decisions. Instead of gut-checking spreadsheets or paying for expensive platforms, your team can run a quick radar scan on any creator, any time, and know immediately whether they're worth an outreach email today."

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, httpx, BeautifulSoup
- **Frontend**: Vanilla HTML/CSS/JS (no framework)
- **Deployment**: Railway + Vercel
- **Data**: RapidAPI TikTok Scraper

## 📝 License

MIT License - feel free to use, modify, and deploy.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📧 Contact

Built with ❤️ for the creator economy.

---

**Creator Growth Radar** © 2024
