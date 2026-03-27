import os
import json
import requests
import argparse
import sys

def get_popular_hashtags(period=7, pages=5, country="US", new_only=False):
    """
    Fetches the list of popular hashtags from TikTok via SociaVault.
    Saves the full list to the 'data' folder.
    """
    api_key = os.environ.get("SOCIAVAULT_API_KEY")
    if not api_key:
        print("Error: SOCIAVAULT_API_KEY environment variable not set.")
        return

    print(f"Fetching popular hashtags for {country} (Period: {period} days)...")
    if new_only:
        print("Filtering for: Newly Trending only.")
    
    all_hashtags = []
    
    for page in range(1, pages + 1):
        print(f"Requesting Page {page}...")
        response = requests.get(
            "https://api.sociavault.com/v1/scrape/tiktok/hashtags/popular",
            headers={"X-API-Key": api_key},
            params={
                "period": period,
                "page": page,
                "countryCode": country,
                "newOnBoard": new_only
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            # The API returns a dictionary where keys are strings "0", "1", etc.
            list_data = data.get("data", {}).get("list", {})
            
            if isinstance(list_data, dict):
                # Sort by numeric keys to maintain order
                sorted_keys = sorted(list_data.keys(), key=lambda x: int(x) if x.isdigit() else x)
                page_items = [list_data[k] for k in sorted_keys]
            else:
                page_items = list_data

            if not page_items:
                print("No more hashtags found.")
                break
                
            all_hashtags.extend(page_items)
            
            # Check if there are more pages according to API metadata
            pagination = data.get("data", {}).get("pagination", {})
            if not pagination.get("has_more"):
                print("End of results reached (has_more is false).")
                break
        else:
            print(f"Error on page {page}: {response.status_code}")
            print(response.text)
            break

    if all_hashtags:
        # Save to data folder
        os.makedirs("data", exist_ok=True)
        file_path = "data/tiktok_popular_hashtags.json"
        with open(file_path, "w") as f:
            json.dump(all_hashtags, f, indent=2)
            
        print(f"\nSuccess! Total {len(all_hashtags)} hashtags saved to {file_path}")
        
        # Display Top 10 Summary
        print("\nTop 10 Popular Hashtags:")
        print(f"{'Rank':<5} {'Hashtag':<25} {'Views':<15} {'Industry'}")
        print("-" * 65)
        for h in all_hashtags[:10]:
            rank = h.get('rank', '-')
            name = f"#{h.get('hashtag_name')}"
            views = h.get('video_views', 0)
            industry = h.get('industry_info', {}).get('value', 'N/A')
            print(f"{rank:<5} {name:<25} {views:<15,} {industry}")
    else:
        print("No hashtags found.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch popular TikTok hashtags.")
    parser.add_argument("--period", type=int, default=7, choices=[7, 30, 120], help="Time period in days (default: 7)")
    parser.add_argument("--pages", type=int, default=5, help="Number of pages to fetch (default: 5, ~100 hashtags)")
    parser.add_argument("--country", default="US", help="Country code (default: US)")
    parser.add_argument("--new", action="store_true", help="Show only newly trending hashtags")
    
    args = parser.parse_args()
    get_popular_hashtags(period=args.period, pages=args.pages, country=args.country, new_only=args.new)
