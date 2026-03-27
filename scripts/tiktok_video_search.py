import os
import json
import requests
import argparse
import sys
import re

def search_tiktok_videos(query, date_posted="yesterday", sort_by="most-liked", region="US"):
    """
    Searches for TikTok videos by keyword using the SociaVault API.
    Saves the JSON response to the 'data' folder.
    """
    api_key = os.environ.get("SOCIAVAULT_API_KEY")
    if not api_key:
        print("Error: SOCIAVAULT_API_KEY environment variable not set.")
        return

    print(f"Searching for: '{query}'")
    print(f"Parameters: date_posted={date_posted}, sort_by={sort_by}, region={region}")
    
    response = requests.get(
        "https://api.sociavault.com/v1/scrape/tiktok/search/keyword",
        headers={"X-API-Key": api_key},
        params={
            "query": query,
            "date_posted": date_posted,
            "sort_by": sort_by,
            "region": region,
            "trim": True
        }
    )

    if response.status_code == 200:
        data = response.json()
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Create a filename-safe slug from the query
        slug = re.sub(r'[^\w\s-]', '', query).strip().lower()
        slug = re.sub(r'[-\s]+', '_', slug)
        
        file_path = f"data/tiktok_search_{slug}.json"
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
            
        print(f"Success! Search results saved to {file_path}")
        
        # Summary of results
        # The API can return search_item_list as a list or a dict with numeric keys
        raw_items = data.get('data', {}).get('search_item_list', [])
        if isinstance(raw_items, dict):
            # Sort by keys if they are numeric strings to maintain order
            sorted_keys = sorted(raw_items.keys(), key=lambda x: int(x) if x.isdigit() else x)
            items = [raw_items[k] for k in sorted_keys]
        else:
            items = raw_items

        print(f"Found {len(items)} videos.")
        
        if items:
            print("\nTop Result:")
            first_item = items[0].get('aweme_info', {})
            print(f"- Description: {first_item.get('desc')}")
            print(f"- Author: {first_item.get('author', {}).get('unique_id')}")
            print(f"- Views: {first_item.get('statistics', {}).get('play_count')}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search TikTok videos by keyword.")
    parser.add_argument("query", help="The keyword or phrase to search for")
    parser.add_argument("--date", default="yesterday", choices=["yesterday", "this-week", "this-month", "last-3-months", "last-6-months", "all-time"], help="Time frame (default: yesterday)")
    parser.add_argument("--sort", default="most-liked", choices=["relevance", "most-liked", "date-posted"], help="Sort order (default: most-liked)")
    parser.add_argument("--region", default="US", help="Region code (default: US)")
    
    args = parser.parse_args()
    search_tiktok_videos(args.query, date_posted=args.date, sort_by=args.sort, region=args.region)
