#!/usr/bin/env python3
"""
Quick test script to evaluate Threads search for stock research
Tests AMZN with different query formats
"""

import os
import requests
from datetime import datetime, timedelta
import json

API_KEY = os.getenv('SOCIAVAULT_API_KEY')
if not API_KEY:
    raise ValueError("SOCIAVAULT_API_KEY environment variable not set")

BASE_URL = "https://api.sociavault.com/v1/scrape/threads/search"

def search_threads(query, trim=False):
    """Search Threads for a specific query"""
    headers = {
        'X-API-Key': API_KEY
    }
    params = {
        'query': query,
        'trim': str(trim).lower()
    }

    print(f"\n{'='*80}")
    print(f"Searching Threads for: '{query}'")
    print(f"{'='*80}")

    response = requests.get(BASE_URL, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    if not data.get('success'):
        print(f"❌ Search failed")
        return None

    posts = data.get('posts', [])
    print(f"📊 Found {len(posts)} posts")

    if not posts:
        print("No posts found for this query")
        return data

    # Analyze the posts
    now = datetime.now()
    one_month_ago = now - timedelta(days=30)

    recent_posts = []
    stock_related = []

    print(f"\n📝 Post Analysis:")
    print(f"{'─'*80}")

    for i, post in enumerate(posts[:10], 1):  # Show first 10
        taken_at = datetime.fromtimestamp(post['taken_at'])
        username = post['user']['username']
        is_verified = post['user']['is_verified']

        caption_text = ""
        if post.get('caption'):
            caption_text = post['caption'].get('text', '')

        like_count = post.get('like_count', 0)

        # Check if from last month
        is_recent = taken_at > one_month_ago
        if is_recent:
            recent_posts.append(post)

        # Basic check for stock-related content
        stock_keywords = ['stock', 'share', 'trading', 'invest', 'earnings', 'bull', 'bear', 'buy', 'sell']
        is_stock_related = any(keyword in caption_text.lower() for keyword in stock_keywords)
        if is_stock_related:
            stock_related.append(post)

        age_str = "📅 RECENT" if is_recent else f"⏰ {(now - taken_at).days} days old"
        verified_str = "✓" if is_verified else ""
        stock_str = "📈 STOCK" if is_stock_related else ""

        print(f"\n{i}. @{username}{verified_str} | {age_str} {stock_str}")
        print(f"   👍 {like_count:,} likes")
        print(f"   🕐 {taken_at.strftime('%Y-%m-%d %H:%M')}")
        print(f"   📄 {caption_text[:150]}{'...' if len(caption_text) > 150 else ''}")

    print(f"\n{'─'*80}")
    print(f"📊 Summary:")
    print(f"   Total posts: {len(posts)}")
    print(f"   From last 30 days: {len(recent_posts)}")
    print(f"   Stock-related keywords: {len(stock_related)}")

    if len(posts) > 0:
        oldest_post = min(posts, key=lambda p: p['taken_at'])
        newest_post = max(posts, key=lambda p: p['taken_at'])
        oldest_date = datetime.fromtimestamp(oldest_post['taken_at'])
        newest_date = datetime.fromtimestamp(newest_post['taken_at'])
        print(f"   Date range: {oldest_date.strftime('%Y-%m-%d')} to {newest_date.strftime('%Y-%m-%d')}")
        print(f"   Avg likes: {sum(p.get('like_count', 0) for p in posts) / len(posts):.0f}")

    return data

def main():
    """Test different query formats for AMZN"""

    queries = [
        "AMZN",
        "$AMZN",
        "Amazon stock",
        "AMZN earnings"
    ]

    results = {}

    for query in queries:
        try:
            data = search_threads(query)
            results[query] = data
        except Exception as e:
            print(f"❌ Error searching '{query}': {e}")
            results[query] = None

    print(f"\n\n{'='*80}")
    print("🎯 OVERALL ASSESSMENT")
    print(f"{'='*80}")

    total_posts = sum(len(r.get('posts', [])) if r else 0 for r in results.values())
    print(f"\nTotal posts across all queries: {total_posts}")

    if total_posts == 0:
        print("\n❌ VERDICT: Threads search returned NO results for AMZN")
        print("   Recommendation: Skip Threads, focus on YouTube instead")
    elif total_posts < 50:
        print(f"\n⚠️  VERDICT: Limited results ({total_posts} posts)")
        print("   Threads may not have enough stock discussion yet")
        print("   Recommendation: Focus on YouTube which has more finance content")
    else:
        print(f"\n✅ VERDICT: Good results ({total_posts} posts)")
        print("   Threads could be useful for stock research")

    # Save full results to file
    output_file = "/home/user/social_media/data/threads_amzn_test.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Full results saved to: {output_file}")

if __name__ == "__main__":
    main()
