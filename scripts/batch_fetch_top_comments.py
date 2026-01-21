#!/usr/bin/env python3
"""
Batch fetch comments from top posts across multiple subreddits.
Identifies top posts by total engagement (upvotes + comments).
"""

import json
import sys
import argparse
from pathlib import Path
import subprocess
import time

def get_top_posts(data_file, top_n=5):
    """Get top N posts from a subreddit data file by total engagement."""
    with open(data_file, 'r') as f:
        data = json.load(f)

    posts = list(data['data']['posts'].values())

    # Calculate total engagement (upvotes + comments)
    for post in posts:
        post['total_engagement'] = post.get('score', 0) + post.get('num_comments', 0)

    # Sort by total engagement
    posts.sort(key=lambda p: p['total_engagement'], reverse=True)

    return posts[:top_n]

def main():
    parser = argparse.ArgumentParser(description='Batch fetch comments from top Reddit posts')
    parser.add_argument('--yes', '-y', action='store_true', help='Skip confirmation prompt')
    args = parser.parse_args()

    # Define data files for each subreddit
    data_files = {
        'ValueInvesting': 'data/reddit/ValueInvesting_top_week_2026-01-21_00-36-56.json',
        'stocks': 'data/reddit/stocks_top_week_2026-01-21_00-37-07.json',
        'options': 'data/reddit/options_top_week_2026-01-21_00-37-19.json'
    }

    all_posts = []

    print("="*80)
    print("BATCH COMMENT FETCHING - Top 5 Posts per Subreddit")
    print("="*80)

    # Collect top posts from each subreddit
    for subreddit, filepath in data_files.items():
        print(f"\n📊 Analyzing r/{subreddit}...")
        top_posts = get_top_posts(filepath, top_n=5)

        print(f"Top 5 posts by engagement:")
        for i, post in enumerate(top_posts, 1):
            title = post.get('title', '')[:60]
            score = post.get('score', 0)
            comments = post.get('num_comments', 0)
            engagement = post['total_engagement']
            url = post.get('url', '')

            print(f"  {i}. [{score:,}⬆️ {comments:,}💬 = {engagement:,}] {title}...")

            all_posts.append({
                'subreddit': subreddit,
                'url': url,
                'title': title,
                'score': score,
                'comments': comments,
                'engagement': engagement
            })

    # Summary
    print(f"\n{'='*80}")
    print(f"Total posts to process: {len(all_posts)}")
    print(f"Comments per post: 5")
    print(f"Total comments to fetch: {len(all_posts) * 5}")
    print(f"Estimated cost: {len(all_posts)} credits (1 credit per post, 5 comments < 48 items)")
    print(f"{'='*80}\n")

    if not args.yes:
        proceed = input("Proceed with fetching? (yes/no): ")
        if proceed.lower() != 'yes':
            print("Aborted.")
            return 1
    else:
        print("Auto-proceeding (--yes flag set)...")

    # Fetch comments for each post
    success_count = 0
    failed_posts = []

    for i, post_info in enumerate(all_posts, 1):
        print(f"\n[{i}/{len(all_posts)}] Processing r/{post_info['subreddit']}: {post_info['title'][:50]}...")

        cmd = [
            'python', 'scripts/fetch_reddit_comments.py',
            '--url', post_info['url'],
            '--amount', '5',
            '--trim',
            '--subreddit', post_info['subreddit']
        ]

        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(result.stdout)
            success_count += 1

            # Rate limiting - small delay between requests
            if i < len(all_posts):
                time.sleep(1)

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to fetch comments")
            print(e.stderr)
            failed_posts.append(post_info['subreddit'] + ": " + post_info['title'][:30])

    # Final summary
    print(f"\n{'='*80}")
    print(f"BATCH PROCESSING COMPLETE")
    print(f"{'='*80}")
    print(f"✓ Successful: {success_count}/{len(all_posts)}")
    if failed_posts:
        print(f"✗ Failed: {len(failed_posts)}")
        for failed in failed_posts:
            print(f"  - {failed}")
    print(f"Total credits used: ~{success_count}")
    print(f"{'='*80}\n")

    return 0 if len(failed_posts) == 0 else 1

if __name__ == '__main__':
    exit(main())
