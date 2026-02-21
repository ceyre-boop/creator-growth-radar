"""TABOOST Creator Earnings & Tax Radar - FastAPI Backend with SQLite."""
import sqlite3
import json
import os
import uuid
import time
from datetime import datetime, timezone
from typing import Optional, List
from contextlib import contextmanager
from fastapi import FastAPI, HTTPException, Header, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import csv
import io
from dotenv import load_dotenv
import httpx

# ── ENV & CONFIG ───────────────────────────────────────────────
load_dotenv()
API_KEY = os.getenv("TABOOST_API_KEY", "dev-key-change-in-production")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")
DB_PATH = os.path.join(os.path.dirname(__file__), "taboost.db")

# ── TIKTOK SCRAPER ─────────────────────────────────────────────
RAPIDAPI_HOST = "tiktok-scraper7.p.rapidapi.com"

# Cache for rate limiting: {username: (timestamp, data)}
_tiktok_cache = {}
CACHE_TTL = 1800  # 30 minutes

def get_cached_or_fetch(username: str, fetch_fn):
    """Get cached TikTok data or fetch fresh."""
    now = time.time()
    if username in _tiktok_cache:
        ts, data = _tiktok_cache[username]
        if now - ts < CACHE_TTL:
            return data
    data = None  # Will be set by caller
    _tiktok_cache[username] = (now, data)
    return data

def set_cache(username: str, data: dict):
    """Set cached TikTok data."""
    _tiktok_cache[username] = (time.time(), data)

async def fetch_tiktok_user_videos(username: str, count: int = 10) -> dict:
    """Fetch user's recent videos from TikTok."""
    clean = username.lstrip("@")
    url = f"https://{RAPIDAPI_HOST}/user/posts"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }
    params = {"unique_id": clean, "count": count}
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=headers, params=params, timeout=15)
        r.raise_for_status()
        return r.json()

async def fetch_tiktok_user_info(username: str) -> dict:
    """Fetch user profile info from TikTok."""
    clean = username.lstrip("@")
    url = f"https://{RAPIDAPI_HOST}/user/info"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }
    params = {"unique_id": clean}
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=headers, params=params, timeout=15)
        r.raise_for_status()
        return r.json()

