"""
Score Computation Algorithms
- Growth Velocity Score (0-100): Measures momentum
- Viral Probability Score (0-100): Measures content ceiling
- Brand Deal Readiness Score (0-100): What agencies care about
"""

from typing import Dict, Any


def compute_growth_velocity_score(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Growth Velocity Score (0-100)
    Measures momentum based on:
    - Follower count (log scale - diminishing returns)
    - Total likes-to-follower ratio (engagement depth)
    - Posting frequency (activity level)
    - Average views trend (recent performance)
    
    Weights recent activity heavily over historical totals.
    """
    followers = data.get("followers", 0)
    total_likes = data.get("total_likes", 0)
    posting_frequency = data.get("posting_frequency_per_week", 0)
    avg_views = data.get("avg_views", 0)
    
    score = 0
    
    # Follower count score (0-25 points, log scale)
    # 1K = 5pts, 10K = 10pts, 100K = 15pts, 1M = 20pts, 10M+ = 25pts
    if followers >= 10_000_000:
        follower_score = 25
    elif followers >= 1_000_000:
        follower_score = 20
    elif followers >= 100_000:
        follower_score = 15
    elif followers >= 10_000:
        follower_score = 10
    elif followers >= 1_000:
        follower_score = 5
    else:
        follower_score = max(0, (followers / 1000) * 5)
    score += follower_score
    
    # Likes-to-follower ratio (0-25 points)
    # Higher ratio = more engaged audience
    if followers > 0:
        like_ratio = total_likes / followers
        # 100+ ratio = 25pts, 50+ = 20pts, 20+ = 15pts, 10+ = 10pts, 5+ = 5pts
        if like_ratio >= 100:
            ratio_score = 25
        elif like_ratio >= 50:
            ratio_score = 20
        elif like_ratio >= 20:
            ratio_score = 15
        elif like_ratio >= 10:
            ratio_score = 10
        elif like_ratio >= 5:
            ratio_score = 5
        else:
            ratio_score = min(25, like_ratio)
        score += ratio_score
    
    # Posting frequency (0-25 points)
    # 7+ posts/week = 25pts, 5+ = 20pts, 3+ = 15pts, 1+ = 10pts
    if posting_frequency >= 7:
        freq_score = 25
    elif posting_frequency >= 5:
        freq_score = 20
    elif posting_frequency >= 3:
        freq_score = 15
    elif posting_frequency >= 1:
        freq_score = 10
    elif posting_frequency > 0:
        freq_score = posting_frequency * 10
    else:
        freq_score = 0
    score += freq_score
    
    # Average views relative to followers (0-25 points)
    # Views/follower > 1.0 means viral reach beyond audience
    if followers > 0:
        views_ratio = avg_views / followers
        if views_ratio >= 1.0:
            views_score = 25
        elif views_ratio >= 0.5:
            views_score = 20
        elif views_ratio >= 0.2:
            views_score = 15
        elif views_ratio >= 0.1:
            views_score = 10
        elif views_ratio >= 0.05:
            views_score = 5
        else:
            views_score = min(25, views_ratio * 100)
        score += views_score
    
    # Determine label and color
    if score >= 80:
        label = "Explosive"
        color = "green"
    elif score >= 60:
        label = "High"
        color = "lime"
    elif score >= 40:
        label = "Moderate"
        color = "yellow"
    elif score >= 20:
        label = "Low"
        color = "orange"
    else:
        label = "Minimal"
        color = "red"
    
    return {
        "raw": min(100, max(0, int(score))),
        "label": label,
        "color": color,
    }


def compute_viral_probability_score(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Viral Probability Score (0-100)
    Measures content ceiling based on:
    - Avg views / follower ratio (>1.0 = reaching beyond audience)
    - Engagement rate vs niche average
    - Consistency of high-view posts
    
    Key insight: If avg views > followers, content is going viral
    """
    followers = data.get("followers", 0)
    avg_views = data.get("avg_views", 0)
    avg_likes = data.get("avg_likes", 0)
    avg_comments = data.get("avg_comments", 0)
    avg_shares = data.get("avg_shares", 0)
    engagement_rate = data.get("engagement_rate", 0)
    
    score = 0
    
    # Views-to-follower ratio (0-40 points) - MOST IMPORTANT
    # This is the strongest viral indicator
    if followers > 0:
        views_ratio = avg_views / followers
        if views_ratio >= 2.0:
            # Content reaching 2x+ their audience - very viral
            ratio_score = 40
        elif views_ratio >= 1.0:
            # Reaching beyond their audience
            ratio_score = 35
        elif views_ratio >= 0.5:
            ratio_score = 25
        elif views_ratio >= 0.2:
            ratio_score = 15
        elif views_ratio >= 0.1:
            ratio_score = 10
        else:
            ratio_score = min(40, views_ratio * 100)
        score += ratio_score
    
    # Engagement rate (0-30 points)
    # 10%+ = 30pts, 5%+ = 25pts, 3%+ = 20pts (agency benchmark), 1%+ = 10pts
    if engagement_rate >= 10:
        eng_score = 30
    elif engagement_rate >= 5:
        eng_score = 25
    elif engagement_rate >= 3:
        eng_score = 20
    elif engagement_rate >= 1:
        eng_score = 10
    else:
        eng_score = min(30, engagement_rate * 10)
    score += eng_score
    
    # Share rate - shares indicate viral potential (0-15 points)
    if avg_views > 0:
        share_rate = (avg_shares / avg_views) * 100
        if share_rate >= 5:
            share_score = 15
        elif share_rate >= 2:
            share_score = 12
        elif share_rate >= 1:
            share_score = 8
        elif share_rate >= 0.5:
            share_score = 5
        else:
            share_score = min(15, share_rate * 10)
        score += share_score
    
    # Comment rate - comments indicate engagement depth (0-15 points)
    if avg_views > 0:
        comment_rate = (avg_comments / avg_views) * 100
        if comment_rate >= 3:
            comment_score = 15
        elif comment_rate >= 1:
            comment_score = 12
        elif comment_rate >= 0.5:
            comment_score = 8
        elif comment_rate >= 0.2:
            comment_score = 5
        else:
            comment_score = min(15, comment_rate * 50)
        score += comment_score
    
    # Determine label and color
    if score >= 80:
        label = "Very High"
        color = "green"
    elif score >= 60:
        label = "High"
        color = "lime"
    elif score >= 40:
        label = "Moderate"
        color = "yellow"
    elif score >= 20:
        label = "Low"
        color = "orange"
    else:
        label = "Very Low"
        color = "red"
    
    return {
        "raw": min(100, max(0, int(score))),
        "label": label,
        "color": color,
    }


def compute_brand_deal_readiness_score(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Brand Deal Readiness Score (0-100)
    What agencies actually care about:
    - Follower count thresholds (10K, 50K, 100K, 1M checkpoints)
    - Engagement rate (3%+ is the agency benchmark)
    - Posting consistency
    - Niche clarity (verified status as proxy)
    """
    followers = data.get("followers", 0)
    engagement_rate = data.get("engagement_rate", 0)
    posting_frequency = data.get("posting_frequency_per_week", 0)
    verified = data.get("verified", False)
    
    score = 0
    
    # Follower milestones (0-40 points)
    # Agencies have hard thresholds for campaign tiers
    if followers >= 1_000_000:
        # Macro influencer - top tier
        follower_score = 40
    elif followers >= 500_000:
        follower_score = 35
    elif followers >= 100_000:
        # Mid-tier influencer
        follower_score = 30
    elif followers >= 50_000:
        follower_score = 25
    elif followers >= 10_000:
        # Micro influencer - minimum for most campaigns
        follower_score = 20
    elif followers >= 5_000:
        follower_score = 15
    elif followers >= 1_000:
        follower_score = 10
    else:
        follower_score = min(20, (followers / 1000) * 10)
    score += follower_score
    
    # Engagement rate (0-30 points)
    # 3%+ is the industry benchmark for brand deals
    if engagement_rate >= 10:
        eng_score = 30
    elif engagement_rate >= 5:
        eng_score = 25
    elif engagement_rate >= 3:
        # Agency benchmark hit
        eng_score = 20
    elif engagement_rate >= 2:
        eng_score = 15
    elif engagement_rate >= 1:
        eng_score = 10
    else:
        eng_score = min(30, engagement_rate * 10)
    score += eng_score
    
    # Posting consistency (0-15 points)
    # Brands want reliable content creators
    if posting_frequency >= 5:
        consistency_score = 15
    elif posting_frequency >= 3:
        consistency_score = 12
    elif posting_frequency >= 1:
        consistency_score = 8
    elif posting_frequency >= 0.5:
        consistency_score = 5
    else:
        consistency_score = 0
    score += consistency_score
    
    # Verification status (0-10 points)
    # Verified = established creator, lower risk for brands
    verification_score = 10 if verified else 0
    score += verification_score
    
    # Bonus: Total likes shows historical performance (0-5 points)
    total_likes = data.get("total_likes", 0)
    if total_likes >= 100_000_000:
        bonus_score = 5
    elif total_likes >= 10_000_000:
        bonus_score = 4
    elif total_likes >= 1_000_000:
        bonus_score = 3
    elif total_likes >= 100_000:
        bonus_score = 2
    else:
        bonus_score = min(5, total_likes / 100_000)
    score += bonus_score
    
    # Determine label and color
    if score >= 85:
        label = "Ready Now"
        color = "green"
    elif score >= 70:
        label = "Almost Ready"
        color = "lime"
    elif score >= 50:
        label = "Building"
        color = "yellow"
    elif score >= 30:
        label = "Early Stage"
        color = "orange"
    else:
        label = "Not Ready"
        color = "red"
    
    return {
        "raw": min(100, max(0, int(score))),
        "label": label,
        "color": color,
    }


def compute_all_scores(data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Compute all three scores and return structured result"""
    return {
        "growth_velocity": compute_growth_velocity_score(data),
        "viral_probability": compute_viral_probability_score(data),
        "brand_deal_readiness": compute_brand_deal_readiness_score(data),
    }
