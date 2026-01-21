#!/usr/bin/env python3
"""
Fetch top Reddit posts from a subreddit using SociaVault API.

This script fetches top posts from a specified subreddit and saves
the raw JSON response to data/reddit/ directory for later analysis.

Usage:
    python fetch_reddit_posts.py --subreddit ValueInvesting --timeframe month

Environment Variables:
    SOCIAVAULT_API_KEY: Your SociaVault API key
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Dict, List, Any
import requests


class SociaVaultClient:
    """Client for interacting with SociaVault Reddit API."""

    BASE_URL = "https://api.sociavault.com/v1"

    def __init__(self, api_key: str):
        """Initialize client with API key."""
        self.api_key = api_key
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }

    def check_credits(self) -> Dict[str, Any]:
        """Check available API credits (costs 0 credits)."""
        response = requests.get(
            f"{self.BASE_URL}/credits",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def fetch_subreddit_posts(
        self,
        subreddit: str,
        timeframe: str = "month",
        sort: str = "top",
        trim: bool = False
    ) -> Dict[str, Any]:
        """
        Fetch posts from a subreddit.

        Args:
            subreddit: Subreddit name (without r/ prefix)
            timeframe: Time period (hour, day, week, month, year, all)
            sort: Sort method (top, new, hot, rising, controversial)
            trim: If True, returns trimmed response (faster, less data)

        Returns:
            API response as dictionary (typically ~25 posts per page)
        """
        params = {
            "subreddit": subreddit,
            "timeframe": timeframe,
            "sort": sort,
            "trim": trim
        }

        response = requests.get(
            f"{self.BASE_URL}/scrape/reddit/subreddit",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()


def save_raw_data(data: Dict[str, Any], subreddit: str, timeframe: str, sort: str, output_dir: str = "data/reddit") -> str:
    """Save raw API response to JSON file."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{output_dir}/{subreddit}_{sort}_{timeframe}_{timestamp}.json"

    os.makedirs(output_dir, exist_ok=True)

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return filename




def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Fetch top Reddit posts using SociaVault API"
    )
    parser.add_argument(
        "--subreddit",
        required=True,
        help="Subreddit name (without r/ prefix)"
    )
    parser.add_argument(
        "--timeframe",
        default="month",
        choices=["hour", "day", "week", "month", "year", "all"],
        help="Time period to fetch posts from (default: month)"
    )
    parser.add_argument(
        "--sort",
        default="top",
        choices=["top", "new", "hot", "rising", "controversial"],
        help="Sort method (default: top)"
    )
    parser.add_argument(
        "--trim",
        action="store_true",
        help="Use trimmed response (faster, less data)"
    )
    parser.add_argument(
        "--output-dir",
        default="data/reddit",
        help="Output directory for JSON files (default: data/reddit)"
    )

    args = parser.parse_args()

    # Get API key from environment
    api_key = os.getenv("SOCIAVAULT_API_KEY")
    if not api_key:
        print("Error: SOCIAVAULT_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    try:
        # Initialize client
        client = SociaVaultClient(api_key)

        # Check credits first (0 cost)
        print("Checking API credits...")
        credits_info = client.check_credits()
        print(f"Available credits: {credits_info.get('credits', 'unknown')}")

        # Fetch posts
        print(f"\nFetching posts from r/{args.subreddit}...")
        print(f"Parameters: timeframe={args.timeframe}, sort={args.sort}, trim={args.trim}")

        data = client.fetch_subreddit_posts(
            subreddit=args.subreddit,
            timeframe=args.timeframe,
            sort=args.sort,
            trim=args.trim
        )

        # Save raw data
        json_file = save_raw_data(data, args.subreddit, args.timeframe, args.sort, args.output_dir)
        print(f"\n✓ Raw data saved to: {json_file}")

        # Get actual post count from nested structure
        posts_dict = data.get('data', {}).get('posts', {})
        post_count = len(posts_dict) if isinstance(posts_dict, dict) else 0

        print(f"✓ Successfully fetched {post_count} posts")
        print(f"✓ Cost: 1 API credit")
        print(f"\nRaw JSON contains full post data including titles and body text.")

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}", file=sys.stderr)
        if e.response.status_code == 402:
            print("Insufficient credits. Please check your SociaVault account.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
