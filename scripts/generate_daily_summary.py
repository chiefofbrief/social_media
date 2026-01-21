#!/usr/bin/env python3
"""
Generate daily summary of top Reddit posts.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def load_posts_from_directory(data_dir):
    """Load all posts from JSON files in directory."""
    data_path = Path(data_dir)
    all_posts = []

    for json_file in data_path.glob('*.json'):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)

            if data.get('success') and 'posts' in data.get('data', {}):
                posts = list(data['data']['posts'].values())
                for post in posts:
                    all_posts.append(post)
        except Exception as e:
            print(f"Error loading {json_file}: {e}", file=sys.stderr)

    return all_posts

def generate_summary(posts, output_file, max_posts=20):
    """Generate markdown summary of top posts."""
    # Sort by score (upvotes)
    posts.sort(key=lambda p: p.get('score', 0), reverse=True)

    # Take top N
    top_posts = posts[:max_posts]

    # Generate markdown
    with open(output_file, 'w') as f:
        f.write(f"# Daily Reddit Top Posts\n\n")
        f.write(f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n\n")
        f.write(f"**Total posts analyzed:** {len(posts)}\n")
        f.write(f"**Top posts shown:** {len(top_posts)}\n\n")
        f.write("---\n\n")

        for i, post in enumerate(top_posts, 1):
            subreddit = post.get('subreddit', 'Unknown')
            title = post.get('title', 'No title')
            score = post.get('score', 0)
            num_comments = post.get('num_comments', 0)
            url = post.get('url', '')
            selftext = post.get('selftext', '')

            f.write(f"## {i}. r/{subreddit} - {title}\n\n")
            f.write(f"**Upvotes:** {score:,} | **Comments:** {num_comments:,}\n\n")

            if selftext:
                # Truncate long posts
                if len(selftext) > 500:
                    selftext = selftext[:500] + "..."
                f.write(f"**Body:**\n```\n{selftext}\n```\n\n")
            else:
                f.write("*Link post (no body text)*\n\n")

            f.write(f"**URL:** {url}\n\n")
            f.write("---\n\n")

    print(f"✓ Summary generated: {output_file}")
    print(f"  Top posts: {len(top_posts)}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_daily_summary.py <data_directory>")
        sys.exit(1)

    data_dir = sys.argv[1]
    output_file = Path(data_dir) / 'daily_summary.md'

    # Load posts
    posts = load_posts_from_directory(data_dir)

    if not posts:
        print("No posts found!", file=sys.stderr)
        sys.exit(1)

    # Generate summary
    generate_summary(posts, output_file)

if __name__ == '__main__':
    main()
