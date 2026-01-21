#!/usr/bin/env python3
"""
Analyze Reddit posts for viral content patterns.
"""

import json
import sys
from pathlib import Path
from collections import Counter
import re

def analyze_title_patterns(posts):
    """Analyze title characteristics."""
    patterns = {
        'questions': [],
        'opinions': [],
        'data_driven': [],
        'personal': [],
        'negative_emotion': [],
        'positive_emotion': [],
        'neutral': []
    }

    word_counts = []

    for post in posts:
        title = post.get('title', '')
        word_count = len(title.split())
        word_counts.append((title, word_count))

        # Classify by type
        if '?' in title:
            patterns['questions'].append(title)

        if any(word in title.lower() for word in ['my ', 'i ', "i'm", "i've"]):
            patterns['personal'].append(title)

        if any(word in title.lower() for word in ['data', 'analysis', 'study', 'research', 'statistics', 'numbers']):
            patterns['data_driven'].append(title)

        # Emotional classification
        negative_words = ['tired', 'losing', 'wrong', 'overvalued', 'warning', 'concerned', 'worried',
                         'avoid', 'danger', 'risk', 'problem', 'issue', 'fail', 'crash', 'scam']
        positive_words = ['undervalued', 'opportunity', 'best', 'top', 'great', 'excellent', 'winning']

        title_lower = title.lower()
        if any(word in title_lower for word in negative_words):
            patterns['negative_emotion'].append(title)
        elif any(word in title_lower for word in positive_words):
            patterns['positive_emotion'].append(title)
        else:
            patterns['neutral'].append(title)

    return patterns, word_counts

def analyze_engagement(posts):
    """Analyze engagement patterns."""
    engagement = []

    for post in posts:
        title = post.get('title', '')[:60]
        score = post.get('score', 0)
        comments = post.get('num_comments', 0)
        ratio = post.get('upvote_ratio', 0)

        # Calculate comment-to-upvote ratio (controversy indicator)
        comment_ratio = comments / score if score > 0 else 0

        engagement.append({
            'title': title,
            'score': score,
            'comments': comments,
            'upvote_ratio': ratio,
            'comment_ratio': comment_ratio
        })

    return engagement

def extract_topics(posts):
    """Extract common topics/themes."""
    all_text = ' '.join([
        (post.get('title', '') + ' ' + post.get('selftext', '')[:200])
        for post in posts
    ])

    # Common finance/investing terms
    keywords = ['stock', 'market', 'value', 'price', 'invest', 'buy', 'sell',
                'valuation', 'company', 'portfolio', 'dividend', 'growth',
                'china', 'tech', 'ai', 'berkshire', 'buffett', 'trump', 'tariff']

    mentions = {}
    for keyword in keywords:
        count = len(re.findall(r'\b' + keyword + r'\b', all_text.lower()))
        if count > 0:
            mentions[keyword] = count

    return dict(sorted(mentions.items(), key=lambda x: x[1], reverse=True))

def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_subreddit.py <data_file.json>")
        sys.exit(1)

    filepath = Path(sys.argv[1])

    with open(filepath, 'r') as f:
        data = json.load(f)

    posts = list(data['data']['posts'].values())
    subreddit = posts[0].get('subreddit', 'Unknown')

    print(f"\n{'='*80}")
    print(f"VIRAL CONTENT ANALYSIS: r/{subreddit}")
    print(f"{'='*80}\n")

    # Title patterns
    patterns, word_counts = analyze_title_patterns(posts)

    print("📝 TITLE CHARACTERISTICS")
    print("-" * 80)
    avg_words = sum(wc for _, wc in word_counts) / len(word_counts)
    print(f"Average title length: {avg_words:.1f} words")
    print(f"\nTitle type distribution:")
    print(f"  Questions: {len(patterns['questions'])} ({len(patterns['questions'])/len(posts)*100:.0f}%)")
    print(f"  Personal ('I'/'My'): {len(patterns['personal'])} ({len(patterns['personal'])/len(posts)*100:.0f}%)")
    print(f"  Data-driven: {len(patterns['data_driven'])} ({len(patterns['data_driven'])/len(posts)*100:.0f}%)")

    print(f"\nEmotional tone:")
    print(f"  Negative: {len(patterns['negative_emotion'])} ({len(patterns['negative_emotion'])/len(posts)*100:.0f}%)")
    print(f"  Positive: {len(patterns['positive_emotion'])} ({len(patterns['positive_emotion'])/len(posts)*100:.0f}%)")
    print(f"  Neutral: {len(patterns['neutral'])} ({len(patterns['neutral'])/len(posts)*100:.0f}%)")

    # Sample titles
    print(f"\n🔥 TOP 10 TITLES (by engagement):")
    print("-" * 80)
    for i, post in enumerate(posts[:10], 1):
        title = post.get('title', '')
        score = post.get('score', 0)
        comments = post.get('num_comments', 0)
        print(f"{i}. [{score:,}⬆️ {comments:,}💬] {title}")

    # Engagement analysis
    print(f"\n💬 ENGAGEMENT PATTERNS")
    print("-" * 80)
    engagement = analyze_engagement(posts)

    avg_score = sum(e['score'] for e in engagement) / len(engagement)
    avg_comments = sum(e['comments'] for e in engagement) / len(engagement)
    avg_ratio = sum(e['upvote_ratio'] for e in engagement) / len(engagement)

    print(f"Average upvotes: {avg_score:,.0f}")
    print(f"Average comments: {avg_comments:,.0f}")
    print(f"Average upvote ratio: {avg_ratio:.2f}")

    # Most controversial (high comment-to-upvote ratio)
    controversial = sorted(engagement, key=lambda x: x['comment_ratio'], reverse=True)[:5]
    print(f"\nMost controversial (high comment-to-upvote ratio):")
    for i, post in enumerate(controversial, 1):
        print(f"  {i}. [{post['score']:,}⬆️ {post['comments']:,}💬 ratio:{post['comment_ratio']:.2f}] {post['title']}...")

    # Topics
    print(f"\n🎯 COMMON TOPICS/THEMES")
    print("-" * 80)
    topics = extract_topics(posts)
    for topic, count in list(topics.items())[:15]:
        print(f"  {topic}: {count} mentions")

    # Sample engaging posts
    print(f"\n📊 HIGH-ENGAGEMENT EXAMPLES")
    print("-" * 80)
    print("\nQuestions that performed well:")
    for title in patterns['questions'][:3]:
        matching = [p for p in posts if p.get('title') == title]
        if matching:
            p = matching[0]
            print(f"  • [{p.get('score', 0):,}⬆️] {title}")

    print("\nOpinionated/Personal posts:")
    for title in patterns['personal'][:3]:
        matching = [p for p in posts if p.get('title') == title]
        if matching:
            p = matching[0]
            print(f"  • [{p.get('score', 0):,}⬆️] {title}")

    print("\nData-driven posts:")
    for title in patterns['data_driven'][:3]:
        matching = [p for p in posts if p.get('title') == title]
        if matching:
            p = matching[0]
            print(f"  • [{p.get('score', 0):,}⬆️] {title}")

    print(f"\n{'='*80}\n")

if __name__ == '__main__':
    main()
