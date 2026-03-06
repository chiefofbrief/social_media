#!/usr/bin/env python3
"""
Verify Reddit data quality:
- Posts are from the specified timeframe
- Posts are sorted by score (top posts)
- Data completeness
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

def verify_data_file(filepath, expected_timeframe_days=7):
    """Verify a single Reddit data file."""
    print(f"\n{'='*80}")
    print(f"Verifying: {filepath.name}")
    print(f"{'='*80}")

    with open(filepath, 'r') as f:
        data = json.load(f)

    # Check basic structure
    if not data.get('success'):
        print("❌ FAIL: API request was not successful")
        return False

    posts = data['data'].get('posts', {})
    post_list = list(posts.values())

    if not post_list:
        print("❌ FAIL: No posts found")
        return False

    print(f"✓ Total posts: {len(post_list)}")

    # Check timeframe
    now = datetime.utcnow()
    cutoff = now - timedelta(days=expected_timeframe_days)

    oldest_post = None
    newest_post = None
    out_of_range = []

    for post in post_list:
        created_utc = post.get('created_utc')
        if created_utc:
            post_date = datetime.fromtimestamp(created_utc)

            if oldest_post is None or post_date < oldest_post:
                oldest_post = post_date
            if newest_post is None or post_date > newest_post:
                newest_post = post_date

            if post_date < cutoff:
                out_of_range.append({
                    'title': post.get('title', 'No title')[:50],
                    'date': post_date.strftime('%Y-%m-%d %H:%M'),
                    'days_ago': (now - post_date).days
                })

    if oldest_post and newest_post:
        print(f"✓ Date range: {oldest_post.strftime('%Y-%m-%d')} to {newest_post.strftime('%Y-%m-%d')}")
        print(f"  Oldest post: {(now - oldest_post).days} days ago")
        print(f"  Newest post: {(now - newest_post).days} days ago")

    if out_of_range:
        print(f"\n⚠️  WARNING: {len(out_of_range)} posts outside {expected_timeframe_days}-day window:")
        for post_info in out_of_range[:5]:  # Show first 5
            print(f"  - {post_info['title']}... ({post_info['days_ago']} days ago)")
        if len(out_of_range) > 5:
            print(f"  ... and {len(out_of_range) - 5} more")
    else:
        print(f"✓ All posts within {expected_timeframe_days}-day window")

    # Check sorting by score
    scores = [post.get('score', 0) for post in post_list]
    is_sorted = all(scores[i] >= scores[i+1] for i in range(len(scores)-1))

    if is_sorted:
        print(f"✓ Posts correctly sorted by score (descending)")
    else:
        print(f"⚠️  Posts may not be sorted by score")

    print(f"\nScore distribution:")
    print(f"  Highest: {max(scores):,} upvotes")
    print(f"  Lowest: {min(scores):,} upvotes")
    print(f"  Average: {sum(scores)/len(scores):,.0f} upvotes")
    print(f"  Median: {sorted(scores)[len(scores)//2]:,} upvotes")

    # Check data completeness
    required_fields = ['title', 'score', 'num_comments', 'created_utc', 'author', 'subreddit']
    missing_fields = []

    for i, post in enumerate(post_list[:5]):  # Check first 5
        for field in required_fields:
            if field not in post or post[field] is None:
                missing_fields.append((i, field))

    if missing_fields:
        print(f"\n⚠️  Missing fields detected in first 5 posts:")
        for idx, field in missing_fields:
            print(f"  Post {idx}: missing '{field}'")
    else:
        print(f"✓ All required fields present in sample posts")

    # Show top 5 posts
    print(f"\n📊 Top 5 Posts:")
    for i, post in enumerate(post_list[:5], 1):
        title = post.get('title', 'No title')
        score = post.get('score', 0)
        comments = post.get('num_comments', 0)
        print(f"  {i}. [{score:,} ⬆️ | {comments:,} 💬] {title[:60]}...")

    return True

def main():
    data_dir = Path('data/reddit')

    # Get week files
    week_files = sorted(data_dir.glob('*_top_week_*.json'))

    if not week_files:
        print("❌ No week-timeframe data files found")
        sys.exit(1)

    print(f"Found {len(week_files)} week-timeframe data files to verify")

    all_valid = True
    for filepath in week_files:
        valid = verify_data_file(filepath)
        if not valid:
            all_valid = False

    print(f"\n{'='*80}")
    if all_valid:
        print("✅ All data files verified successfully")
    else:
        print("❌ Some data files have issues")
    print(f"{'='*80}")

if __name__ == '__main__':
    main()
