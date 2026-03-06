#!/usr/bin/env python3
"""
Analyze Reddit comments for viral content patterns.
"""

import json
from pathlib import Path
from collections import defaultdict
import statistics

def analyze_comments_by_subreddit():
    """Analyze all fetched comments grouped by subreddit."""
    comment_dir = Path('data/reddit/comments')
    files = sorted(comment_dir.glob('*.json'))

    # Group comments by subreddit
    by_subreddit = defaultdict(list)

    for f in files:
        with open(f) as file:
            data = json.load(file)

        subreddit = data['metadata']['subreddit']

        if 'comments' in data and 'data' in data['comments']:
            comments_data = data['comments']['data']

            for key, comment in comments_data.items():
                by_subreddit[subreddit].append(comment)

    # Analyze each subreddit
    for subreddit in sorted(by_subreddit.keys()):
        print(f"\n{'='*80}")
        print(f"r/{subreddit} - COMMENT ANALYSIS")
        print(f"{'='*80}")

        comments = by_subreddit[subreddit]
        print(f"Total comments: {len(comments)}")

        analyze_comment_characteristics(comments, subreddit)

def analyze_comment_characteristics(comments, subreddit):
    """Analyze characteristics of comments."""

    # Sort by score
    sorted_comments = sorted(comments, key=lambda c: c.get('score', 0), reverse=True)

    # Length analysis
    lengths = [len(c.get('body', '').split()) for c in comments]
    avg_length = statistics.mean(lengths)
    median_length = statistics.median(lengths)

    print(f"\n📊 LENGTH STATISTICS")
    print(f"-" * 80)
    print(f"Average words: {avg_length:.1f}")
    print(f"Median words: {median_length:.0f}")
    print(f"Shortest: {min(lengths)} words")
    print(f"Longest: {max(lengths)} words")

    # Score distribution
    scores = [c.get('score', 0) for c in comments]
    avg_score = statistics.mean(scores)
    median_score = statistics.median(scores)

    print(f"\n⬆️  ENGAGEMENT STATISTICS")
    print(f"-" * 80)
    print(f"Average upvotes: {avg_score:.1f}")
    print(f"Median upvotes: {median_score:.0f}")
    print(f"Highest: {max(scores)} upvotes")
    print(f"Lowest: {min(scores)} upvotes")

    # Top comments
    print(f"\n🔥 TOP 10 COMMENTS")
    print(f"-" * 80)
    for i, comment in enumerate(sorted_comments[:10], 1):
        score = comment.get('score', 0)
        body = comment.get('body', '')
        words = len(body.split())

        # Truncate body for display
        preview = body[:100].replace('\n', ' ')
        if len(body) > 100:
            preview += "..."

        print(f"{i}. [{score}⬆️ | {words}w] {preview}")

    # Comment types analysis
    print(f"\n📝 COMMENT TYPE PATTERNS")
    print(f"-" * 80)

    types = {
        'questions': 0,
        'agreements': 0,
        'disagreements': 0,
        'data_driven': 0,
        'personal_experience': 0,
        'humor': 0,
        'short_pithy': 0
    }

    for comment in comments:
        body = comment.get('body', '').lower()

        if '?' in body:
            types['questions'] += 1

        if any(word in body for word in ['agree', 'exactly', 'this', 'correct', 'yes']):
            types['agreements'] += 1

        if any(word in body for word in ['disagree', 'wrong', 'incorrect', 'no', 'but', 'however', 'actually']):
            types['disagreements'] += 1

        if any(word in body for word in ['data', 'research', 'study', 'statistics', '%']):
            types['data_driven'] += 1

        if any(word in body for word in [' i ', "i'm", "i've", ' my ', 'me ']):
            types['personal_experience'] += 1

        if any(word in body for word in ['lol', 'lmao', 'haha', '😂', '🤣']):
            types['humor'] += 1

        if len(body.split()) <= 10:
            types['short_pithy'] += 1

    for ctype, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
        pct = (count / len(comments)) * 100
        print(f"  {ctype.replace('_', ' ').title()}: {count} ({pct:.0f}%)")

    # Relationship to parent
    print(f"\n🔗 COMMENT DEPTH ANALYSIS")
    print(f"-" * 80)

    depths = defaultdict(int)
    for comment in comments:
        parent_id = comment.get('parent_id', '')
        if parent_id.startswith('t3_'):  # Direct reply to post
            depths['direct_replies'] += 1
        elif parent_id.startswith('t1_'):  # Reply to comment
            depths['nested_replies'] += 1

    for depth_type, count in depths.items():
        pct = (count / len(comments)) * 100
        print(f"  {depth_type.replace('_', ' ').title()}: {count} ({pct:.0f}%)")

def main():
    print(f"{'='*80}")
    print("REDDIT COMMENT ANALYSIS - Viral Pattern Identification")
    print(f"{'='*80}")

    analyze_comments_by_subreddit()

    print(f"\n{'='*80}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    main()
