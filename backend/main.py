"""
Creator Growth Radar - Backend API
FastAPI application for TikTok creator analytics
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import asyncio

from scraper import scrape_tiktok_profile, get_recent_posts_stats
from scorer import compute_all_scores

app = FastAPI(
    title="Creator Growth Radar API",
    description="TikTok creator analytics and scoring API",
    version="1.0.0",
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Creator Growth Radar API",
        "status": "online",
        "version": "1.0.0",
    }


@app.get("/analyze")
async def analyze_creator(username: str = Query(..., description="TikTok username to analyze")):
    """
    Analyze a TikTok creator and return scores.
    
    Returns:
    - Profile stats (followers, following, total likes, etc.)
    - Recent post metrics (avg views, engagement rate, posting frequency)
    - Three computed scores (0-100 each):
      - growth_velocity_score
      - viral_probability_score
      - brand_deal_readiness_score
    """
    # Clean username (remove @ if present)
    username = username.lstrip("@").strip()
    
    if not username:
        raise HTTPException(status_code=400, detail="Username is required")
    
    # Fetch profile data
    profile_data = await scrape_tiktok_profile(username)
    
    if not profile_data:
        raise HTTPException(
            status_code=404,
            detail=f"Could not find TikTok profile for @{username}. The account may be private or doesn't exist.",
        )
    
    # Fetch recent posts stats
    posts_data = await get_recent_posts_stats(username, limit=10)
    
    # Calculate engagement rate
    followers = profile_data.get("followers", 1)
    avg_likes = posts_data.get("avg_likes", 0)
    avg_comments = posts_data.get("avg_comments", 0)
    avg_shares = posts_data.get("avg_shares", 0)
    
    if followers > 0 and (avg_likes + avg_comments + avg_shares) > 0:
        engagement_rate = ((avg_likes + avg_comments + avg_shares) / followers) * 100
    else:
        # Fallback: use total likes / followers if no recent post data
        total_likes = profile_data.get("total_likes", 0)
        total_videos = profile_data.get("total_videos", 1)
        if followers > 0 and total_videos > 0:
            avg_likes_per_video = total_likes / total_videos
            engagement_rate = (avg_likes_per_video / followers) * 100
        else:
            engagement_rate = 0
    
    # Combine all data for scoring
    scoring_data = {
        **profile_data,
        **posts_data,
        "engagement_rate": round(engagement_rate, 2),
    }
    
    # Compute scores
    scores = compute_all_scores(scoring_data)
    
    # Estimate 24h follower change (simulated based on growth velocity)
    # In production, this would require historical data tracking
    growth_velocity = scores["growth_velocity"]["raw"]
    if growth_velocity >= 80:
        follower_change_24h = int(followers * 0.02)  # 2% daily growth
    elif growth_velocity >= 60:
        follower_change_24h = int(followers * 0.01)  # 1% daily growth
    elif growth_velocity >= 40:
        follower_change_24h = int(followers * 0.005)  # 0.5% daily growth
    else:
        follower_change_24h = int(followers * 0.001)  # 0.1% daily growth
    
    # Build response
    response = {
        "username": username,
        "followers": followers,
        "following": profile_data.get("following", 0),
        "total_likes": profile_data.get("total_likes", 0),
        "total_videos": profile_data.get("total_videos", 0),
        "verified": profile_data.get("verified", False),
        "follower_change_24h": follower_change_24h,
        "avg_views_last_10": posts_data.get("avg_views", 0),
        "engagement_rate": round(engagement_rate, 2),
        "posting_frequency_per_week": posts_data.get("posting_frequency_per_week", 0),
        "growth_velocity_score": scores["growth_velocity"]["raw"],
        "viral_probability_score": scores["viral_probability"]["raw"],
        "brand_deal_readiness_score": scores["brand_deal_readiness"]["raw"],
        "score_breakdown": {
            "growth_velocity": scores["growth_velocity"],
            "viral_probability": scores["viral_probability"],
            "brand_deal_readiness": scores["brand_deal_readiness"],
        },
    }
    
    return response


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "api": "operational",
        "scraper": "ready",
        "scorer": "ready",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