def parse_tiktok_stats(videos_response: dict, user_info_response: dict) -> dict:
    """Parse TikTok API responses into normalized stats.
    
    Expected API structure:
    {
      "code": 0,
      "data": {
        "videos": [{
          "aweme_id": "...",
          "play_count": 123456,
          "digg_count": 5678,
          "comment_count": 123,
          "share_count": 45,
          "create_time": 1234567890,
          "author": {
            "unique_id": "username",
            "nickname": "Display Name",
            "avatar": "https://..."
          }
        }]
      }
    }
    """
    # Handle both response formats
    if videos_response.get("code") == 0:
        videos_data = videos_response.get("data", {})
        videos = videos_data.get("videos", [])
    else:
        videos = videos_response.get("videos", []) or videos_response.get("data", {}).get("videos", [])
    
    if user_info_response.get("code") == 0:
        user_data = user_info_response.get("data", {})
        user_info = user_data.get("user", {}) or user_data.get("userInfo", {})
    else:
        user_info = user_info_response.get("user", {}) or user_info_response.get("data", {}).get("user", {})
    
    # Extract user info - handle multiple API response formats
    handle = user_info.get("unique_id", "") or user_info.get("id", "")
    if not handle and videos and len(videos) > 0:
        author = videos[0].get("author", {})
        handle = author.get("unique_id", "") or author.get("id", "")
    
    nickname = user_info.get("nickname", "") or (videos[0].get("author", {}).get("nickname", "")) if videos else handle
    avatar = user_info.get("avatar", "") or user_info.get("avatarMedium", "") or user_info.get("avatarLarger", "")
    if not avatar and videos and len(videos) > 0:
        avatar = videos[0].get("author", {}).get("avatar", "")
    
    followers = int(user_info.get("followerCount", 0) or user_info.get("followers", 0) or user_info.get("fanCount", 0) or 0)
    following = int(user_info.get("followingCount", 0) or user_info.get("following", 0) or 0)
    total_likes = int(user_info.get("heartCount", 0) or user_info.get("totalLikes", 0) or user_info.get("heart", 0) or 0)
    
    # Calculate averages from videos
    if videos:
        # Handle both camelCase and snake_case field names
        play_counts = [int(v.get("play_count", 0) or v.get("playCount", 0) or 0) for v in videos]
        digg_counts = [int(v.get("digg_count", 0) or v.get("diggCount", 0) or 0) for v in videos]
        comment_counts = [int(v.get("comment_count", 0) or v.get("commentCount", 0) or 0) for v in videos]
        share_counts = [int(v.get("share_count", 0) or v.get("shareCount", 0) or 0) for v in videos]
        create_times = [int(v.get("create_time", 0) or v.get("createTime", 0) or 0) for v in videos]
        
        avg_views = round(sum(play_counts) / len(play_counts)) if play_counts else 0
        avg_likes = round(sum(digg_counts) / len(digg_counts)) if digg_counts else 0
        avg_comments = round(sum(comment_counts) / len(comment_counts)) if comment_counts else 0
        avg_shares = round(sum(share_counts) / len(share_counts)) if share_counts else 0
        
        # Posts per week calculation
        posts_per_week = 4.0  # default
        if len(create_times) >= 2:
            oldest = min(create_times)
            newest = max(create_times)
            days_span = max(1, (newest - oldest) / 86400)
            weeks_span = days_span / 7
            posts_per_week = round(len(videos) / max(weeks_span, 0.1), 1)
        
        # Engagement rate
        if followers > 0:
            engagement_rate = round((avg_likes + avg_comments + avg_shares) / followers * 100, 2)
        else:
            engagement_rate = 0
    else:
        avg_views = 0
        avg_likes = 0
        avg_comments = 0
        avg_shares = 0
        posts_per_week = 0
        engagement_rate = 0
    
    return {
        "handle": f"@{handle}" if handle and not handle.startswith("@") else handle,
        "nickname": nickname,
        "avatar": avatar,
        "followers": followers,
        "following": following,
        "total_likes": total_likes,
        "avg_views": avg_views,
        "avg_likes": avg_likes,
        "avg_comments": avg_comments,
        "avg_shares": avg_shares,
        "engagement_rate": min(100, engagement_rate),
        "posts_per_week": posts_per_week,
        "video_count_analyzed": len(videos)
    }

def compute_scores(stats: dict) -> dict:
    """Compute growth, viral, and brand scores from real stats."""
    followers = stats.get("followers", 0)
    avg_views = stats.get("avg_views", 0)
    engagement = stats.get("engagement_rate", 0)
    posts_per_week = stats.get("posts_per_week", 4)
    avg_shares = stats.get("avg_shares", 0)
    
    # Growth Velocity: rewards high posting freq + strong engagement + view momentum
    growth = min(100, round(
        (engagement * 4) + 
        (avg_views / max(followers, 1) * 40) + 
        (posts_per_week * 4)
    ))
    
    # Viral Probability: views vs followers ratio is the key signal
    view_ratio = avg_views / max(followers, 1)
    viral = min(100, round(
        (view_ratio * 60) + 
        (engagement * 2.5) + 
        (avg_shares / max(avg_views, 1) * 200)
    ))
    
    # Brand Readiness: follower threshold + engagement quality + consistency
    follower_score = min(40, (len(str(int(followers))) - 3) * 10) if followers > 0 else 0
    brand = min(100, round(
        follower_score + 
        (engagement * 3.5) + 
        (posts_per_week * 3) + 
        (10 if followers >= 10000 else 0) + 
        (10 if followers >= 100000 else 0)
    ))
    
    avg = round((growth + viral + brand) / 3)
    letter = "S" if avg >= 80 else "A" if avg >= 65 else "B" if avg >= 45 else "C"
    
    return {
        "growth_velocity": max(5, growth),
        "viral_probability": max(5, viral),
        "brand_readiness": max(5, brand),
        "overall": avg,
        "grade": letter
    }

