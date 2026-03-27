import os
import json
import requests
import argparse
import sys

def get_tiktok_transcript(url, use_ai=False):
    """
    Fetches the transcript for a TikTok video using the SociaVault API.
    Saves the JSON response to the 'data' folder.
    """
    api_key = os.environ.get("SOCIAVAULT_API_KEY")
    if not api_key:
        print("Error: SOCIAVAULT_API_KEY environment variable not set.")
        return

    print(f"Fetching transcript for: {url}")
    print(f"AI Fallback: {'Enabled (10 credits)' if use_ai else 'Disabled (1 credit)'}")
    
    response = requests.get(
        "https://api.sociavault.com/v1/scrape/tiktok/transcript",
        headers={"X-API-Key": api_key},
        params={
            "url": url,
            "language": "en",
            "use_ai_as_fallback": use_ai
        }
    )

    if response.status_code == 200:
        data = response.json()
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Save to data folder
        file_path = "data/tiktok_transcript.json"
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
            
        print(f"Success! Transcript saved to {file_path}")
        
        if 'data' in data and data['data'].get('transcript'):
            print("\nTranscript Preview:")
            # Show first 200 chars
            print(data['data']['transcript'][:200] + "...")
        else:
            print("Note: Transcript data was empty.")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch TikTok transcript.")
    # URL is mandatory in the format: https://www.tiktok.com/t/ZP8bbhvaG/
    parser.add_argument("url", help="The TikTok video URL")
    parser.add_argument("--use-ai", action="store_true", help="Enable AI fallback (costs 10 credits instead of 1)")
    
    args = parser.parse_args()
    get_tiktok_transcript(args.url, use_ai=args.use_ai)
