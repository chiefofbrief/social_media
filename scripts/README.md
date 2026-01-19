# Reddit Data Collection Scripts

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