# ── APP SETUP ──────────────────────────────────────────────────
app = FastAPI(
    title="TABOOST Creator Earnings & Tax Radar API",
    description="API for creator earnings tracking and agency management",
    version="1.0.0"
)

# ── CORS ───────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── DATABASE SETUP ─────────────────────────────────────────────
def init_db():
    """Initialize SQLite database with tables and seed data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Creators table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS creators (
            id TEXT PRIMARY KEY,
            handle TEXT NOT NULL UNIQUE,
            name TEXT,
            followers INTEGER DEFAULT 0,
            avg_views INTEGER DEFAULT 0,
            engagement REAL DEFAULT 0,
            posts_per_week REAL DEFAULT 4,
            status TEXT DEFAULT 'trending',
            trend TEXT DEFAULT '[]',
            notes TEXT DEFAULT '',
            home_state TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Earnings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS earnings (
            id TEXT PRIMARY KEY,
            creator_id TEXT NOT NULL,
            source TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            note TEXT DEFAULT '',
            tax_year INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (creator_id) REFERENCES creators(id)
        )
    """)
    
    # Scores table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            creator_id TEXT PRIMARY KEY,
            growth_velocity INTEGER DEFAULT 50,
            viral_probability INTEGER DEFAULT 50,
            brand_readiness INTEGER DEFAULT 50,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (creator_id) REFERENCES creators(id)
        )
    """)
    
    # Check if we need to seed data
    cursor.execute("SELECT COUNT(*) FROM creators")
    if cursor.fetchone()[0] == 0:
        # Seed with sample creators
        seed_creators = [
            ("c1", "@rileydance", "Riley Summers", 892000, 410000, 8.7, 6, "hot", "[820,835,841,858,867,879,892]", "Brand deal closing with FashionNova. Push engagement this week."),
            ("c2", "@chefmarcus", "Marcus Webb", 234000, 98000, 11.2, 4, "trending", "[198,205,210,218,224,229,234]", "Food niche — strong CPMs. Ready for first brand deal."),
            ("c3", "@techbyjay", "Jason Park", 1400000, 620000, 5.1, 3, "hot", "[1310,1330,1350,1368,1380,1392,1400]", "Biggest account. Keep posting consistently."),
            ("c4", "@lilylifts", "Lily Torres", 67000, 31000, 14.8, 7, "trending", "[51,54,57,59,62,65,67]", "Engagement is insane. Build to 100k before pitching brands."),
            ("c5", "@dj_kobi", "Kobi Mensah", 388000, 145000, 6.3, 2, "watch", "[392,391,390,389,390,388,388]", "Stagnating. Need content strategy meeting."),
            ("c6", "@gemmacooks", "Gemma Hill", 155000, 72000, 9.4, 5, "trending", "[138,141,144,148,151,153,155]", "Consistent grower. Pitch kitchenware deals.")
        ]
        
        cursor.executemany("""
            INSERT INTO creators (id, handle, name, followers, avg_views, engagement, posts_per_week, status, trend, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, seed_creators)
        
        # Seed scores
        seed_scores = [
            ("c1", 78, 65, 82),
            ("c2", 85, 72, 68),
            ("c3", 62, 58, 91),
            ("c4", 92, 88, 55),
            ("c5", 45, 40, 70),
            ("c6", 80, 75, 72)
        ]
        
        cursor.executemany("""
            INSERT INTO scores (creator_id, growth_velocity, viral_probability, brand_readiness)
            VALUES (?, ?, ?, ?)
        """, seed_scores)
        
        # Seed earnings for c1
        seed_earnings = [
            (str(uuid.uuid4()), "c1", "live", 84.50, "2025-01-14", "Tuesday night LIVE, 1.5hrs", 2025),
            (str(uuid.uuid4()), "c1", "brand", 350.00, "2025-01-11", "Fashion Nova post", 2025),
            (str(uuid.uuid4()), "c1", "live", 42.25, "2025-01-09", "Weekend LIVE", 2025),
            (str(uuid.uuid4()), "c1", "fund", 28.10, "2025-01-07", "Creator Fund payout", 2025)
        ]
        
        cursor.executemany("""
            INSERT INTO earnings (id, creator_id, source, amount, date, note, tax_year)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, seed_earnings)
    
    conn.commit()
    conn.close()

# Initialize DB on startup
init_db()

@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# ── AUTH DEPENDENCY ────────────────────────────────────────────
def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verify API key for protected endpoints."""
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return x_api_key

# ── ROOT & HEALTH ──────────────────────────────────────────────
@app.get("/")
async def root():
    """Root endpoint - API info."""
    return {
        "status": "TABOOST API running",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """Health check - no auth required."""
    return {"status": "ok", "service": "taboost-api"}

@app.get("/analyze")
async def analyze_creator(username: str = Query(..., description="TikTok username (with or without @)")):
    """Analyze a TikTok creator and return real scores (no auth required for testing)."""
    if not RAPIDAPI_KEY:
        return {
            "error": "RAPIDAPI_KEY not configured",
            "hint": "Set RAPIDAPI_KEY in .env file"
        }
    
    try:
        videos_response = await fetch_tiktok_user_videos(username)
        user_info_response = await fetch_tiktok_user_info(username)
        
        stats = parse_tiktok_stats(videos_response, user_info_response)
        scores = compute_scores(stats)
        
        return {
            "success": True,
            "username": username,
            "stats": stats,
            "scores": scores,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "username": username,
            "error": str(e)
        }

# ── STATS ENDPOINT ─────────────────────────────────────────────
@app.get("/api/stats")
async def get_stats(api_key: str = Depends(verify_api_key)):
    """Get agency-wide statistics."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Total creators
        cursor.execute("SELECT COUNT(*) FROM creators")
        total_creators = cursor.fetchone()[0]
        
        # Total earnings
        cursor.execute("SELECT COUNT(*), SUM(amount) FROM earnings")
        row = cursor.fetchone()
        total_earnings = row[1] or 0
        total_count = row[0] or 0
        
        # YTD total
        current_year = datetime.now().year
        cursor.execute("SELECT SUM(amount) FROM earnings WHERE tax_year = ?", (current_year,))
        ytd_total = cursor.fetchone()[0] or 0
        
        return {
            "totalCreators": total_creators,
            "totalEarningsLogged": total_count,
            "totalEarningsAmount": round(total_earnings, 2),
            "ytdTotal": round(ytd_total, 2),
            "taxYear": current_year
        }

# ── CREATOR ENDPOINTS ──────────────────────────────────────────

@app.get("/api/creators")
async def list_creators(api_key: str = Depends(verify_api_key)):
    """Get full creator roster."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM creators ORDER BY followers DESC")
        rows = cursor.fetchall()
        
        creators = []
        for row in rows:
            creator = dict(row)
            creator["trend"] = json.loads(creator["trend"] or "[]")
            creators.append(creator)
        
        return creators

@app.get("/api/creators/{creator_id}")
async def get_creator(creator_id: str, api_key: str = Depends(verify_api_key)):
    """Get single creator details."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM creators WHERE id = ?", (creator_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Creator not found")
        
        creator = dict(row)
        creator["trend"] = json.loads(creator["trend"] or "[]")
        return creator

@app.post("/api/creators")
async def create_creator(creator_data: dict, api_key: str = Depends(verify_api_key)):
    """Add new creator to roster."""
    new_id = str(uuid.uuid4())
    
    engagement = creator_data.get("engagement", 0)
    status = "hot" if engagement > 8 else "trending"
    followers = creator_data.get("followers", 1000)
    trend = [round(followers * m, 0) for m in [0.94, 0.95, 0.96, 0.97, 0.98, 0.99, 1.0]]
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO creators (id, handle, name, followers, avg_views, engagement, posts_per_week, status, trend)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            new_id,
            creator_data.get("handle", "@unknown"),
            creator_data.get("name", "Unknown"),
            followers,
            creator_data.get("avgViews", 0),
            engagement,
            creator_data.get("postsPerWeek", 4),
            status,
            json.dumps(trend)
        ))
        conn.commit()
        
        # Create default scores
        cursor.execute("""
            INSERT INTO scores (creator_id) VALUES (?)
        """, (new_id,))
        conn.commit()
    
    return {
        "id": new_id,
        "handle": creator_data.get("handle", "@unknown"),
        "name": creator_data.get("name", "Unknown"),
        "followers": followers,
        "avgViews": creator_data.get("avgViews", 0),
        "engagement": engagement,
        "postsPerWeek": creator_data.get("postsPerWeek", 4),
        "status": status,
        "trend": trend,
        "notes": ""
    }

@app.put("/api/creators/{creator_id}/notes")
async def update_creator_notes(creator_id: str, notes_data: dict, api_key: str = Depends(verify_api_key)):
    """Update manager notes for a creator."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM creators WHERE id = ?", (creator_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Creator not found")
        
        cursor.execute("UPDATE creators SET notes = ? WHERE id = ?", (notes_data.get("notes", ""), creator_id))
        conn.commit()
        
        cursor.execute("SELECT * FROM creators WHERE id = ?", (creator_id,))
        row = cursor.fetchone()
        creator = dict(row)
        creator["trend"] = json.loads(creator["trend"] or "[]")
        return creator

@app.get("/api/creators/{creator_id}/scores")
async def get_creator_scores(creator_id: str, api_key: str = Depends(verify_api_key), refresh: bool = Query(False)):
    """Get performance scores for a creator (with real TikTok data)."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Get creator info
        cursor.execute("SELECT * FROM creators WHERE id = ?", (creator_id,))
        creator_row = cursor.fetchone()
        
        if not creator_row:
            raise HTTPException(status_code=404, detail="Creator not found")
        
        creator = dict(creator_row)
        handle = creator["handle"].lstrip("@")
        
        # Check cache first (unless refresh requested)
        cached = _tiktok_cache.get(handle)
        if cached and not refresh:
            ts, stats = cached
            if time.time() - ts < CACHE_TTL:
                scores = compute_scores(stats)
                return {
                    **scores,
                    "stats": stats,
                    "cached": True,
                    "cacheAge": round(time.time() - ts)
                }
        
        # Fetch real TikTok data
        if not RAPIDAPI_KEY:
            # Fallback to stored data if no API key
            cursor.execute("SELECT * FROM scores WHERE creator_id = ?", (creator_id,))
            row = cursor.fetchone()
            if row:
                return {
                    "growth_velocity": row["growth_velocity"],
                    "viral_probability": row["viral_probability"],
                    "brand_readiness": row["brand_readiness"],
                    "overall": round((row["growth_velocity"] + row["viral_probability"] + row["brand_readiness"]) / 3),
                    "cached": False,
                    "note": "No RAPIDAPI_KEY configured - using stored scores"
                }
            return {"growth_velocity": 50, "viral_probability": 50, "brand_readiness": 50, "overall": 50}
        
        try:
            videos_response = await fetch_tiktok_user_videos(handle)
            user_info_response = await fetch_tiktok_user_info(handle)
            
            stats = parse_tiktok_stats(videos_response, user_info_response)
            scores = compute_scores(stats)
            
            # Cache the result
            set_cache(handle, stats)
            
            # Update creator in DB with fresh data
            cursor.execute("""
                UPDATE creators SET 
                    followers = ?, avg_views = ?, engagement = ?, posts_per_week = ?,
                    trend = ?, notes = ?
                WHERE id = ?
            """, (
                stats["followers"],
                stats["avg_views"],
                stats["engagement_rate"],
                stats["posts_per_week"],
                json.dumps(stats.get("trend", [stats["followers"]] * 7)),
                f"Auto-updated from TikTok • {stats['video_count_analyzed']} videos analyzed",
                creator_id
            ))
            
            # Update or insert scores
            cursor.execute("""
                INSERT OR REPLACE INTO scores (creator_id, growth_velocity, viral_probability, brand_readiness, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (creator_id, scores["growth_velocity"], scores["viral_probability"], scores["brand_readiness"]))
            
            conn.commit()
            
            return {
                **scores,
                "stats": stats,
                "cached": False,
                "source": "tiktok_api"
            }
        except Exception as e:
            # Fallback to stored scores on API error
            cursor.execute("SELECT * FROM scores WHERE creator_id = ?", (creator_id,))
            row = cursor.fetchone()
            if row:
                return {
                    "growth_velocity": row["growth_velocity"],
                    "viral_probability": row["viral_probability"],
                    "brand_readiness": row["brand_readiness"],
                    "overall": round((row["growth_velocity"] + row["viral_probability"] + row["brand_readiness"]) / 3),
                    "error": str(e),
                    "fallback": True
                }
            raise HTTPException(status_code=500, detail=f"TikTok API error: {str(e)}")

# ── EARNINGS ENDPOINTS ─────────────────────────────────────────

@app.get("/api/creators/{creator_id}/earnings")
async def get_earnings(creator_id: str, api_key: str = Depends(verify_api_key)):
    """Get earnings history for a creator."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM earnings WHERE creator_id = ? ORDER BY date DESC", (creator_id,))
        rows = cursor.fetchall()
        
        return [
            {
                "id": row["id"],
                "source": row["source"],
                "amount": row["amount"],
                "date": row["date"],
                "note": row["note"] or ""
            }
            for row in rows
        ]

@app.get("/api/creators/{creator_id}/earnings/ytd")
async def get_ytd_earnings(creator_id: str, api_key: str = Depends(verify_api_key)):
    """Get year-to-date earnings summary."""
    current_year = datetime.now().year
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT source, SUM(amount) as total 
            FROM earnings 
            WHERE creator_id = ? AND tax_year = ?
            GROUP BY source
        """, (creator_id, current_year))
        rows = cursor.fetchall()
        
        by_source = {row["source"]: row["total"] for row in rows}
        ytd_total = sum(by_source.values())
        
        return {
            "creatorId": creator_id,
            "taxYear": current_year,
            "ytdTotal": round(ytd_total, 2),
            "bySource": by_source
        }

@app.post("/api/creators/{creator_id}/earnings")
async def create_earning(creator_id: str, earning_data: dict, api_key: str = Depends(verify_api_key)):
    """Log a new earning entry."""
    new_id = str(uuid.uuid4())
    date_str = earning_data.get("date", datetime.now().strftime("%Y-%m-%d"))
    tax_year = int(date_str.split("-")[0])
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM creators WHERE id = ?", (creator_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Creator not found")
        
        cursor.execute("""
            INSERT INTO earnings (id, creator_id, source, amount, date, note, tax_year)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            new_id,
            creator_id,
            earning_data.get("source", "other"),
            earning_data.get("amount", 0),
            date_str,
            earning_data.get("note", ""),
            tax_year
        ))
        conn.commit()
    
    return {
        "id": new_id,
        "source": earning_data.get("source", "other"),
        "amount": earning_data.get("amount", 0),
        "date": date_str,
        "note": earning_data.get("note", "")
    }

@app.delete("/api/creators/{creator_id}/earnings/{earning_id}")
async def delete_earning(creator_id: str, earning_id: str, api_key: str = Depends(verify_api_key)):
    """Delete an earning entry."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM earnings WHERE id = ? AND creator_id = ?", (earning_id, creator_id))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Earning not found")
        
        cursor.execute("DELETE FROM earnings WHERE id = ? AND creator_id = ?", (earning_id, creator_id))
        conn.commit()
    
    return {"success": True, "message": "Entry deleted"}

