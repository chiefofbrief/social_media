# GitHub Actions - Daily Reddit Summary

## Overview

This workflow automatically fetches top Reddit posts from r/ValueInvesting, r/stocks, and r/options every day.

## Setup Instructions

### 1. Add API Key as Secret

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `SOCIAVAULT_API_KEY`
5. Value: Your SociaVault API key (from https://sociavault.com/dashboard)
6. Click **Add secret**

### 2. Enable GitHub Actions

1. Go to **Actions** tab in your repository
2. If prompted, enable GitHub Actions for the repository
3. The workflow will appear as "Daily Reddit Top Posts"

### 3. Workflow Schedule

- **Automatic:** Runs daily at 9:00 AM UTC
- **Manual:** Can be triggered manually from the Actions tab:
  1. Go to **Actions** → **Daily Reddit Top Posts**
  2. Click **Run workflow** → **Run workflow**

## Output

The workflow generates a markdown summary organized by subreddit:
- **Top 10 posts per subreddit** (or fewer if less than 10 available)
- **Separate sections** for r/ValueInvesting, r/stocks, and r/options
- For each post: Title, upvotes, comments, body text (first 500 chars), and URL
- **Total: Up to 30 posts** (10 per subreddit)

### Viewing Results

**Option 1: Artifacts** (Recommended)
1. Go to **Actions** tab
2. Click on the latest workflow run
3. Scroll to **Artifacts** section
4. Download `daily-reddit-summary-XXX.md`

**Option 2: Workflow Logs**
1. Go to **Actions** tab
2. Click on the latest workflow run
3. Click on "Display summary in logs" step
4. View the summary directly in logs

## Cost

- **API Credits:** 3 credits per day (1 per subreddit)
- **GitHub Actions:** Free for public repositories, included minutes for private repos

## Customization

### Change Schedule

Edit `.github/workflows/daily-reddit-summary.yml`:

```yaml
schedule:
  - cron: '0 9 * * *'  # Change to your preferred time (UTC)
```

Common schedules:
- `'0 0 * * *'` - Midnight UTC
- `'0 12 * * *'` - Noon UTC
- `'0 */6 * * *'` - Every 6 hours

### Add More Subreddits

Edit the "Fetch top posts" step:

```yaml
- name: Fetch top posts from past day
  env:
    SOCIAVAULT_API_KEY: ${{ secrets.SOCIAVAULT_API_KEY }}
  run: |
    python scripts/fetch_reddit_posts.py --subreddit ValueInvesting --timeframe day --output-dir /tmp/reddit_data
    python scripts/fetch_reddit_posts.py --subreddit stocks --timeframe day --output-dir /tmp/reddit_data
    python scripts/fetch_reddit_posts.py --subreddit options --timeframe day --output-dir /tmp/reddit_data
    python scripts/fetch_reddit_posts.py --subreddit investing --timeframe day --output-dir /tmp/reddit_data  # ADD THIS
```

### Change Number of Posts Per Subreddit

Edit `scripts/generate_daily_summary.py` line 30:

```python
def generate_summary(posts, output_file, posts_per_subreddit=10):  # Change 10
```

This controls how many posts are shown for EACH subreddit (not total).
For example, `posts_per_subreddit=5` would show 5 posts from each subreddit (15 total).

## Troubleshooting

### Workflow Fails

**Check API Key:**
- Ensure `SOCIAVAULT_API_KEY` secret is set correctly
- Verify key is valid at https://sociavault.com/dashboard

**Check Credits:**
- Ensure you have at least 3 credits available
- Check credit balance in your SociaVault dashboard

**View Logs:**
1. Go to **Actions** → Click failed workflow
2. Click on failed job to see error details

### No Posts in Summary

- Posts may be empty if there are no new posts in the past day
- Try changing timeframe to `week` in the workflow file
