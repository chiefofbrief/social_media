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

def generate_summary(posts, output_file, posts_per_subreddit=10):
    """Generate markdown summary with separate sections per subreddit."""
    from collections import defaultdict

    # Group posts by subreddit
    posts_by_subreddit = defaultdict(list)
    for post in posts:
        subreddit = post.get('subreddit', 'Unknown')
        posts_by_subreddit[subreddit].append(post)

    # Sort posts within each subreddit by score
    for subreddit in posts_by_subreddit:
        posts_by_subreddit[subreddit].sort(key=lambda p: p.get('score', 0), reverse=True)

    # Generate markdown
    total_posts_shown = 0

    with open(output_file, 'w') as f:
        f.write(f"# Daily Reddit Top Posts\n\n")
        f.write(f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n\n")
        f.write(f"**Total posts analyzed:** {len(posts)}\n")
        f.write(f"**Subreddits:** {', '.join(sorted(posts_by_subreddit.keys()))}\n\n")
        f.write("---\n\n")

        # Write each subreddit section
        for subreddit in sorted(posts_by_subreddit.keys()):
            subreddit_posts = posts_by_subreddit[subreddit]

            # Take top N posts (or all if fewer than N)
            top_posts = subreddit_posts[:posts_per_subreddit]
            total_posts_shown += len(top_posts)

            f.write(f"# r/{subreddit}\n\n")
            f.write(f"**Showing top {len(top_posts)} of {len(subreddit_posts)} posts**\n\n")
            f.write("---\n\n")

            for i, post in enumerate(top_posts, 1):
                title = post.get('title', 'No title')
                score = post.get('score', 0)
                num_comments = post.get('num_comments', 0)
                url = post.get('url', '')
                selftext = post.get('selftext', '')

                f.write(f"## {i}. {title}\n\n")
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

            f.write("\n")  # Extra space between subreddit sections

    print(f"✓ Summary generated: {output_file}")
    print(f"  Subreddits: {len(posts_by_subreddit)}")
    print(f"  Total posts shown: {total_posts_shown}")
    for subreddit in sorted(posts_by_subreddit.keys()):
        count = min(len(posts_by_subreddit[subreddit]), posts_per_subreddit)
        print(f"    r/{subreddit}: {count} posts")

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
