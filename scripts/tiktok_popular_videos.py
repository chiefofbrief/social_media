import os
import json
import requests
import argparse
import sys

def get_popular_videos(period=7, pages=1, order_by="hot", country="US"):
    """
    Fetches the list of popular videos from TikTok via SociaVault.
    Saves the full list to the 'data' folder.
    """
    api_key = os.environ.get("SOCIAVAULT_API_KEY")
    if not api_key:
        print("Error: SOCIAVAULT_API_KEY environment variable not set.")
        return

    print(f"Fetching popular videos for {country} (Period: {period} days, Sort: {order_by})...")
    
    all_videos = []
    
    for page in range(1, pages + 1):
        print(f"Requesting Page {page}...")
        response = requests.get(
            "https://api.sociavault.com/v1/scrape/tiktok/videos/popular",
            headers={"X-API-Key": api_key},
            params={
                "period": period,
                "page": page,
                "orderBy": order_by,
                "countryCode": country
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            # API returns videos as a dict with numeric keys "0", "1", etc.
            raw_videos = data.get("data", {}).get("videos", {})
            
            if isinstance(raw_videos, dict):
                sorted_keys = sorted(raw_videos.keys(), key=lambda x: int(x) if x.isdigit() else x)
                page_items = [raw_videos[k] for k in sorted_keys]
            else:
                page_items = raw_videos

            if not page_items:
                print("No more videos found.")
                break
                
            all_videos.extend(page_items)
            
            pagination = data.get("data", {}).get("pagination", {})
            if not pagination.get("has_more"):
                print("End of results reached (has_more is false).")
                break
        else:
            print(f"Error on page {page}: {response.status_code}")
            print(response.text)
            break

    if all_videos:
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        file_path = "data/tiktok_popular_videos.json"
        with open(file_path, "w") as f:
            json.dump(all_videos, f, indent=2)
            
        print(f"\nSuccess! Total {len(all_videos)} videos saved to {file_path}")
        
        # Display Summary
        print("\nTop Popular Videos:")
        print(f"{'#':<3} {'Title':<60} {'Duration'}")
        print("-" * 75)
        for i, v in enumerate(all_videos[:20], 1):
            title = v.get('title', 'No Title').strip().replace('\n', ' ')
            if len(title) > 57:
                title = title[:57] + "..."
            duration = v.get('duration', 0)
            print(f"{i:<3} {title:<60} {duration}s")
    else:
        print("No videos found.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch popular TikTok videos.")
    parser.add_argument("--period", type=int, default=7, choices=[7, 30], help="Time period in days (7 or 30, default: 7)")
    parser.add_argument("--pages", type=int, default=1, help="Number of pages to fetch (default: 1, 10 videos per page)")
    parser.add_argument("--order", default="hot", choices=["like", "hot", "comment", "repost"], help="Sort order (default: hot/views)")
    parser.add_argument("--country", default="US", help="Country code (default: US)")
    
    args = parser.parse_args()
    get_popular_videos(period=args.period, pages=args.pages, order_by=args.order, country=args.country)
