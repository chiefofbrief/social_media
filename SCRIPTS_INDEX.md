# TikTok Data Scraping Scripts Index

This document provides an overview of the available Python scripts for scraping TikTok data, including their purpose, usage, and parameters. All scripts are located in the `scripts/` directory and interact with the SociaVault API.

---

## 1. `tiktok_video_info.py`

**Purpose**: Fetches comprehensive information about a single TikTok video, including its description, author, various metadata, and attempts to retrieve the transcript.

**Location**: `scripts/tiktok_video_info.py`

**Usage**:
```bash
python3 scripts/tiktok_video_info.py <TIKTOK_URL> [--use-ai]
```

**Parameters**:
*   `<TIKTOK_URL>` (positional, **required**): The full URL of the TikTok video to fetch.
    *   Example: `https://www.tiktok.com/t/ZP8bbhvaG/`
*   `--use-ai` (optional flag): If present, enables AI fallback for transcript retrieval. This costs 10 credits instead of 1 if the AI fallback is triggered. Defaults to `False`.

**Output**: Saves the full JSON response to `data/tiktok_video_info.json`.

---

## 2. `tiktok_video_transcript.py`

**Purpose**: Fetches the transcript for a specific TikTok video using a dedicated transcript endpoint, which is more reliable for transcript retrieval than the video info endpoint.

**Location**: `scripts/tiktok_video_transcript.py`

**Usage**:
```bash
python3 scripts/tiktok_video_transcript.py <TIKTOK_URL> [--use-ai]
```

**Parameters**:
*   `<TIKTOK_URL>` (positional, **required**): The full URL of the TikTok video to fetch the transcript for.
    *   Example: `https://www.tiktok.com/t/ZP8bbhvaG/`
*   `--use-ai` (optional flag): If present, enables AI fallback for transcript retrieval. This costs 10 credits instead of 1 if the AI fallback is triggered. Defaults to `False`.

**Output**: Saves the full JSON response to `data/tiktok_transcript.json`.

---

## 3. `tiktok_video_search.py`

**Purpose**: Searches for TikTok videos based on a keyword or phrase, allowing filtering by time frame, sorting criteria, and region.

**Location**: `scripts/tiktok_video_search.py`

**Usage**:
```bash
python3 scripts/tiktok_video_search.py <QUERY> [--date <TIME_FRAME>] [--sort <ORDER_BY>] [--region <COUNTRY_CODE>]
```

**Parameters**:
*   `<QUERY>` (positional, **required**): The keyword or phrase to search for.
    *   Example: `"stock market news"`
*   `--date` (optional): Time frame for the search.
    *   Options: `yesterday`, `this-week`, `this-month`, `last-3-months`, `last-6-months`, `all-time`
    *   **Default**: `yesterday`
*   `--sort` (optional): Sort order for the results.
    *   Options: `relevance`, `most-liked`, `date-posted`
    *   **Default**: `most-liked`
*   `--region` (optional): 2-letter country code for the proxy region.
    *   **Default**: `US`

**Output**: Saves the full JSON response to `data/tiktok_search_<query_slug>.json` (e.g., `data/tiktok_search_stock_market_news.json`).

---

## 4. `tiktok_popular_hashtags.py`

**Purpose**: Fetches a list of currently popular/trending hashtags on TikTok, filtered by time period, number of pages, country, and option for newly trending hashtags.

**Location**: `scripts/tiktok_popular_hashtags.py`

**Usage**:
```bash
python3 scripts/tiktok_popular_hashtags.py [--period <DAYS>] [--pages <NUM_PAGES>] [--country <COUNTRY_CODE>] [--new]
```

**Parameters**:
*   `--period` (optional): Time period in days for trending data.
    *   Options: `7`, `30`, `120`
    *   **Default**: `7`
*   `--pages` (optional): Number of pages of hashtags to fetch (approx. 20 hashtags per page).
    *   **Default**: `5` (fetches ~100 hashtags)
*   `--country` (optional): 2-letter country code for the region.
    *   **Default**: `US`
*   `--new` (optional flag): If present, filters to show only newly trending hashtags.

**Output**: Saves the full list of hashtags as a JSON array to `data/tiktok_popular_hashtags.json`.

---

## 5. `tiktok_popular_videos.py`

**Purpose**: Fetches a list of currently popular videos on TikTok, filtered by time period, number of pages, sorting criteria, and country.

**Location**: `scripts/tiktok_popular_videos.py`

**Usage**:
```bash
python3 scripts/tiktok_popular_videos.py [--period <DAYS>] [--pages <NUM_PAGES>] [--order <ORDER_BY>] [--country <COUNTRY_CODE>]
```

**Parameters**:
*   `--period` (optional): Time period in days for popular video data.
    *   Options: `7`, `30`
    *   **Default**: `7`
*   `--pages` (optional): Number of pages of videos to fetch (10 videos per page).
    *   **Default**: `1` (fetches 10 videos)
*   `--order` (optional): Sort order for the results.
    *   Options: `like`, `hot` (views), `comment`, `repost`
    *   **Default**: `hot` (most views)
*   `--country` (optional): 2-letter country code for the region.
    *   **Default**: `US`

**Output**: Saves the full list of videos as a JSON array to `data/tiktok_popular_videos.json`.
