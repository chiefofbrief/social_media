#!/usr/bin/env python3
"""
Fetch comments from a Reddit post using SociaVault API.

Usage:
    python fetch_reddit_comments.py --url <post_url> [--amount 5] [--trim]
"""

import requests
import json
import argparse
import os
from datetime import datetime
from pathlib import Path

# API configuration
API_KEY = os.getenv('SOCIAVAULT_API_KEY')
if not API_KEY:
    raise ValueError("SOCIAVAULT_API_KEY environment variable not set")

BASE_URL = "https://api.sociavault.com"
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def check_credits():
    """Check available API credits."""
    url = f"{BASE_URL}/v1/account/credits"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        data = response.json()
        credits = data.get('credits', 0)
        print(f"Available credits: {credits}")
        return credits
    else:
        print(f"Warning: Could not check credits (status {response.status_code})")
        return None

def fetch_comments(post_url, amount=5, trim=False):
    """
    Fetch comments from a Reddit post.

    Args:
        post_url: Full URL to Reddit post
        amount: Number of comments to fetch (default: 5)
        trim: Use trimmed response format (default: False)

    Returns:
        dict with 'success', 'data', 'cost'
    """
    url = f"{BASE_URL}/v1/scrape/reddit/post/comments/simple"

    params = {
        "url": post_url,
        "amount": amount,
        "trim": str(trim).lower()
    }

    print(f"\nFetching {amount} comments from post...")
    print(f"URL: {post_url}")
    print(f"Parameters: amount={amount}, trim={trim}")

    response = requests.get(url, headers=HEADERS, params=params)

    if response.status_code == 200:
        comments = response.json()

        # Calculate cost (1 credit per 48 items, minimum 1)
        # For amounts <= 48, cost is 1 credit
        cost = max(1, -(-amount // 48))  # Ceiling division

        return {
            'success': True,
            'data': comments,
            'cost': cost,
            'count': len(comments) if isinstance(comments, list) else 0
        }
    else:
        error_msg = response.json() if response.headers.get('content-type') == 'application/json' else response.text
        return {
            'success': False,
            'error': error_msg,
            'status_code': response.status_code
        }

def extract_post_id(url):
    """Extract post ID from Reddit URL."""
    # URL format: https://www.reddit.com/r/subreddit/comments/POST_ID/title/
    parts = url.split('/')
    if 'comments' in parts:
        idx = parts.index('comments')
        if idx + 1 < len(parts):
            return parts[idx + 1]
    return None

def save_comments(comments, post_url, subreddit=None):
    """Save comments to JSON file."""
    # Create data directory
    data_dir = Path('data/reddit/comments')
    data_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename
    post_id = extract_post_id(post_url)
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    if subreddit:
        filename = f"{subreddit}_{post_id}_{timestamp}.json"
    else:
        filename = f"post_{post_id}_{timestamp}.json"

    filepath = data_dir / filename

    # Save with metadata
    output = {
        'success': True,
        'metadata': {
            'post_url': post_url,
            'post_id': post_id,
            'subreddit': subreddit,
            'fetched_at': timestamp,
            'comment_count': len(comments)
        },
        'comments': comments
    }

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    return filepath

def main():
    parser = argparse.ArgumentParser(description='Fetch comments from a Reddit post')
    parser.add_argument('--url', required=True, help='Reddit post URL')
    parser.add_argument('--amount', type=int, default=5, help='Number of comments to fetch (default: 5)')
    parser.add_argument('--trim', action='store_true', help='Use trimmed response format')
    parser.add_argument('--subreddit', help='Subreddit name (for filename)')

    args = parser.parse_args()

    # Check credits
    print("Checking API credits...")
    check_credits()

    # Fetch comments
    result = fetch_comments(args.url, amount=args.amount, trim=args.trim)

    if result['success']:
        # Save to file
        filepath = save_comments(result['data'], args.url, args.subreddit)

        print(f"\n✓ Successfully fetched {result['count']} comments")
        print(f"✓ Saved to: {filepath}")
        print(f"✓ Cost: {result['cost']} API credit(s)")

        # Show top 3 comments preview
        if result['count'] > 0:
            print(f"\n📊 Top 3 Comments Preview:")
            for i, comment in enumerate(result['data'][:3], 1):
                if args.trim and isinstance(comment, dict):
                    score = comment.get('score', comment.get('ups', 0))
                    body = comment.get('body', '')[:80]
                    author = comment.get('author', 'unknown')
                    print(f"  {i}. [{score}⬆️] @{author}: {body}...")
                else:
                    print(f"  {i}. {str(comment)[:100]}...")
    else:
        print(f"\n❌ Failed to fetch comments")
        print(f"Status: {result.get('status_code', 'unknown')}")
        print(f"Error: {result.get('error', 'unknown')}")
        return 1

    return 0

if __name__ == '__main__':
    exit(main())
