#!/usr/bin/env python3
"""
Stock Social Data Fetcher (Reddit via SociaVault API)
======================================================

Fetches Reddit posts and discussions about specific stock tickers from
investment-focused subreddits using the SociaVault API.

SUBREDDITS COVERED:
    - r/stocks (stock market discussions and analysis)
    - r/ValueInvesting (value investing strategies)
    - r/options (options trading strategies)

INSTALLATION:
    pip install requests rich

CONFIGURATION:
    export SOCIAVAULT_API_KEY="your_api_key_here"

BASIC USAGE:
    python fetch_stock_social_data.py --ticker TSLA                    # Default: 14 days
    python fetch_stock_social_data.py --ticker AAPL --days 7           # Last week
    python fetch_stock_social_data.py --tickers TSLA AAPL NVDA         # Multiple tickers
    python fetch_stock_social_data.py --ticker MSFT --min-score 100    # High engagement only

PARAMETERS:
    --ticker         Single stock ticker (e.g., TSLA, AAPL, NVDA)
    --tickers        Multiple stock tickers space-separated
    --days           Number of days to look back (default: 14)
    --min-score      Minimum post score/upvotes (default: 50)
    --min-comments   Minimum number of comments (default: 10)
    --max-results    Maximum posts per ticker (default: 50)
    --save           Save results to JSON file (default: True)

FILTERING LOGIC:
    Posts are included if they meet ANY of these criteria:
    - Score (upvotes) >= min-score OR
    - Number of comments >= min-comments

    This ensures we capture both highly upvoted AND highly discussed posts.

OUTPUT:
    - Terminal: Formatted display with post title, stats, URL, body preview
    - File: data/stocks/{TICKER}/reddit_{timestamp}.json

API COST:
    - Credit check: 0 credits
    - Per ticker: 3 credits (1 per subreddit)
    - Example: 5 tickers = 15 credits = $0.072

EXAMPLE OUTPUT:
    data/stocks/TSLA/reddit_2026-02-01_15-30-45.json

FEATURES:
    - Smart engagement filtering (quality over quantity)
    - Date range filtering (get exactly N days of data)
    - Ticker-to-company name mapping for better search results
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
DEFAULT_DAYS = 14  # 2 weeks
DEFAULT_MIN_SCORE = 50  # Minimum upvotes to be considered
DEFAULT_MIN_COMMENTS = 10  # Minimum comments to be considered
DEFAULT_MAX_RESULTS = 50  # Max posts to return per ticker
REQUEST_TIMEOUT = 30  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 2

# Target subreddits for stock discussions
TARGET_SUBREDDITS = ["stocks", "ValueInvesting", "options"]

# Ticker to company name mapping for better search results
TICKER_MAPPING = {
    "TSLA": "Tesla",
    "AAPL": "Apple",
    "NVDA": "NVIDIA",
    "MSFT": "Microsoft",
    "AMZN": "Amazon",
    "GOOGL": "Google",
    "META": "Meta",
    "AMD": "AMD",
    "PLTR": "Palantir",
    "GME": "GameStop",
    "SPY": "S&P 500",
    "QQQ": "NASDAQ",
    "VOO": "Vanguard S&P 500",
}

# ============================================================================
# API CLIENT
# ============================================================================

class SociaVaultClient:
    """Client for interacting with SociaVault Reddit API."""

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

    def fetch_subreddit_posts(self, subreddit: str, timeframe: str = "month", sort: str = "top"):
        """
        Fetch posts from a specific subreddit with retry logic.

        Args:
            subreddit: Subreddit name (without r/ prefix)
            timeframe: Time period (hour, day, week, month, year, all)
            sort: Sort method (top, new, hot, rising, controversial)

        Returns:
            API response as dictionary containing posts from the subreddit

        Raises:
            Exception: If the request fails after all retries
        """
        params = {
            "subreddit": subreddit,
            "timeframe": timeframe,
            "sort": sort,
            "trim": False  # Get full data for analysis
        }

        # Retry logic with exponential backoff
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.get(
                    f"{SOCIAVAULT_BASE_URL}/scrape/reddit/subreddit",
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



def filter_posts_by_date(posts: list, days: int) -> list:
    """
    Filter posts to only include those from the last N days.

    Args:
        posts: List of post dictionaries
        days: Number of days to look back

    Returns:
        Filtered list of posts
    """
    cutoff_timestamp = (datetime.now() - timedelta(days=days)).timestamp()

    filtered = [
        post for post in posts
        if post.get('created_utc', 0) >= cutoff_timestamp
    ]

    return filtered


def filter_posts_by_engagement(posts: list, min_score: int, min_comments: int) -> list:
    """
    Filter posts by engagement metrics.

    Posts are included if they have:
    - Score >= min_score OR
    - Number of comments >= min_comments

    Args:
        posts: List of post dictionaries
        min_score: Minimum score/upvotes
        min_comments: Minimum number of comments

    Returns:
        Filtered list of posts
    """
    filtered = [
        post for post in posts
        if post.get('score', 0) >= min_score or post.get('num_comments', 0) >= min_comments
    ]

    return filtered


def filter_posts_by_ticker(posts: list, ticker: str, company_name: str = "") -> list:
    """
    Filter posts to only include those that mention the ticker or company.

    Args:
        posts: List of post dictionaries
        ticker: Stock ticker symbol
        company_name: Optional company name

    Returns:
        Filtered list of posts that mention the ticker or company
    """
    ticker_upper = ticker.upper()
    ticker_lower = ticker.lower()

    search_terms = [ticker_upper, ticker_lower, f"${ticker_upper}"]
    if company_name:
        search_terms.append(company_name.lower())

    filtered = []
    for post in posts:
        title = post.get('title', '').lower()
        selftext = post.get('selftext', '').lower()

        # Check if any search term appears in title or body
        for term in search_terms:
            if term.lower() in title or term.lower() in selftext:
                filtered.append(post)
                break

    return filtered


def extract_posts_from_response(data: dict) -> list:
    """
    Extract posts list from API response.

    Args:
        data: API response dictionary

    Returns:
        List of post dictionaries
    """
    posts_dict = data.get('data', {}).get('posts', {})

    if isinstance(posts_dict, dict):
        posts = list(posts_dict.values())
    else:
        posts = []

    return posts


def fetch_ticker_data(client: SociaVaultClient, ticker: str, days: int,
                     min_score: int, min_comments: int, max_results: int, console: Console) -> dict:
    """
    Fetch and filter Reddit posts for a specific ticker.

    Args:
        client: SociaVaultClient instance
        ticker: Stock ticker symbol
        days: Number of days to look back
        min_score: Minimum post score
        min_comments: Minimum number of comments
        max_results: Maximum posts to return
        console: Rich console object

    Returns:
        Dictionary with ticker data and filtered posts
    """
    try:
        company_name = TICKER_MAPPING.get(ticker.upper(), "")
        all_posts = []

        # Fetch from each target subreddit (1 credit per subreddit = 3 credits total)
        for subreddit in TARGET_SUBREDDITS:
            try:
                console.print(f"[cyan]  Fetching r/{subreddit}...[/cyan]")

                # Use month timeframe and filter locally for precise date control
                data = client.fetch_subreddit_posts(subreddit, timeframe="month", sort="top")

                # Extract posts
                posts = extract_posts_from_response(data)
                console.print(f"[dim]    Found {len(posts)} posts in r/{subreddit}[/dim]")

                all_posts.extend(posts)

                # Small delay between subreddit fetches
                if subreddit != TARGET_SUBREDDITS[-1]:
                    time.sleep(0.5)

            except Exception as e:
                console.print(f"[yellow]    ⚠ Error fetching r/{subreddit}: {str(e)}[/yellow]")
                continue

        console.print(f"[dim]  Total posts from all subreddits: {len(all_posts)}[/dim]")

        # Filter by ticker mention
        posts = filter_posts_by_ticker(all_posts, ticker, company_name)
        console.print(f"[dim]  After ticker filter: {len(posts)} posts[/dim]")

        # Filter by date
        posts = filter_posts_by_date(posts, days)
        console.print(f"[dim]  After date filter ({days} days): {len(posts)} posts[/dim]")

        # Filter by engagement
        posts = filter_posts_by_engagement(posts, min_score, min_comments)
        console.print(f"[dim]  After engagement filter: {len(posts)} posts[/dim]")

        # Sort by score (highest engagement first)
        posts.sort(key=lambda p: p.get('score', 0), reverse=True)

        # Limit results
        posts = posts[:max_results]

        console.print(f"[green]✓ {ticker}: {len(posts)} posts found[/green]")

        return {
            "ticker": ticker,
            "company_name": company_name,
            "days_back": days,
            "min_score": min_score,
            "min_comments": min_comments,
            "posts_count": len(posts),
            "posts": posts,
            "fetched_at": datetime.now().isoformat(),
            "subreddits": TARGET_SUBREDDITS
        }

    except Exception as e:
        console.print(f"[yellow]⚠ Error fetching {ticker}: {str(e)}[/yellow]")
        return {
            "ticker": ticker,
            "error": str(e),
            "posts": []
        }

# ============================================================================
# OUTPUT & DISPLAY
# ============================================================================

def display_ticker_results(ticker_data: dict, console: Console):
    """
    Display ticker results in formatted terminal output.

    Args:
        ticker_data: Ticker data dictionary with posts
        console: Rich console object
    """
    ticker = ticker_data.get('ticker', 'UNKNOWN')
    posts = ticker_data.get('posts', [])
    company_name = ticker_data.get('company_name', '')

    if not posts:
        console.print(f"\n[yellow]No posts found for ${ticker}[/yellow]")
        return

    # Header
    header_text = f"${ticker}"
    if company_name:
        header_text += f" - {company_name}"

    console.print("\n")
    console.print(Panel(Text(header_text, style="bold white", justify="center"),
                        border_style="blue", padding=(1, 2)))

    # Stats
    total_score = sum(p.get('score', 0) for p in posts)
    total_comments = sum(p.get('num_comments', 0) for p in posts)
    avg_upvote_ratio = sum(p.get('upvote_ratio', 0) for p in posts) / len(posts) if posts else 0

    stats_table = Table(show_header=False, box=None, padding=(0, 2))
    stats_table.add_column(justify="left")
    stats_table.add_column(justify="left")

    stats_table.add_row("[cyan]Posts Found:", f"[white]{len(posts)}[/white]")
    stats_table.add_row("[cyan]Total Upvotes:", f"[white]{total_score:,}[/white]")
    stats_table.add_row("[cyan]Total Comments:", f"[white]{total_comments:,}[/white]")
    stats_table.add_row("[cyan]Avg Upvote Ratio:", f"[white]{avg_upvote_ratio:.1%}[/white]")
    stats_table.add_row("[cyan]Timeframe:", f"[white]{ticker_data.get('days_back', 'N/A')} days[/white]")
    stats_table.add_row("[cyan]Subreddits:", f"[white]r/{', r/'.join(TARGET_SUBREDDITS)}[/white]")

    console.print(stats_table)
    console.print("\n" + "═" * console.width + "\n")

    # Display top posts
    for i, post in enumerate(posts, 1):
        # Title
        title = post.get('title', 'No title')
        title_text = Text(f"{i}. {title}", style="bold cyan")
        console.print(title_text)

        # Stats
        score = post.get('score', 0)
        num_comments = post.get('num_comments', 0)
        upvote_ratio = post.get('upvote_ratio', 0)
        author = post.get('author', 'unknown')
        subreddit = post.get('subreddit', 'unknown')
        created_utc = post.get('created_utc', 0)

        # Format date
        post_date = datetime.fromtimestamp(created_utc).strftime("%b %d, %Y")

        stats = f"[green]↑ {score:,}[/green]  •  [blue]{num_comments:,} comments[/blue]"
        if upvote_ratio:
            stats += f"  •  [dim]{int(upvote_ratio * 100)}% upvoted[/dim]"
        stats += f"  •  [yellow]r/{subreddit}[/yellow]  •  [dim]{post_date}[/dim]"
        console.print(stats)

        # URL
        permalink = post.get('permalink', '')
        if permalink:
            url = f"https://reddit.com{permalink}"
            console.print(f"[blue underline]{url}[/blue underline]")

        # Post body preview
        selftext = post.get('selftext', '')
        if selftext:
            console.print()
            max_length = 200
            clean_text = selftext.strip()
            if len(clean_text) > max_length:
                clean_text = clean_text[:max_length] + "..."
            console.print(f"[dim]{clean_text}[/dim]")

        # Separator
        if i < len(posts):
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
    filename = output_dir / f"reddit_{timestamp}.json"

    # Save data
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(ticker_data, f, indent=2, ensure_ascii=False)

    console.print(f"[green]💾 Saved to: {filename}[/green]")


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Main function to fetch stock social data from Reddit."""

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Fetch Reddit posts about stock tickers from investment subreddits'
    )

    # Ticker arguments (mutually exclusive)
    ticker_group = parser.add_mutually_exclusive_group(required=True)
    ticker_group.add_argument('--ticker', help='Single stock ticker (e.g., TSLA)')
    ticker_group.add_argument('--tickers', nargs='+', help='Multiple tickers (e.g., TSLA AAPL NVDA)')

    # Filter arguments
    parser.add_argument('--days', type=int, default=DEFAULT_DAYS,
                       help=f'Number of days to look back (default: {DEFAULT_DAYS})')
    parser.add_argument('--min-score', type=int, default=DEFAULT_MIN_SCORE,
                       help=f'Minimum post score (default: {DEFAULT_MIN_SCORE})')
    parser.add_argument('--min-comments', type=int, default=DEFAULT_MIN_COMMENTS,
                       help=f'Minimum comments (default: {DEFAULT_MIN_COMMENTS})')
    parser.add_argument('--max-results', type=int, default=DEFAULT_MAX_RESULTS,
                       help=f'Maximum posts per ticker (default: {DEFAULT_MAX_RESULTS})')

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

        # Warn if low on credits (3 credits per ticker)
        required_credits = len(tickers) * 3
        if isinstance(available_credits, (int, float)) and available_credits < required_credits:
            console.print(f"[yellow]⚠ Warning: Low credits. This operation requires {required_credits} credits.[/yellow]\n")

        # Display search parameters
        console.print("[cyan]Search Parameters:[/cyan]")
        console.print(f"  Tickers: {', '.join(tickers)}")
        console.print(f"  Days back: {args.days}")
        console.print(f"  Min score: {args.min_score}")
        console.print(f"  Min comments: {args.min_comments}")
        console.print(f"  Max results per ticker: {args.max_results}")
        console.print(f"  Target subreddits: r/{', r/'.join(TARGET_SUBREDDITS)}")
        console.print()

        # Fetch data for each ticker
        all_results = []
        for ticker in tickers:
            console.print(f"\n[bold cyan]Fetching ${ticker}...[/bold cyan]")

            ticker_data = fetch_ticker_data(
                client, ticker, args.days,
                args.min_score, args.min_comments, args.max_results,
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
        console.print(f"[dim]Total API credits used: {len(tickers) * 3}[/dim]")

        total_posts = sum(len(r.get('posts', [])) for r in all_results)
        console.print(f"[dim]Total posts found: {total_posts}[/dim]\n")

        return 0

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        return 1
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
