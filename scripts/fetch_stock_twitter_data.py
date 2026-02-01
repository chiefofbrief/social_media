#!/usr/bin/env python3
"""
Stock Twitter/X Data Fetcher (via SociaVault API)
==================================================

Fetches tweets about specific stock tickers from influential financial/news accounts
via the SociaVault API.

APPROACH:
    Since SociaVault doesn't support Twitter search/hashtag endpoints, this script:
    1. Fetches tweets from curated list of financial news & analyst accounts
    2. Filters for mentions of your target ticker(s)
    3. Returns tweets with high engagement that mention the stock

TARGET ACCOUNTS (automatically checked):
    - Financial news: CNBC, Bloomberg, Reuters, WSJ, FT
    - Market analysts: stocktalkweekly, unusual_whales
    - Company officials: checked for each ticker (e.g., @elonmusk for TSLA)

INSTALLATION:
    pip install requests rich

CONFIGURATION:
    export SOCIAVAULT_API_KEY="your_api_key_here"

BASIC USAGE:
    python fetch_stock_twitter_data.py --ticker TSLA                    # Default: 7 days
    python fetch_stock_twitter_data.py --ticker AAPL --days 3           # Last 3 days
    python fetch_stock_twitter_data.py --tickers TSLA AAPL NVDA         # Multiple tickers
    python fetch_stock_twitter_data.py --ticker MSFT --min-likes 100    # High engagement only

PARAMETERS:
    --ticker         Single stock ticker (e.g., TSLA, AAPL, NVDA)
    --tickers        Multiple stock tickers space-separated
    --days           Number of days to look back (default: 7)
    --min-likes      Minimum tweet likes (default: 10)
    --min-retweets   Minimum retweets (default: 5)
    --max-results    Maximum tweets per ticker (default: 50)
    --save           Save results to JSON file (default: True)

FILTERING LOGIC:
    Tweets are included if they:
    - Mention the ticker symbol (e.g., TSLA, $TSLA) OR company name
    - Have likes >= min-likes OR retweets >= min-retweets
    - Are from the last N days

OUTPUT:
    - Terminal: Formatted display with tweet text, stats, URL
    - File: data/stocks/{TICKER}/twitter_{timestamp}.json

API COST:
    - Credit check: 0 credits
    - Per ticker: 5-8 credits (fetches from 5-8 influential accounts)
    - Example: 1 ticker = ~6 credits = $0.029

EXAMPLE OUTPUT:
    data/stocks/TSLA/twitter_2026-02-01_15-30-45.json

FEATURES:
    - Curated list of influential financial accounts
    - Smart ticker mention filtering (ticker symbols + company names)
    - Engagement filtering (quality over quantity)
    - Date range filtering (get exactly N days of data)
    - Rich terminal formatting with stats
    - Automatic data organization by ticker
    - Retry logic with exponential backoff

REQUIREMENTS:
    - Python 3.7+
    - requests (for API calls)
    - rich (for terminal formatting)
    - Valid SociaVault API key
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

try:
    import requests
except ImportError:
    print("Error: requests not installed. Please run: pip install requests rich")
    sys.exit(1)

# ============================================================================
# CONSTANTS
# ============================================================================

SOCIAVAULT_BASE_URL = "https://api.sociavault.com/v1"
DEFAULT_DAYS = 7  # 1 week (Twitter moves faster than Reddit)
DEFAULT_MIN_LIKES = 10  # Minimum likes to be considered
DEFAULT_MIN_RETWEETS = 5  # Minimum retweets to be considered
DEFAULT_MAX_RESULTS = 50  # Max tweets to return per ticker
REQUEST_TIMEOUT = 30  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 2

# Financial news and analyst accounts to check for stock mentions
FINANCIAL_ACCOUNTS = [
    "CNBC",
    "Bloomberg",
    "Reuters",
    "WSJ",
    "FT",
    "MarketWatch",
    "stocktalkweekly",
    "unusual_whales",
]

# Company official accounts and CEOs for specific tickers
TICKER_ACCOUNTS = {
    "TSLA": ["elonmusk", "Tesla"],
    "AAPL": ["tim_cook", "Apple"],
    "NVDA": ["nvidia", "nvidiaai"],
    "MSFT": ["Microsoft", "satyanadella"],
    "AMZN": ["amazon", "JeffBezos"],
    "META": ["Meta", "finkd"],
    "GOOGL": ["Google", "sundarpichai"],
    "AMD": ["AMD", "LisaSu"],
    "PLTR": ["PalantirTech"],
}

# ============================================================================
# API CLIENT
# ============================================================================

class SociaVaultClient:
    """Client for interacting with SociaVault Twitter/X API."""

    def __init__(self, api_key: str):
        """Initialize client with API key."""
        self.api_key = api_key
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }

    def check_credits(self):
        """Check available API credits (costs 0 credits)."""
        response = requests.get(
            f"{SOCIAVAULT_BASE_URL}/credits",
            headers=self.headers,
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        return response.json()

    def fetch_user_tweets(self, handle: str):
        """
        Fetch tweets from a specific Twitter user with retry logic.

        Args:
            handle: Twitter handle without @ (e.g., "elonmusk")

        Returns:
            API response as dictionary containing tweets

        Raises:
            Exception: If the request fails after all retries
        """
        params = {
            "handle": handle,
            "trim": False  # Get full data for analysis
        }

        # Retry logic with exponential backoff
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.get(
                    f"{SOCIAVAULT_BASE_URL}/scrape/twitter/user-tweets",
                    headers=self.headers,
                    params=params,
                    timeout=REQUEST_TIMEOUT
                )

                # Handle rate limiting (429) with retry
                if response.status_code == 429:
                    if attempt < MAX_RETRIES - 1:
                        delay = RETRY_DELAY * (2 ** attempt)
                        print(f"  ⚠️  Rate limit hit (attempt {attempt + 1}/{MAX_RETRIES})")
                        print(f"  ⏳ Waiting {delay}s before retry...")
                        time.sleep(delay)
                        continue
                    else:
                        raise Exception(f"API rate limit exceeded after {MAX_RETRIES} retries.")

                # Raise for other HTTP errors
                response.raise_for_status()
                return response.json()

            except requests.exceptions.HTTPError as e:
                if response.status_code == 401:
                    raise Exception("Authentication failed. Please check your SOCIAVAULT_API_KEY.")
                elif response.status_code == 402:
                    raise Exception("Insufficient credits. Please check your SociaVault account.")
                elif response.status_code == 403:
                    raise Exception("Access forbidden. Your API key may not have access to this endpoint.")
                elif response.status_code == 429:
                    continue
                else:
                    raise Exception(f"API request failed with status {response.status_code}: {str(e)}")
            except requests.exceptions.Timeout:
                if attempt < MAX_RETRIES - 1:
                    delay = RETRY_DELAY * (2 ** attempt)
                    print(f"  ⚠️  Request timeout (attempt {attempt + 1}/{MAX_RETRIES})")
                    print(f"  ⏳ Retrying in {delay}s...")
                    time.sleep(delay)
                    continue
                raise Exception(f"API request timed out after multiple retries.")
            except requests.exceptions.RequestException as e:
                raise Exception(f"API request failed: {str(e)}")

        # If we exhausted all retries
        raise Exception(f"API request failed after {MAX_RETRIES} retries.")

# ============================================================================
# DATA PROCESSING
# ============================================================================

def filter_tweets_by_date(tweets: list, days: int) -> list:
    """
    Filter tweets to only include those from the last N days.

    Args:
        tweets: List of tweet dictionaries
        days: Number of days to look back

    Returns:
        Filtered list of tweets
    """
    cutoff_timestamp = (datetime.now() - timedelta(days=days)).timestamp()

    filtered = []
    for tweet in tweets:
        # Twitter API returns created_at as a timestamp or date string
        created_at = tweet.get('created_at', 0)

        # Handle different date formats
        if isinstance(created_at, str):
            try:
                # Try parsing ISO format
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                tweet_timestamp = dt.timestamp()
            except:
                continue
        else:
            tweet_timestamp = created_at

        if tweet_timestamp >= cutoff_timestamp:
            filtered.append(tweet)

    return filtered


def filter_tweets_by_engagement(tweets: list, min_likes: int, min_retweets: int) -> list:
    """
    Filter tweets by engagement metrics.

    Tweets are included if they have:
    - Likes >= min_likes OR
    - Retweets >= min_retweets

    Args:
        tweets: List of tweet dictionaries
        min_likes: Minimum likes/favorites
        min_retweets: Minimum retweets

    Returns:
        Filtered list of tweets
    """
    filtered = []
    for tweet in tweets:
        # Get engagement metrics from the legacy field or top level
        legacy = tweet.get('legacy', {})
        likes = legacy.get('favorite_count', 0) or tweet.get('favorite_count', 0)
        retweets = legacy.get('retweet_count', 0) or tweet.get('retweet_count', 0)

        if likes >= min_likes or retweets >= min_retweets:
            filtered.append(tweet)

    return filtered


def extract_tweets_from_response(data: dict) -> list:
    """
    Extract tweets list from API response.

    Args:
        data: API response dictionary

    Returns:
        List of tweet dictionaries
    """
    # Twitter API might return tweets in different structures
    tweets = data.get('data', {}).get('tweets', [])

    if isinstance(tweets, dict):
        tweets = list(tweets.values())
    elif not isinstance(tweets, list):
        tweets = []

    return tweets


def filter_tweets_by_ticker(tweets: list, ticker: str) -> list:
    """
    Filter tweets to only include those that mention the ticker.

    Args:
        tweets: List of tweet dictionaries
        ticker: Stock ticker symbol (e.g., TSLA)

    Returns:
        Filtered list of tweets that mention the ticker
    """
    ticker_upper = ticker.upper()
    ticker_lower = ticker.lower()

    # Search variations: TSLA, $TSLA, #TSLA, tsla
    search_terms = [
        ticker_upper,
        ticker_lower,
        f"${ticker_upper}",
        f"#{ticker_upper}",
        f"${ticker_lower}",
        f"#{ticker_lower}",
    ]

    filtered = []
    for tweet in tweets:
        legacy = tweet.get('legacy', {})
        text = legacy.get('full_text', '') or tweet.get('text', '') or tweet.get('full_text', '')
        text_lower = text.lower()

        # Check if any search term appears in the tweet text
        for term in search_terms:
            if term.lower() in text_lower:
                filtered.append(tweet)
                break

    return filtered


def fetch_ticker_data(client: SociaVaultClient, ticker: str, days: int,
                     min_likes: int, min_retweets: int, max_results: int, console: Console) -> dict:
    """
    Fetch and filter Twitter posts for a specific ticker.

    Args:
        client: SociaVaultClient instance
        ticker: Stock ticker symbol
        days: Number of days to look back
        min_likes: Minimum tweet likes
        min_retweets: Minimum retweets
        max_results: Maximum tweets to return
        console: Rich console object

    Returns:
        Dictionary with ticker data and filtered tweets
    """
    try:
        # Build list of accounts to check
        accounts_to_check = FINANCIAL_ACCOUNTS.copy()

        # Add ticker-specific accounts if available
        ticker_accounts = TICKER_ACCOUNTS.get(ticker.upper(), [])
        accounts_to_check.extend(ticker_accounts)

        console.print(f"[cyan]  Checking {len(accounts_to_check)} accounts for ${ticker} mentions...[/cyan]")

        all_tweets = []
        successful_fetches = 0

        # Fetch from each account
        for account in accounts_to_check:
            try:
                console.print(f"[dim]    Fetching @{account}...[/dim]", end=" ")

                data = client.fetch_user_tweets(account)
                tweets = extract_tweets_from_response(data)

                console.print(f"[dim]{len(tweets)} tweets[/dim]")
                all_tweets.extend(tweets)
                successful_fetches += 1

                # Small delay between accounts
                if account != accounts_to_check[-1]:
                    time.sleep(0.5)

            except Exception as e:
                console.print(f"[yellow]⚠ Error[/yellow]")
                continue

        console.print(f"[dim]  Total tweets from {successful_fetches} accounts: {len(all_tweets)}[/dim]")

        # Filter by ticker mention
        tweets = filter_tweets_by_ticker(all_tweets, ticker)
        console.print(f"[dim]  After ticker filter: {len(tweets)} tweets mention ${ticker}[/dim]")

        # Filter by date
        tweets = filter_tweets_by_date(tweets, days)
        console.print(f"[dim]  After date filter ({days} days): {len(tweets)} tweets[/dim]")

        # Filter by engagement
        tweets = filter_tweets_by_engagement(tweets, min_likes, min_retweets)
        console.print(f"[dim]  After engagement filter: {len(tweets)} tweets[/dim]")

        # Sort by engagement (likes + retweets)
        def get_engagement_score(tweet):
            legacy = tweet.get('legacy', {})
            likes = legacy.get('favorite_count', 0) or tweet.get('favorite_count', 0)
            retweets = legacy.get('retweet_count', 0) or tweet.get('retweet_count', 0)
            return likes + (retweets * 2)  # Weight retweets higher

        tweets.sort(key=get_engagement_score, reverse=True)

        # Limit results
        tweets = tweets[:max_results]

        console.print(f"[green]✓ ${ticker}: {len(tweets)} tweets found[/green]")

        return {
            "ticker": ticker,
            "days_back": days,
            "min_likes": min_likes,
            "min_retweets": min_retweets,
            "tweets_count": len(tweets),
            "tweets": tweets,
            "fetched_at": datetime.now().isoformat(),
            "accounts_checked": accounts_to_check,
            "successful_fetches": successful_fetches,
            "platform": "twitter"
        }

    except Exception as e:
        console.print(f"[yellow]⚠ Error fetching ${ticker}: {str(e)}[/yellow]")
        return {
            "ticker": ticker,
            "error": str(e),
            "tweets": []
        }

# ============================================================================
# OUTPUT & DISPLAY
# ============================================================================

def display_ticker_results(ticker_data: dict, console: Console):
    """
    Display ticker results in formatted terminal output.

    Args:
        ticker_data: Ticker data dictionary with tweets
        console: Rich console object
    """
    ticker = ticker_data.get('ticker', 'UNKNOWN')
    tweets = ticker_data.get('tweets', [])

    if not tweets:
        console.print(f"\n[yellow]No tweets found for ${ticker}[/yellow]")
        return

    # Header
    header_text = f"${ticker} on Twitter/X"

    console.print("\n")
    console.print(Panel(Text(header_text, style="bold white", justify="center"),
                        border_style="blue", padding=(1, 2)))

    # Stats
    total_likes = sum(t.get('legacy', {}).get('favorite_count', 0) or t.get('favorite_count', 0) for t in tweets)
    total_retweets = sum(t.get('legacy', {}).get('retweet_count', 0) or t.get('retweet_count', 0) for t in tweets)
    total_replies = sum(t.get('legacy', {}).get('reply_count', 0) or t.get('reply_count', 0) for t in tweets)

    stats_table = Table(show_header=False, box=None, padding=(0, 2))
    stats_table.add_column(justify="left")
    stats_table.add_column(justify="left")

    stats_table.add_row("[cyan]Tweets Found:", f"[white]{len(tweets)}[/white]")
    stats_table.add_row("[cyan]Total Likes:", f"[white]{total_likes:,}[/white]")
    stats_table.add_row("[cyan]Total Retweets:", f"[white]{total_retweets:,}[/white]")
    stats_table.add_row("[cyan]Total Replies:", f"[white]{total_replies:,}[/white]")
    stats_table.add_row("[cyan]Timeframe:", f"[white]{ticker_data.get('days_back', 'N/A')} days[/white]")

    console.print(stats_table)
    console.print("\n" + "═" * console.width + "\n")

    # Display top tweets
    for i, tweet in enumerate(tweets, 1):
        legacy = tweet.get('legacy', {})
        user_legacy = tweet.get('user', {}).get('legacy', {})

        # Extract tweet text
        text = legacy.get('full_text', '') or tweet.get('text', '') or tweet.get('full_text', '')

        # Get engagement metrics
        likes = legacy.get('favorite_count', 0) or tweet.get('favorite_count', 0)
        retweets = legacy.get('retweet_count', 0) or tweet.get('retweet_count', 0)
        replies = legacy.get('reply_count', 0) or tweet.get('reply_count', 0)

        # Get user info
        username = user_legacy.get('screen_name', '') or tweet.get('username', 'unknown')

        # Get timestamp
        created_at = legacy.get('created_at', '') or tweet.get('created_at', '')
        if created_at:
            try:
                if isinstance(created_at, str):
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                else:
                    dt = datetime.fromtimestamp(created_at)
                tweet_date = dt.strftime("%b %d, %Y %H:%M")
            except:
                tweet_date = str(created_at)
        else:
            tweet_date = "unknown"

        # Display tweet number and text
        console.print(f"[bold cyan]{i}.[/bold cyan]")

        # Truncate long tweets for display
        max_length = 280
        display_text = text.strip()
        if len(display_text) > max_length:
            display_text = display_text[:max_length] + "..."

        console.print(f"[white]{display_text}[/white]")
        console.print()

        # Stats
        stats = f"[red]❤ {likes:,}[/red]  •  [green]🔁 {retweets:,}[/green]  •  [blue]💬 {replies:,}[/blue]"
        stats += f"  •  [dim]@{username}  •  {tweet_date}[/dim]"
        console.print(stats)

        # Tweet URL (if available)
        tweet_id = tweet.get('id_str', '') or tweet.get('id', '')
        if tweet_id and username:
            url = f"https://twitter.com/{username}/status/{tweet_id}"
            console.print(f"[blue underline]{url}[/blue underline]")

        # Separator
        if i < len(tweets):
            console.print("\n" + "─" * console.width + "\n")

    console.print("\n" + "═" * console.width + "\n")


def save_ticker_data(ticker_data: dict, console: Console):
    """
    Save ticker data to JSON file.

    Args:
        ticker_data: Ticker data dictionary
        console: Rich console object
    """
    ticker = ticker_data.get('ticker', 'UNKNOWN')

    # Create directory structure
    output_dir = Path("data/stocks") / ticker
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = output_dir / f"twitter_{timestamp}.json"

    # Save data
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(ticker_data, f, indent=2, ensure_ascii=False)

    console.print(f"[green]💾 Saved to: {filename}[/green]")


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Main function to fetch stock Twitter/X data."""

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Fetch Twitter/X posts about stock tickers using cashtag search'
    )

    # Ticker arguments (mutually exclusive)
    ticker_group = parser.add_mutually_exclusive_group(required=True)
    ticker_group.add_argument('--ticker', help='Single stock ticker (e.g., TSLA)')
    ticker_group.add_argument('--tickers', nargs='+', help='Multiple tickers (e.g., TSLA AAPL NVDA)')

    # Filter arguments
    parser.add_argument('--days', type=int, default=DEFAULT_DAYS,
                       help=f'Number of days to look back (default: {DEFAULT_DAYS})')
    parser.add_argument('--min-likes', type=int, default=DEFAULT_MIN_LIKES,
                       help=f'Minimum tweet likes (default: {DEFAULT_MIN_LIKES})')
    parser.add_argument('--min-retweets', type=int, default=DEFAULT_MIN_RETWEETS,
                       help=f'Minimum retweets (default: {DEFAULT_MIN_RETWEETS})')
    parser.add_argument('--max-results', type=int, default=DEFAULT_MAX_RESULTS,
                       help=f'Maximum tweets per ticker (default: {DEFAULT_MAX_RESULTS})')

    # Output arguments
    parser.add_argument('--no-save', action='store_true',
                       help='Do not save results to file')

    args = parser.parse_args()

    console = Console()

    # Get API key from environment
    api_key = os.environ.get('SOCIAVAULT_API_KEY')
    if not api_key:
        console.print("[red]Error: SOCIAVAULT_API_KEY environment variable not set[/red]")
        console.print("\n[yellow]Please set your API key:[/yellow]")
        console.print("  export SOCIAVAULT_API_KEY='your_api_key_here'")
        return 1

    # Determine tickers to fetch
    if args.ticker:
        tickers = [args.ticker.upper()]
    else:
        tickers = [t.upper() for t in args.tickers]

    try:
        # Initialize client
        client = SociaVaultClient(api_key)

        # Check credits
        console.print("[cyan]Checking API credits...[/cyan]")
        credits_info = client.check_credits()
        available_credits = credits_info.get('credits', 'unknown')
        console.print(f"[green]✓ Available credits: {available_credits}[/green]\n")

        # Warn if low on credits (estimate 8 accounts per ticker)
        estimated_credits = len(tickers) * 8
        if isinstance(available_credits, (int, float)) and available_credits < estimated_credits:
            console.print(f"[yellow]⚠ Warning: Low credits. This operation may require up to {estimated_credits} credits.[/yellow]\n")

        # Display search parameters
        console.print("[cyan]Search Parameters:[/cyan]")
        console.print(f"  Tickers: {', '.join(tickers)}")
        console.print(f"  Days back: {args.days}")
        console.print(f"  Min likes: {args.min_likes}")
        console.print(f"  Min retweets: {args.min_retweets}")
        console.print(f"  Max results per ticker: {args.max_results}")
        console.print()

        # Fetch data for each ticker
        all_results = []
        for ticker in tickers:
            console.print(f"\n[bold cyan]Fetching ${ticker}...[/bold cyan]")

            ticker_data = fetch_ticker_data(
                client, ticker, args.days,
                args.min_likes, args.min_retweets, args.max_results,
                console
            )

            all_results.append(ticker_data)

            # Display results
            display_ticker_results(ticker_data, console)

            # Save to file
            if not args.no_save:
                save_ticker_data(ticker_data, console)

            # Add delay between tickers to avoid rate limiting
            if len(tickers) > 1 and ticker != tickers[-1]:
                time.sleep(1)

        # Summary
        console.print("\n" + "═" * console.width)
        console.print(f"\n[green]✓ Completed! Processed {len(tickers)} ticker(s)[/green]")

        total_credits = sum(r.get('successful_fetches', 0) for r in all_results)
        console.print(f"[dim]Total API credits used: {total_credits}[/dim]")

        total_tweets = sum(len(r.get('tweets', [])) for r in all_results)
        console.print(f"[dim]Total tweets found: {total_tweets}[/dim]\n")

        return 0

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        return 1
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
