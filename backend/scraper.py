"""
TikTok Scraper Module
Primary: RapidAPI TikTok Scraper (free tier)
Fallback: Direct HTML scraping with rotating user agents
"""

import httpx
import os
import random
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup

# RapidAPI configuration
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")
RAPIDAPI_HOST = "tiktok-scraper7.p.rapidapi.com"

# Rotating user agents for fallback scraping
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]


async def scrape_tiktok_profile(username: str) -> Optional[Dict[str, Any]]:
    """
    Scrape TikTok profile data.
    Tries RapidAPI first, falls back to direct HTML scraping.
    """
    # Try RapidAPI first
    if RAPIDAPI_KEY:
        try:
            return await scrape_via_rapidapi(username)
        except Exception as e:
            print(f"RapidAPI failed: {e}, trying fallback...")
    
    # Fallback to direct scraping
    return await scrape_via_html(username)


async def scrape_via_rapidapi(username: str) -> Optional[Dict[str, Any]]:
    """Scrape using RapidAPI TikTok Scraper"""
    url = f"https://{RAPIDAPI_HOST}/user/detail?region=US&sec_uid=&unique_id={username}"
    
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST,
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
    
    # Parse RapidAPI response
    if data and "userInfo" in data:
        user_info = data["userInfo"]["user"]
        stats = data["userInfo"]["stats"]
        
        return {
            "username": username,
            "followers": stats.get("followerCount", 0),
            "following": stats.get("followingCount", 0),
            "total_likes": stats.get("heartCount", 0),
            "total_videos": stats.get("videoCount", 0),
            "verified": user_info.get("verified", False),
            "bio": user_info.get("signature", ""),
            "avatar": user_info.get("avatarThumb", ""),
        }
    
    return None


async def scrape_via_html(username: str) -> Optional[Dict[str, Any]]:
    """
    Fallback: Scrape TikTok profile HTML directly.
    Note: This is less reliable and may get blocked.
    """
    url = f"https://www.tiktok.com/@{username}"
    
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
    }
    
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            # TikTok embeds data in script tags
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            
            # Look for __INITIAL_STATE__ or similar data
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and '__INITIAL_STATE__' in script.string:
                    # Parse the JSON data
                    import re
                    import json
                    match = re.search(r'__INITIAL_STATE__\s*=\s*({.+?});', script.string)
                    if match:
                        data = json.loads(match.group(1))
                        # Extract user info from the complex structure
                        user_data = extract_from_initial_state(data, username)
                        if user_data:
                            return user_data
            
            # Alternative: look for meta tags
            followers = extract_meta_tag(soup, "tiktok:followers")
            likes = extract_meta_tag(soup, "tiktok:likes")
            
            if followers:
                return {
                    "username": username,
                    "followers": int(followers.replace(',', '')),
                    "following": 0,
                    "total_likes": int(likes.replace(',', '')) if likes else 0,
                    "total_videos": 0,
                    "verified": False,
                    "bio": "",
                    "avatar": "",
                }
            
        except Exception as e:
            print(f"HTML scraping failed: {e}")
    
    return None


def extract_from_initial_state(data: dict, username: str) -> Optional[Dict[str, Any]]:
    """Extract user data from TikTok's __INITIAL_STATE__"""
    try:
        # Navigate the complex TikTok data structure
        if "UserModule" in data and "users" in data["UserModule"]:
            user = data["UserModule"]["users"].get(username)
            if user and "user" in user:
                user_info = user["user"]
                stats = user.get("stats", {})
                return {
                    "username": username,
                    "followers": stats.get("followerCount", 0),
                    "following": stats.get("followingCount", 0),
                    "total_likes": stats.get("heartCount", 0),
                    "total_videos": stats.get("videoCount", 0),
                    "verified": user_info.get("verified", False),
                    "bio": user_info.get("signature", ""),
                    "avatar": user_info.get("avatarThumb", ""),
                }
    except Exception:
        pass
    return None


def extract_meta_tag(soup: BeautifulSoup, name: str) -> Optional[str]:
    """Extract content from meta tag"""
    tag = soup.find('meta', attrs={'name': name})
    if tag and tag.has_attr('content'):
        return tag['content']
    return None


async def get_recent_posts_stats(username: str, limit: int = 10) -> Dict[str, Any]:
    """
    Get stats from recent posts (avg views, engagement, posting frequency).
    This requires additional API calls to fetch post data.
    """
    if not RAPIDAPI_KEY:
        return {
            "avg_views": 0,
            "avg_likes": 0,
            "avg_comments": 0,
            "avg_shares": 0,
            "posting_frequency_per_week": 0,
            "engagement_rate": 0,
        }
    
    try:
        url = f"https://{RAPIDAPI_HOST}/feed/user?unique_id={username}&count={limit}&region=US"
        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": RAPIDAPI_HOST,
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
        
        posts = data.get("itemList", [])
        if not posts:
            return {
                "avg_views": 0,
                "avg_likes": 0,
                "avg_comments": 0,
                "avg_shares": 0,
                "posting_frequency_per_week": 0,
                "engagement_rate": 0,
            }
        
        total_views = 0
        total_likes = 0
        total_comments = 0
        total_shares = 0
        
        timestamps = []
        for post in posts:
            stats = post.get("stats", {})
            total_views += stats.get("playCount", 0)
            total_likes += stats.get("diggCount", 0)
            total_comments += stats.get("commentCount", 0)
            total_shares += stats.get("shareCount", 0)
            
            create_time = post.get("createTime", 0)
            if create_time:
                timestamps.append(create_time)
        
        n = len(posts)
        avg_views = total_views // n if n > 0 else 0
        avg_likes = total_likes // n if n > 0 else 0
        avg_comments = total_comments // n if n > 0 else 0
        avg_shares = total_shares // n if n > 0 else 0
        
        # Calculate posting frequency (posts per week)
        posting_frequency = 0
        if len(timestamps) >= 2:
            timestamps.sort(reverse=True)
            oldest = timestamps[-1]
            newest = timestamps[0]
            days_span = max(1, (newest - oldest) / 86400)  # Convert seconds to days
            posting_frequency = (n / days_span) * 7  # Posts per week
        
        # Engagement rate = (likes + comments + shares) / followers * 100
        # We'll calculate this in the main endpoint with follower data
        
        return {
            "avg_views": avg_views,
            "avg_likes": avg_likes,
            "avg_comments": avg_comments,
            "avg_shares": avg_shares,
            "posting_frequency_per_week": round(posting_frequency, 2),
        }
        
    except Exception as e:
        print(f"Failed to get recent posts: {e}")
        return {
            "avg_views": 0,
            "avg_likes": 0,
            "avg_comments": 0,
            "avg_shares": 0,
            "posting_frequency_per_week": 0,
        }
