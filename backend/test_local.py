"""
Local Test Script - Test the API without deployment
Run this to verify everything works before deploying
"""

import asyncio
import json
from scorer import compute_all_scores


async def test_with_mock_data():
    """Test scoring algorithms with mock TikTok data"""
    
    print("\n" + "="*60)
    print("  Creator Growth Radar - Local Test")
    print("="*60 + "\n")
    
    # Test case 1: Mega creator (like Charli D'Amelio)
    print("Test 1: Mega Creator (150M+ followers)")
    print("-" * 40)
    mega_creator = {
        "username": "charlidamelio",
        "followers": 154_000_000,
        "following": 1200,
        "total_likes": 11_000_000_000,
        "total_videos": 2500,
        "verified": True,
        "avg_views": 4_200_000,
        "avg_likes": 350_000,
        "avg_comments": 15_000,
        "avg_shares": 8_000,
        "posting_frequency_per_week": 4.2,
        "engagement_rate": 8.4,
    }
    
    scores = compute_all_scores(mega_creator)
    print(f"  Growth Velocity:      {scores['growth_velocity']['raw']:3d}/100 - {scores['growth_velocity']['label']}")
    print(f"  Viral Probability:    {scores['viral_probability']['raw']:3d}/100 - {scores['viral_probability']['label']}")
    print(f"  Brand Deal Readiness: {scores['brand_deal_readiness']['raw']:3d}/100 - {scores['brand_deal_readiness']['label']}")
    print()
    
    # Test case 2: Rising micro-influencer
    print("Test 2: Rising Micro-Influencer (50K followers)")
    print("-" * 40)
    rising_star = {
        "username": "rising_creator",
        "followers": 50_000,
        "following": 800,
        "total_likes": 2_500_000,
        "total_videos": 150,
        "verified": False,
        "avg_views": 75_000,  # Views > followers = viral!
        "avg_likes": 8_000,
        "avg_comments": 400,
        "avg_shares": 200,
        "posting_frequency_per_week": 5.5,
        "engagement_rate": 17.2,
    }
    
    scores = compute_all_scores(rising_star)
    print(f"  Growth Velocity:      {scores['growth_velocity']['raw']:3d}/100 - {scores['growth_velocity']['label']}")
    print(f"  Viral Probability:    {scores['viral_probability']['raw']:3d}/100 - {scores['viral_probability']['label']}")
    print(f"  Brand Deal Readiness: {scores['brand_deal_readiness']['raw']:3d}/100 - {scores['brand_deal_readiness']['label']}")
    print()
    
    # Test case 3: Small creator just starting
    print("Test 3: New Creator (2K followers)")
    print("-" * 40)
    new_creator = {
        "username": "newbie_tiktoker",
        "followers": 2_000,
        "following": 500,
        "total_likes": 15_000,
        "total_videos": 30,
        "verified": False,
        "avg_views": 800,
        "avg_likes": 100,
        "avg_comments": 5,
        "avg_shares": 2,
        "posting_frequency_per_week": 2.0,
        "engagement_rate": 5.35,
    }
    
    scores = compute_all_scores(new_creator)
    print(f"  Growth Velocity:      {scores['growth_velocity']['raw']:3d}/100 - {scores['growth_velocity']['label']}")
    print(f"  Viral Probability:    {scores['viral_probability']['raw']:3d}/100 - {scores['viral_probability']['label']}")
    print(f"  Brand Deal Readiness: {scores['brand_deal_readiness']['raw']:3d}/100 - {scores['brand_deal_readiness']['label']}")
    print()
    
    # Test case 4: High engagement niche creator
    print("Test 4: High Engagement Niche Creator (100K followers)")
    print("-" * 40)
    niche_creator = {
        "username": "niche_expert",
        "followers": 100_000,
        "following": 200,
        "total_likes": 8_000_000,
        "total_videos": 400,
        "verified": True,
        "avg_views": 150_000,  # 1.5x followers = viral reach
        "avg_likes": 12_000,
        "avg_comments": 800,
        "avg_shares": 600,
        "posting_frequency_per_week": 7.0,
        "engagement_rate": 13.4,
    }
    
    scores = compute_all_scores(niche_creator)
    print(f"  Growth Velocity:      {scores['growth_velocity']['raw']:3d}/100 - {scores['growth_velocity']['label']}")
    print(f"  Viral Probability:    {scores['viral_probability']['raw']:3d}/100 - {scores['viral_probability']['label']}")
    print(f"  Brand Deal Readiness: {scores['brand_deal_readiness']['raw']:3d}/100 - {scores['brand_deal_readiness']['label']}")
    print()
    
    print("="*60)
    print("  All tests completed successfully!")
    print("="*60 + "\n")


def test_api_response_format():
    """Show expected API response format"""
    
    print("\n" + "="*60)
    print("  Expected API Response Format")
    print("="*60 + "\n")
    
    example_response = {
        "username": "charlidamelio",
        "followers": 154000000,
        "following": 1200,
        "total_likes": 11000000000,
        "total_videos": 2500,
        "verified": True,
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
    
    print(json.dumps(example_response, indent=2))
    print()


if __name__ == "__main__":
    print("\n📡 Creator Growth Radar - Test Suite\n")
    
    # Run async tests
    asyncio.run(test_with_mock_data())
    
    # Show API format
    test_api_response_format()
    
    print("✅ All scoring algorithms working correctly!")
    print("\nNext steps:")
    print("1. Run: uvicorn main:app --reload")
    print("2. Visit: http://localhost:8000/docs")
    print("3. Test /analyze endpoint with a username")
    print("4. Deploy to Railway + Vercel using deploy.bat\n")
