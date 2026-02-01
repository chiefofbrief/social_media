#!/usr/bin/env python3
"""
YouTube Stock Research Script

Searches YouTube for videos about a specific stock ticker or company,
retrieves video details including transcripts, and analyzes sentiment.

Usage:
    python youtube_stock_research.py TICKER [options]

Examples:
    python youtube_stock_research.py TSLA
    python youtube_stock_research.py AMZN --query "Amazon earnings" --time-period this_week
    python youtube_stock_research.py NVDA --max-videos 50 --include-comments
"""

import os
import sys
import argparse
import requests
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

API_KEY = os.getenv('SOCIAVAULT_API_KEY')
if not API_KEY:
    raise ValueError("SOCIAVAULT_API_KEY environment variable not set")

BASE_URL = "https://api.sociavault.com/v1/scrape/youtube"


class YouTubeStockResearch:
    """YouTube stock research tool"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {'X-API-Key': api_key}

    def search_videos(
        self,
        query: str,
        upload_date: Optional[str] = None,
        sort_by: str = "relevance",
        max_videos: int = 20,
        include_extras: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search YouTube for videos matching query

        Args:
            query: Search query (e.g., "TSLA stock", "$AMZN earnings")
            upload_date: Filter by upload date (last_hour, today, this_week, this_month, this_year)
            sort_by: Sort by relevance or upload_date
            max_videos: Maximum number of videos to fetch
            include_extras: Get like/comment counts in search results

        Returns:
            List of video objects
        """
        url = f"{BASE_URL}/search"

        params = {
            'query': query,
            'sortBy': sort_by,
            'includeExtras': str(include_extras).lower()
        }

        if upload_date:
            params['uploadDate'] = upload_date

        all_videos = []
        continuation_token = None

        print(f"🔍 Searching YouTube for: '{query}'")
        if upload_date:
            print(f"📅 Time filter: {upload_date}")
        print(f"📊 Fetching up to {max_videos} videos...")

        while len(all_videos) < max_videos:
            if continuation_token:
                params['continuationToken'] = continuation_token

            try:
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                result = response.json()

                # Handle nested data structure
                if not result.get('success'):
                    print(f"❌ API returned error: {result.get('error', 'Unknown error')}")
                    break

                data = result.get('data', {})
                videos_dict = data.get('videos', {})

                # Convert videos object to list
                videos = list(videos_dict.values()) if isinstance(videos_dict, dict) else videos_dict

                if not videos:
                    break

                all_videos.extend(videos)
                print(f"   Found {len(all_videos)} videos so far...")

                continuation_token = data.get('continuationToken')
                if not continuation_token:
                    break

            except Exception as e:
                print(f"❌ Error searching: {e}")
                break

        result = all_videos[:max_videos]
        print(f"✅ Retrieved {len(result)} videos\n")
        return result

    def get_video_details(self, video_url: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a video including transcript

        Args:
            video_url: YouTube video URL

        Returns:
            Video details dictionary or None if error
        """
        url = f"{BASE_URL}/video"
        params = {'url': video_url}

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            result = response.json()

            # Handle nested data structure
            if not result.get('success'):
                return None

            return result.get('data', {})
        except Exception as e:
            print(f"⚠️  Error getting details for {video_url}: {e}")
            return None

    def analyze_video_sentiment(self, video: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze sentiment in video title, description, and transcript

        Args:
            video: Video details dictionary

        Returns:
            Sentiment analysis results
        """
        # Keywords for sentiment analysis
        bullish_keywords = [
            'buy', 'bull', 'bullish', 'long', 'growth', 'profit', 'gain',
            'opportunity', 'breakout', 'rally', 'surge', 'moon', 'rocket',
            'upgrade', 'beat', 'outperform', 'strong', 'positive'
        ]

        bearish_keywords = [
            'sell', 'bear', 'bearish', 'short', 'decline', 'loss', 'crash',
            'risk', 'warning', 'downgrade', 'miss', 'weak', 'negative',
            'overvalued', 'bubble', 'correction', 'downturn'
        ]

        # Combine all text for analysis
        title = (video.get('title') or '').lower()
        description = (video.get('description') or '').lower()
        transcript = (video.get('transcript_only_text') or '').lower()

        all_text = f"{title} {description} {transcript}"

        # Count sentiment keywords
        bullish_count = sum(1 for keyword in bullish_keywords if keyword in all_text)
        bearish_count = sum(1 for keyword in bearish_keywords if keyword in all_text)

        # Determine sentiment
        if bullish_count > bearish_count:
            sentiment = "bullish"
            confidence = bullish_count / (bullish_count + bearish_count) if (bullish_count + bearish_count) > 0 else 0
        elif bearish_count > bullish_count:
            sentiment = "bearish"
            confidence = bearish_count / (bullish_count + bearish_count) if (bullish_count + bearish_count) > 0 else 0
        else:
            sentiment = "neutral"
            confidence = 0.5

        return {
            'sentiment': sentiment,
            'confidence': round(confidence, 2),
            'bullish_signals': bullish_count,
            'bearish_signals': bearish_count,
            'has_transcript': len(transcript) > 0
        }

    def research_stock(
        self,
        ticker: str,
        custom_query: Optional[str] = None,
        time_period: str = "this_month",
        max_videos: int = 20,
        include_details: bool = True
    ) -> Dict[str, Any]:
        """
        Research a stock ticker on YouTube

        Args:
            ticker: Stock ticker symbol (e.g., "TSLA", "AMZN")
            custom_query: Custom search query (overrides default ticker search)
            time_period: Time filter for videos
            max_videos: Maximum videos to analyze
            include_details: Whether to fetch full video details + transcripts

        Returns:
            Research results dictionary
        """
        # Build search query
        if custom_query:
            query = custom_query
        else:
            # Search for multiple formats: ticker, $ticker, ticker stock
            query = f"{ticker} stock"

        # Search for videos
        videos = self.search_videos(
            query=query,
            upload_date=time_period if time_period != "all_time" else None,
            max_videos=max_videos
        )

        if not videos:
            print(f"❌ No videos found for '{query}'")
            return {
                'ticker': ticker,
                'query': query,
                'time_period': time_period,
                'timestamp': datetime.now().isoformat(),
                'videos': [],
                'summary': {'total_videos': 0}
            }

        # Enrich with video details if requested
        enriched_videos = []

        if include_details:
            print(f"📹 Fetching details for {len(videos)} videos...")
            for i, video in enumerate(videos, 1):
                video_url = video.get('url')
                if not video_url:
                    continue

                print(f"   [{i}/{len(videos)}] {video.get('title', 'Unknown')[:60]}...")

                details = self.get_video_details(video_url)
                if details:
                    # Merge search result with detailed info
                    enriched = {**video, **details}

                    # Add sentiment analysis
                    sentiment = self.analyze_video_sentiment(enriched)
                    enriched['sentiment_analysis'] = sentiment

                    enriched_videos.append(enriched)
                else:
                    # Keep original if details fetch failed
                    enriched_videos.append(video)
        else:
            enriched_videos = videos

        # Generate summary statistics
        summary = self._generate_summary(enriched_videos, include_details)

        print(f"\n✅ Research complete!")
        print(f"   Total videos: {summary['total_videos']}")
        print(f"   Total views: {summary['total_views']:,}")
        if include_details:
            print(f"   Sentiment: {summary['sentiment_breakdown']}")

        return {
            'ticker': ticker,
            'query': query,
            'time_period': time_period,
            'timestamp': datetime.now().isoformat(),
            'videos': enriched_videos,
            'summary': summary
        }

    def _generate_summary(self, videos: List[Dict[str, Any]], include_sentiment: bool = True) -> Dict[str, Any]:
        """Generate summary statistics from videos"""
        total_views = sum((v.get('viewCountInt') or 0) for v in videos)
        total_likes = sum((v.get('likeCountInt') or 0) for v in videos)
        total_comments = sum((v.get('commentCountInt') or 0) for v in videos)

        summary = {
            'total_videos': len(videos),
            'total_views': total_views,
            'total_likes': total_likes,
            'total_comments': total_comments,
            'avg_views': int(total_views / len(videos)) if videos else 0,
            'avg_likes': int(total_likes / len(videos)) if videos else 0,
        }

        if include_sentiment and videos:
            sentiments = [v.get('sentiment_analysis', {}).get('sentiment', 'neutral') for v in videos]
            summary['sentiment_breakdown'] = {
                'bullish': sentiments.count('bullish'),
                'bearish': sentiments.count('bearish'),
                'neutral': sentiments.count('neutral')
            }

            # Dominant sentiment
            if summary['sentiment_breakdown']['bullish'] > summary['sentiment_breakdown']['bearish']:
                summary['dominant_sentiment'] = 'bullish'
            elif summary['sentiment_breakdown']['bearish'] > summary['sentiment_breakdown']['bullish']:
                summary['dominant_sentiment'] = 'bearish'
            else:
                summary['dominant_sentiment'] = 'neutral'

        return summary


def main():
    parser = argparse.ArgumentParser(
        description='Research stock ticker sentiment on YouTube',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s TSLA
  %(prog)s AMZN --query "Amazon earnings Q4" --time-period this_week
  %(prog)s NVDA --max-videos 50
  %(prog)s MSFT --time-period today --no-details
        """
    )

    parser.add_argument('ticker', help='Stock ticker symbol (e.g., TSLA, AMZN)')
    parser.add_argument('--query', help='Custom search query (overrides default ticker search)')
    parser.add_argument(
        '--time-period',
        choices=['last_hour', 'today', 'this_week', 'this_month', 'this_year', 'all_time'],
        default='this_month',
        help='Time filter for videos (default: this_month)'
    )
    parser.add_argument('--max-videos', type=int, default=20, help='Maximum videos to fetch (default: 20)')
    parser.add_argument('--no-details', action='store_true', help='Skip fetching video details and transcripts')
    parser.add_argument('--output', help='Output file path (default: data/youtube/{ticker}_{timestamp}.json)')

    args = parser.parse_args()

    # Initialize researcher
    researcher = YouTubeStockResearch(API_KEY)

    # Run research
    results = researcher.research_stock(
        ticker=args.ticker.upper(),
        custom_query=args.query,
        time_period=args.time_period,
        max_videos=args.max_videos,
        include_details=not args.no_details
    )

    # Save results
    if args.output:
        output_file = args.output
    else:
        # Default output path
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        output_dir = '/home/user/social_media/data/youtube'
        os.makedirs(output_dir, exist_ok=True)
        output_file = f"{output_dir}/{args.ticker.upper()}_{args.time_period}_{timestamp}.json"

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n💾 Results saved to: {output_file}")

    # Print top videos
    print(f"\n📊 Top 5 Videos by Views:")
    print("─" * 100)

    sorted_videos = sorted(
        results['videos'],
        key=lambda v: v.get('viewCountInt', 0),
        reverse=True
    )

    for i, video in enumerate(sorted_videos[:5], 1):
        title = video.get('title', 'Unknown')
        views = video.get('viewCountInt', 0)
        likes = video.get('likeCountInt', 0)
        channel = video.get('channel', {}).get('title', 'Unknown')
        url = video.get('url', '')

        sentiment_info = ""
        if 'sentiment_analysis' in video:
            sent = video['sentiment_analysis']
            emoji = "🟢" if sent['sentiment'] == 'bullish' else "🔴" if sent['sentiment'] == 'bearish' else "⚪"
            sentiment_info = f" {emoji} {sent['sentiment'].upper()}"

        print(f"{i}. {title[:70]}")
        print(f"   Channel: {channel} | Views: {views:,} | Likes: {likes:,}{sentiment_info}")
        print(f"   {url}")
        print()


if __name__ == "__main__":
    main()
