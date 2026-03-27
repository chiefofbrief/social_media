import os
import json
import requests
import sys

def get_tiktok_video_info(url):
    """
    Fetches TikTok video information using the SociaVault API.
    Saves the full JSON response to the 'data' folder.
    """
    api_key = os.environ.get("SOCIAVAULT_API_KEY")
    if not api_key:
        print("Error: SOCIAVAULT_API_KEY environment variable not set.")
        return

    print(f"Fetching info (including transcript) for: {url}")
    
    response = requests.get(
        "https://api.sociavault.com/v1/scrape/tiktok/video-info",
        headers={"X-API-Key": api_key},
        params={
            "url": url,
            "get_transcript": True,  # Enabled to fetch the video text
            "trim": True
        }
    )

    if response.status_code == 200:
        data = response.json()
        
        # Ensure 'data' directory exists for storage
        os.makedirs("data", exist_ok=True)
        
        # Save structured output to data folder
        file_path = "data/tiktok_video_info.json"
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
            
        print(f"Success! Data saved to {file_path}")
        
        # Display key summary info
        if 'data' in data and 'aweme_detail' in data['data']:
            detail = data['data']['aweme_detail']
            print(f"Description: {detail.get('desc')}")
            
        if 'data' in data and data['data'].get('transcript'):
            print("Transcript retrieved successfully.")
        else:
            print("Note: Transcript was not available for this video.")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    # URL is mandatory as the first argument
    if len(sys.argv) < 2:
        print("Usage: python3 tiktok_video_info.py <TIKTOK_URL>")
        print("Example: python3 tiktok_video_info.py https://www.tiktok.com/t/ZP8bbhvaG/")
        sys.exit(1)
        
    video_url = sys.argv[1]
    get_tiktok_video_info(video_url)
