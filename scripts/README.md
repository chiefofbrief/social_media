# Social Media Data Collection Scripts

## fetch_stock_social_data.py

**NEW:** Fetches Reddit posts about specific stock tickers from investment-focused subreddits.

### Features

- Search by stock ticker (e.g., TSLA, AAPL, NVDA)
- Automatically searches 3 key subreddits: r/stocks, r/ValueInvesting, r/options
- Smart engagement filtering (upvotes OR comments threshold)
- Date range filtering (default: 2 weeks)
- Ticker-to-company name mapping for better search results
- Beautiful terminal output with rich formatting
- Auto-saves to organized directory structure

### Setup

1. Set your SociaVault API key:
   ```bash
   export SOCIAVAULT_API_KEY="your-api-key-here"
   ```

2. Install dependencies:
   ```bash
   pip install requests rich
   ```

### Usage

**Single ticker (default: 14 days, engagement filter):**
```bash
python scripts/fetch_stock_social_data.py --ticker TSLA
```

**Multiple tickers:**
```bash
python scripts/fetch_stock_social_data.py --tickers TSLA AAPL NVDA
```

**Custom timeframe (7 days):**
```bash
python scripts/fetch_stock_social_data.py --ticker AAPL --days 7
```

**Higher engagement filter:**
```bash
python scripts/fetch_stock_social_data.py --ticker NVDA --min-score 100 --min-comments 20
```

**More results:**
```bash
python scripts/fetch_stock_social_data.py --ticker MSFT --max-results 100
```

### Parameters

- `--ticker`: Single stock ticker (e.g., TSLA)
- `--tickers`: Multiple tickers space-separated (e.g., TSLA AAPL NVDA)
- `--days`: Number of days to look back (default: 14)
- `--min-score`: Minimum post upvotes (default: 50)
- `--min-comments`: Minimum comments (default: 10)
- `--max-results`: Max posts per ticker (default: 50)
- `--no-save`: Don't save to file (display only)

**Filtering Logic:** Posts are included if they have score >= min-score OR comments >= min-comments

### Output

**Terminal:** Beautiful formatted display with:
- Post titles, upvotes, comments, upvote ratio
- Subreddit, author, date
- Clickable URLs
- Post body preview (first 200 chars)
- Summary statistics

**File:** `data/stocks/{TICKER}/reddit_{timestamp}.json`

Example: `data/stocks/TSLA/reddit_2026-02-01_15-30-45.json`

### Cost

- **3 credits per ticker** (1 credit per subreddit)
- Credit check: 0 credits (automatic)
- Example: 5 tickers = 15 credits = $0.072

### Example Output Structure

```json
{
  "ticker": "TSLA",
  "company_name": "Tesla",
  "search_query": "(TSLA OR \"Tesla\") (stock OR price OR earnings OR buy OR sell OR analysis)",
  "days_back": 14,
  "posts_count": 42,
  "subreddits": ["stocks", "ValueInvesting", "options"],
  "posts": [
    {
      "title": "Tesla Q4 earnings discussion",
      "score": 523,
      "num_comments": 187,
      "upvote_ratio": 0.92,
      "subreddit": "stocks",
      "author": "investor123",
      "created_utc": 1738348800,
      "permalink": "/r/stocks/comments/...",
      "selftext": "...",
      "url": "..."
    }
  ]
}
```

---

## fetch_reddit_posts.py

Fetches top posts from any subreddit using the SociaVault API.

### Setup

1. Set your SociaVault API key as an environment variable:
   ```bash
   export SOCIAVAULT_API_KEY="your-api-key-here"
   ```

2. Install required dependencies:
   ```bash
   pip install requests
   ```

### Usage

Basic usage (fetches ~25 top posts from past month):
```bash
python scripts/fetch_reddit_posts.py --subreddit ValueInvesting
```

Custom parameters:
```bash
python scripts/fetch_reddit_posts.py \
  --subreddit ValueInvesting \
  --timeframe week \
  --sort hot
```

### Parameters

- `--subreddit`: Subreddit name (required, without r/ prefix)
- `--timeframe`: Time period (hour, day, week, month, year, all) - default: month
- `--sort`: Sort method (top, new, hot, rising, controversial) - default: top
- `--trim`: Use trimmed response for faster/lighter data (optional flag)

**Note:** The API returns ~25 posts per page. To fetch more posts, use pagination with the `after` parameter (not yet implemented).

### Output

The script saves one file in `data/reddit/`:

**Raw JSON**: `{subreddit}_{sort}_{timeframe}_{timestamp}.json`
- Complete API response with all post data
- Includes full titles and body text (`selftext` field)
- Ready for analysis with custom scripts or Claude
- Key fields: `title`, `selftext`, `score`, `num_comments`, `upvote_ratio`, `is_self`, `is_video`, `author`, `created_utc`

### Cost

- **1 API credit** per execution
- Credit check (0 credits) runs automatically before fetch

### Examples

Fetch top posts from r/ValueInvesting (past month):
```bash
python scripts/fetch_reddit_posts.py --subreddit ValueInvesting
```

Fetch trending posts from r/stocks (past week):
```bash
python scripts/fetch_reddit_posts.py --subreddit stocks --timeframe week --sort hot
```

Fetch controversial posts:
```bash
python scripts/fetch_reddit_posts.py --subreddit wallstreetbets --sort controversial
```
