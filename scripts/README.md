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

Basic usage (fetches top 30 posts from past month):
```bash
python scripts/fetch_reddit_posts.py --subreddit ValueInvesting
```

Custom parameters:
```bash
python scripts/fetch_reddit_posts.py \
  --subreddit ValueInvesting \
  --timeframe week \
  --sort top \
  --limit 50
```

### Parameters

- `--subreddit`: Subreddit name (required, without r/ prefix)
- `--timeframe`: Time period (hour, day, week, month, year, all) - default: month
- `--sort`: Sort method (top, new, hot, rising, controversial) - default: top
- `--limit`: Number of posts to fetch - default: 30
- `--trim`: Use trimmed response for faster/lighter data (optional flag)

### Output

The script generates two files in `data/reddit/`:

1. **Raw JSON**: `{subreddit}_{sort}_{timeframe}_{timestamp}.json`
   - Complete API response with all post data
   - Preserved for detailed analysis
   - Not loaded into Claude context

2. **Summary**: `{subreddit}_summary.md`
   - Lightweight markdown with key metrics
   - Token-efficient for Claude analysis
   - Lists titles, scores, comments, upvote ratios

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
python scripts/fetch_reddit_posts.py --subreddit wallstreetbets --sort controversial --limit 20
```