# ── EXPORT ENDPOINTS ───────────────────────────────────────────

@app.get("/api/creators/{creator_id}/export/csv")
async def export_csv(creator_id: str, api_key: str = Depends(verify_api_key)):
    """Export earnings as CSV."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM creators WHERE id = ?", (creator_id,))
        creator_row = cursor.fetchone()
        
        if not creator_row:
            raise HTTPException(status_code=404, detail="Creator not found")
        
        creator = dict(creator_row)
        
        cursor.execute("SELECT * FROM earnings WHERE creator_id = ? ORDER BY date DESC", (creator_id,))
        earnings = [dict(row) for row in cursor.fetchall()]
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow(["Creator Earnings Export"])
        writer.writerow([f"Creator: {creator['name']} ({creator['handle']})"])
        writer.writerow([f"Export Date: {datetime.now().isoformat()}"])
        writer.writerow([])
        writer.writerow(["Date", "Source", "Amount (USD)", "Notes"])
        
        for e in earnings:
            writer.writerow([e["date"], e["source"], f"{e['amount']:.2f}", e.get("note", "")])
        
        output.seek(0)
        
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={creator['handle']}_earnings.csv"}
        )

@app.get("/api/creators/{creator_id}/export/pdf")
async def export_pdf(creator_id: str, api_key: str = Depends(verify_api_key)):
    """Export earnings as HTML for PDF printing."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM creators WHERE id = ?", (creator_id,))
        creator_row = cursor.fetchone()
        
        if not creator_row:
            raise HTTPException(status_code=404, detail="Creator not found")
        
        creator = dict(creator_row)
        
        cursor.execute("SELECT * FROM earnings WHERE creator_id = ? ORDER BY date DESC", (creator_id,))
        earnings = [dict(row) for row in cursor.fetchall()]
        ytd_total = sum(e["amount"] for e in earnings)
        
        rows_html = "".join(
            f"<tr><td>{e['date']}</td><td>{e['source']}</td><td>${e['amount']:.2f}</td><td>{e.get('note', '-') or '-'}</td></tr>"
            for e in earnings
        )
        
        html_content = f"""
        <html>
        <head><title>Tax Pack - {creator['handle']}</title>
        <style>
            body {{ font-family: monospace; padding: 40px; color: #111; }}
            h1 {{ font-size: 22px; margin-bottom: 4px; }}
            .sub {{ color: #666; font-size: 12px; margin-bottom: 30px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th {{ text-align: left; padding: 8px; background: #f5f5f5; }}
            td {{ padding: 8px; border-bottom: 1px solid #eee; }}
            .total {{ font-weight: bold; margin-top: 24px; font-size: 16px; }}
        </style></head>
        <body>
            <h1>Creator Earnings — Tax Pack</h1>
            <div class="sub">{creator['name']} ({creator['handle']}) · Generated {datetime.now().strftime('%Y-%m-%d')}</div>
            <table>
                <tr><th>Date</th><th>Source</th><th>Amount</th><th>Notes</th></tr>
                {rows_html}
            </table>
            <div class="total">YTD Total: ${ytd_total:.2f}</div>
        </body></html>
        """
        
        return StreamingResponse(
            io.BytesIO(html_content.encode()),
            media_type="text/html",
            headers={"Content-Disposition": f"attachment; filename={creator['handle']}_tax_pack.html"}
        )

# ── RUN ────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
