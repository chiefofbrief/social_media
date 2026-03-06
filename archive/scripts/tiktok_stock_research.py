#!/usr/bin/env python3
"""
TikTok Stock Research Script

Searches TikTok for videos about specific stock tickers or companies,
retrieves video details including transcripts, and analyzes sentiment.

Usage:
    python tiktok_stock_research.py TICKER [options]

Examples:
    python tiktok_stock_research.py TSLA
    python tiktok_stock_research.py AMZN --query "Amazon stock news" --time-period this_week
    python tiktok_stock_research.py NVDA --max-videos 50 --sort-by most-liked
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

BASE_URL = "https://api.sociavault.com/v1/scrape/tiktok"


class TikTokStockResearch:
    """TikTok stock research tool"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {'X-API-Key': api_key}

    def search_videos(
        self,
        query: str,
        date_posted: Optional[str] = None,
        sort_by: str = "relevance",
        max_videos: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search TikTok for videos matching query

        Args:
            query: Search query (e.g., "TSLA stock", "$AMZN", "#stocks")
            date_posted: Filter by date (yesterday, this-week, this-month, last-3-months, last-6-months, all-time)
            sort_by: Sort by relevance, most-liked, or date-posted
            max_videos: Maximum number of videos to fetch

        Returns:
            List of video objects
        """
        url = f"{BASE_URL}/search/keyword"

        params = {
            'query': query,
            'sort_by': sort_by
        }

        if date_posted:
            params['date_posted'] = date_posted

        all_videos = []
        cursor = None

        print(f"🔍 Searching TikTok for: '{query}'")
        if date_posted:
            print(f"📅 Time filter: {date_posted}")
        print(f"📊 Fetching up to {max_videos} videos...")

        while len(all_videos) < max_videos:
            if cursor:
                params['cursor'] = cursor

            try:
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                result = response.json()

                # Handle nested data structure
                if not result.get('success'):
                    print(f"❌ API returned error: {result.get('error', 'Unknown error')}")
                    break

                data = result.get('data', {})
                search_items_dict = data.get('search_item_list', {})

                # Convert search_item_list object to list
                if isinstance(search_items_dict, dict):
                    search_items = list(search_items_dict.values())
                else:
                    search_items = search_items_dict

                if not search_items:
                    break

                # Extract aweme_info from each search item
                videos = []
                for item in search_items:
                    aweme_info = item.get('aweme_info', {})
                    if aweme_info:
                        videos.append(aweme_info)

                if not videos:
                    break

                all_videos.extend(videos)
                print(f"   Found {len(all_videos)} videos so far...")

                # Get cursor for next page
                cursor = data.get('cursor')
                if not cursor or cursor == 0:
                    break

            except Exception as e:
                print(f"❌ Error searching: {e}")
                break

        result = all_videos[:max_videos]
        print(f"✅ Retrieved {len(result)} videos\n")
        return result

    def get_video_details(self, video_id: str, author_unique_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a video including transcript

        Args:
            video_id: TikTok video ID
            author_unique_id: Author's unique ID

        Returns:
            Video details dictionary or None if error
        """
        # Construct TikTok URL
        video_url = f"https://www.tiktok.com/@{author_unique_id}/video/{video_id}"

        url = f"{BASE_URL}/video-info"
        params = {
            'url': video_url,
            'get_transcript': 'true'
        }

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()

            aweme_detail = data.get('aweme_detail', {})

            # Add transcript to main object if available
            if 'transcript' in data and data['transcript']:
                aweme_detail['transcript_text'] = self._parse_webvtt(data['transcript'])

            return aweme_detail
        except Exception as e:
            print(f"⚠️  Error getting details for video {video_id}: {e}")
            return None

    def _parse_webvtt(self, webvtt: str) -> str:
        """Parse WEBVTT transcript to plain text"""
        if not webvtt:
            return ""

        lines = webvtt.split('\n')
        text_lines = []

        for line in lines:
            line = line.strip()
            # Skip WEBVTT header, timestamps, and empty lines
            if line and not line.startswith('WEBVTT') and '-->' not in line:
                text_lines.append(line)

        return ' '.join(text_lines)

    def analyze_video_sentiment(self, video: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze sentiment in video description and transcript

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
        desc = (video.get('desc') or '').lower()
        transcript = (video.get('transcript_text') or '').lower()

        all_text = f"{desc} {transcript}"

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
        time_period: str = "this-month",
        max_videos: int = 20,
        sort_by: str = "relevance",
        include_details: bool = True
    ) -> Dict[str, Any]:
        """
        Research a stock ticker on TikTok

        Args:
            ticker: Stock ticker symbol (e.g., "TSLA", "AMZN")
            custom_query: Custom search query (overrides default ticker search)
            time_period: Time filter for videos
            max_videos: Maximum videos to analyze
            sort_by: Sort method (relevance, most-liked, date-posted)
            include_details: Whether to fetch full video details + transcripts

        Returns:
            Research results dictionary
        """
        # Build search query
        if custom_query:
            query = custom_query
        else:
            # Try both ticker formats: "#TSLA stock" and "$TSLA"
            query = f"#{ticker} stock"

        # Search for videos
        videos = self.search_videos(
            query=query,
            date_posted=time_period if time_period != "all_time" else None,
            sort_by=sort_by,
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
                # Extract necessary info from basic video object
                video_id = video.get('aweme_id')
                author = video.get('author', {})
                author_unique_id = author.get('unique_id', '')

                if not video_id or not author_unique_id:
                    enriched_videos.append(video)
                    continue

                desc = video.get('desc', 'Unknown')
                print(f"   [{i}/{len(videos)}] {desc[:60]}...")

                details = self.get_video_details(video_id, author_unique_id)

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
        if include_details and 'sentiment_breakdown' in summary:
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
        # Get stats from statistics object in TikTok response
        total_views = 0
        total_likes = 0
        total_comments = 0
        total_shares = 0

        for v in videos:
            stats = v.get('statistics', {})
            total_views += (stats.get('play_count') or 0)
            total_likes += (stats.get('digg_count') or 0)
            total_comments += (stats.get('comment_count') or 0)
            total_shares += (stats.get('share_count') or 0)

        summary = {
            'total_videos': len(videos),
            'total_views': total_views,
            'total_likes': total_likes,
            'total_comments': total_comments,
            'total_shares': total_shares,
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
        description='Research stock ticker sentiment on TikTok',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s TSLA
  %(prog)s AMZN --query "Amazon stock news" --time-period this-week
  %(prog)s NVDA --max-videos 50 --sort-by most-liked
  %(prog)s MSFT --time-period yesterday --no-details
        """
    )

    parser.add_argument('ticker', help='Stock ticker symbol (e.g., TSLA, AMZN)')
    parser.add_argument('--query', help='Custom search query (overrides default ticker search)')
    parser.add_argument(
        '--time-period',
        choices=['yesterday', 'this-week', 'this-month', 'last-3-months', 'last-6-months', 'all_time'],
        default='this-month',
        help='Time filter for videos (default: this-month)'
    )
    parser.add_argument(
        '--sort-by',
        choices=['relevance', 'most-liked', 'date-posted'],
        default='relevance',
        help='Sort method (default: relevance)'
    )
    parser.add_argument('--max-videos', type=int, default=20, help='Maximum videos to fetch (default: 20)')
    parser.add_argument('--no-details', action='store_true', help='Skip fetching video details and transcripts')
    parser.add_argument('--output', help='Output file path (default: data/tiktok/{ticker}_{timestamp}.json)')

    args = parser.parse_args()

    # Initialize researcher
    researcher = TikTokStockResearch(API_KEY)

    # Run research
    results = researcher.research_stock(
        ticker=args.ticker.upper(),
        custom_query=args.query,
        time_period=args.time_period,
        max_videos=args.max_videos,
        sort_by=args.sort_by,
        include_details=not args.no_details
    )

    # Save results
    if args.output:
        output_file = args.output
    else:
        # Default output path
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        output_dir = '/home/user/social_media/data/tiktok'
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
        key=lambda v: v.get('statistics', {}).get('play_count', 0),
        reverse=True
    )

    for i, video in enumerate(sorted_videos[:5], 1):
        desc = video.get('desc', 'No description')
        stats = video.get('statistics', {})
        views = stats.get('play_count', 0)
        likes = stats.get('digg_count', 0)

        author = video.get('author', {})
        username = author.get('unique_id', 'Unknown')

        sentiment_info = ""
        if 'sentiment_analysis' in video:
            sent = video['sentiment_analysis']
            emoji = "🟢" if sent['sentiment'] == 'bullish' else "🔴" if sent['sentiment'] == 'bearish' else "⚪"
            sentiment_info = f" {emoji} {sent['sentiment'].upper()}"

        video_id = video.get('aweme_id', '')
        video_url = f"https://www.tiktok.com/@{username}/video/{video_id}"

        print(f"{i}. {desc[:70]}")
        print(f"   @{username} | Views: {views:,} | Likes: {likes:,}{sentiment_info}")
        print(f"   {video_url}")
        print()


if __name__ == "__main__":
    main()
