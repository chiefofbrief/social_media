# Social Media Research Scripts

Collection of scripts for researching stocks and topics across social media platforms using the SociaVault API.

## Available Scripts

- **[youtube_stock_research.py](#youtube_stock_researchpy)** - Research stock sentiment on YouTube with video analysis and transcripts
- **[tiktok_stock_research.py](#tiktok_stock_researchpy)** - Research stock sentiment on TikTok (FinTok) with video analysis and transcripts
- **[fetch_reddit_posts.py](#fetch_reddit_postspy)** - Fetch top posts from any subreddit

---

## youtube_stock_research.py

Searches YouTube for videos about specific stocks, retrieves video details including transcripts, and analyzes sentiment for stock research.

### Features

- 🔍 Search YouTube for stock tickers/companies
- 📅 Filter by time period (today, this_week, this_month, this_year, all_time)
- 📹 Fetch full video details including transcripts
- 📊 Automatic sentiment analysis (bullish/bearish/neutral)
- 💾 Saves structured JSON results with engagement metrics

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

Basic usage (searches "TICKER stock" for past month):
```bash
python scripts/youtube_stock_research.py TSLA
```

Custom search with time filter:
```bash
python scripts/youtube_stock_research.py AMZN --time-period this_week --max-videos 20
```

Custom query with specific search terms:
```bash
python scripts/youtube_stock_research.py NVDA --query "NVDA earnings analysis" --max-videos 15
```

Skip transcript fetching for faster results:
```bash
python scripts/youtube_stock_research.py MSFT --no-details
```

### Parameters

- `ticker` (required): Stock ticker symbol (e.g., TSLA, AMZN, NVDA)
- `--query`: Custom search query (overrides default "{ticker} stock" search)
- `--time-period`: Time filter - `last_hour`, `today`, `this_week`, `this_month` (default), `this_year`, `all_time`
- `--max-videos`: Maximum videos to fetch (default: 20)
- `--no-details`: Skip fetching video details and transcripts (faster but no sentiment analysis)
- `--output`: Custom output file path

### Output

The script saves results to `data/youtube/{TICKER}_{timeperiod}_{timestamp}.json` with:

- **Search metadata**: ticker, query, time period, timestamp
- **Video details**: title, description, channel info, views, likes, comments
- **Transcripts**: Full video transcripts with timestamps
- **Sentiment analysis**: Bullish/bearish/neutral classification based on keywords in title, description, and transcript
- **Summary statistics**: Total videos, views, engagement, sentiment breakdown

### Sentiment Analysis

Videos are analyzed for bullish/bearish sentiment using keyword detection:

- 🟢 **Bullish**: buy, bull, growth, profit, opportunity, breakout, rally, upgrade, outperform
- 🔴 **Bearish**: sell, bear, decline, loss, crash, warning, downgrade, weak, overvalued
- ⚪ **Neutral**: Neither sentiment dominates

### Cost

- **1 credit** per search request
- **1 credit** per video detail fetch (if `--no-details` not used)
- Example: `--max-videos 10` with details = ~11 credits total

### Examples

Research Tesla stock from today:
```bash
python scripts/youtube_stock_research.py TSLA --time-period today
```

Research Amazon with custom query:
```bash
python scripts/youtube_stock_research.py AMZN --query "Amazon AWS earnings Q4"
```

Quick search without transcripts (cheaper):
```bash
python scripts/youtube_stock_research.py NVDA --max-videos 30 --no-details
```

Research Apple over past year:
```bash
python scripts/youtube_stock_research.py AAPL --time-period this_year --max-videos 50
```

---

## tiktok_stock_research.py

Searches TikTok (FinTok) for videos about specific stocks, retrieves video details including transcripts, and analyzes sentiment for stock research.

### Features

- 🔍 Search TikTok for stock tickers/companies with keyword or hashtag
- 📅 Filter by time period (yesterday, this-week, this-month, last-3-months, last-6-months, all_time)
- 📹 Fetch full video details including transcripts
- 📊 Automatic sentiment analysis (bullish/bearish/neutral)
- 💾 Saves structured JSON results with engagement metrics
- 🔥 Sort by relevance, most-liked, or date-posted

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

Basic usage (searches "#{TICKER} stock" for past month):
```bash
python scripts/tiktok_stock_research.py TSLA
```

Custom search with time filter:
```bash
python scripts/tiktok_stock_research.py AMZN --query "Amazon stock news" --time-period this-week
```

Sort by most-liked videos:
```bash
python scripts/tiktok_stock_research.py NVDA --max-videos 30 --sort-by most-liked
```

Skip transcript fetching for faster results:
```bash
python scripts/tiktok_stock_research.py MSFT --no-details
```

### Parameters

- `ticker` (required): Stock ticker symbol (e.g., TSLA, AMZN, NVDA)
- `--query`: Custom search query (overrides default "#{ticker} stock" search)
- `--time-period`: Time filter - `yesterday`, `this-week`, `this-month` (default), `last-3-months`, `last-6-months`, `all_time`
- `--sort-by`: Sort method - `relevance` (default), `most-liked`, `date-posted`
- `--max-videos`: Maximum videos to fetch (default: 20)
- `--no-details`: Skip fetching video details and transcripts (faster but no sentiment analysis)
- `--output`: Custom output file path

### Output

The script saves results to `data/tiktok/{TICKER}_{timeperiod}_{timestamp}.json` with:

- **Search metadata**: ticker, query, time period, timestamp
- **Video details**: description, author info, views, likes, comments, shares
- **Transcripts**: Full video transcripts parsed from WEBVTT format
- **Sentiment analysis**: Bullish/bearish/neutral classification based on keywords in description and transcript
- **Summary statistics**: Total videos, views, engagement, sentiment breakdown

### Sentiment Analysis

Videos are analyzed for bullish/bearish sentiment using keyword detection:

- 🟢 **Bullish**: buy, bull, growth, profit, opportunity, breakout, rally, upgrade, outperform
- 🔴 **Bearish**: sell, bear, decline, loss, crash, warning, downgrade, weak, overvalued
- ⚪ **Neutral**: Neither sentiment dominates

### Cost

- **1 credit** per search request
- **1 credit** per video detail fetch (if `--no-details` not used)
- Example: `--max-videos 10` with details = ~11 credits total

### Examples

Research Tesla stock from this month (FinTok):
```bash
python scripts/tiktok_stock_research.py TSLA
```

Find most-liked videos about Amazon:
```bash
python scripts/tiktok_stock_research.py AMZN --sort-by most-liked --max-videos 30
```

Quick search without transcripts (cheaper):
```bash
python scripts/tiktok_stock_research.py NVDA --max-videos 50 --no-details
```

Search with custom query and hashtag:
```bash
python scripts/tiktok_stock_research.py AAPL --query "#AAPL stock analysis"
```

Research from past 3 months:
```bash
python scripts/tiktok_stock_research.py GME --time-period last-3-months --max-videos 40
```

---

## Reddit Data Collection Scripts

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
