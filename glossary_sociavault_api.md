# SociaVault API Analysis: Reddit Strategic Implementation

This document outlines the capabilities, strategic approach, and cost-optimization logic for using the SociaVault API to perform Reddit conversation analysis and trend tracking.

---

## 1. Core Capability Assessment
* **Access Type:** Read-Only data extraction. No "POST" or "WRITE" capabilities exist for Reddit.
* **Authentication:** API Key required via `X-API-Key` header.
* **Format:** Standard REST API returning JSON (Full and Trimmed versions available).
* **Pricing Model:** One-time Credit Packs; credits never expire.

---

## 2. Strategic Implementation Flow

For monitoring "conversations" (Top Posts + Top Comments), the following multi-step logic is recommended to ensure data freshness while minimizing credit usage.

### Goal A: Identify Trending Topics (Last 48 Hours)
1.  **Request:** `GET /v1/scrape/reddit/subreddit`
    * **Params:** `timeframe: week`, `sort: new`, `trim: true`
2.  **Application Logic:**
    * SociaVault's finest granularity is `day` (24h). To get exactly 48 hours, pull the `week` timeframe and filter results locally using the `created_utc` Unix timestamp.
    * **Ranking:** After filtering for time, sort the remaining posts by `score` or `num_comments` to identify the true "trends" of that 48-hour window.

### Goal B: Topic-Specific Commentary (e.g., Amazon Stock)
1.  **Request:** `GET /v1/scrape/reddit/search`
    * **Query Suggestion:** `(AMZN OR "Amazon") (stock OR price OR earnings)`
    * **Params:** `timeframe: week`, `sort: relevance`
2.  **Enrichment:** Use results from this search to feed the comment extraction endpoints.

---

## 3. Data Extraction Guide

| Endpoint | Use Case | Cost | Pro Tip |
| :--- | :--- | :--- | :--- |
| `/v1/scrape/reddit/subreddit` | Identifying subreddit trends. | 1 Credit | Returns ~25 posts per page. Use `trim: true` for faster discovery. Use `after` parameter for pagination. |
| `/v1/scrape/reddit/search` | Tracking specific keywords/tickers. | 1 Credit | Support Boolean operators in the `query`. |
| `/v1/scrape/reddit/post/comments/simple` | High-volume sentiment/flat lists. | 1 Credit / 48 items | **Always set `amount: 48`** to maximize data per credit. |
| `/v1/scrape/reddit/post/comments` | Threaded conversation analysis. | 1 Credit | Best for understanding reply-chains and arguments. |
| `/v1/credits` | Monitoring balance. | **0 Credits** | Call this at the start of every script to prevent 402 errors. |

### Subreddit Endpoint Details
**Parameters:**
- `subreddit` (required): Subreddit name without r/ prefix
- `timeframe` (optional): hour, day, week, month, year, all
- `sort` (optional): top, new, hot, rising, controversial, best
- `after` (optional): Pagination token from previous response
- `trim` (optional): Set to `true` for lightweight response

**Response Structure:**
```json
{
  "success": true,
  "data": {
    "posts": {
      "0": { /* post object */ },
      "1": { /* post object */ },
      ...
    }
  },
  "after": "t3_abc123"  // Use this for next page
}
```

**Pagination Strategy:**
- Default: ~25 posts per request
- To fetch more: Use the `after` token from response in next request
- Cost: 1 credit per page (not per post)
- For 50 posts: 2 requests = 2 credits
- For 100 posts: 4 requests = 4 credits

---

## 4. Cost Reduction & Optimization
To prevent "credit bleeding," implement these programmatic safeguards:

* **The "Gatekeeper" Filter:** Do not automate comment scraping for every post found. Only call comment endpoints if the post meets a threshold (e.g., `num_comments > 10` or `upvote_ratio > 0.85`).
* **Boolean Clumping:** Combine related keywords into a single search query (e.g., `AMZN OR "Amazon Stock"`) to avoid making multiple 1-credit requests.
* **Trim Parameter:** Use `trim: true` for the discovery phase (listing posts). Switch to `trim: false` only when you need deep metrics like `upvote_ratio` or `num_crossposts` for final analysis.

---

## 5. Pricing Baseline (Starter Pack)
* **Investment:** $29 (one-time).
* **Credits:** 6,000 (~$0.0048 per credit).
* **Sample Lifetime:** Pulling 10 subreddits and the top 10 comment threads for each daily (~20 credits/day) would allow this pack to last for **~300 days**.

---

## 6. Response Fields for Analysis
Key fields in the SociaVault response schema to focus on:

### Post Fields
* `created_utc`: Essential for the 48-hour window filter (Unix timestamp).
* `score`: Net upvotes (upvotes minus downvotes) - primary ranking metric.
* `upvote_ratio`: Vital to distinguish "viral positive trends" from "controversial/divisive topics" (0.0-1.0).
* `num_comments`: Best indicator of active "conversation" vs. passive content consumption.
* `is_self`: `true` for text posts, `false` for links/images.
* `is_video`: `true` for video posts (Reddit-hosted or external).
* `selftext`: Post body text (empty string for link posts).
* `url`: Post URL (self-posts link to Reddit, others to external URLs).
* `title`: Post title (max ~300 chars, typically much shorter).
* `author`: Username of poster.
* `subreddit`: Subreddit name without r/ prefix.
* `permalink`: Reddit-relative URL path for the post.

### Comment Fields
* `parent_id` (in Standard Comments): Used to reconstruct the structure of a discussion.
* `body`: Comment text content.
* `score`: Comment score (upvotes - downvotes).
