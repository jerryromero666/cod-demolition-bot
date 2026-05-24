import os
import tweepy
import requests
from bs4 import BeautifulSoup
import asyncio
import re
from dotenv import load_dotenv  # Tool to read hidden local keys

# Load local .env file if it exists (for running securely on your PC)
load_dotenv()

# Safely pulling keys (No hardcoded plaintext keys here anymore!)
API_KEY = os.getenv("API_KEY")
API_KEY_SECRET = os.getenv("API_KEY_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

TARGET_ACCOUNTS = ["CallofDuty", "Treyarch", "CallofDutyCM", "MaTtKs," "Activision", "CODUpdates", "ATVI_AB"]
REPLY_MESSAGE = "Bring DEMOLITION to HARDCORE in BO7 PLEASE!!!! We're still stuck playing Cold War to enjoy HC Demo - there's DOZENS OF US!!!! PLzzzZzzZ <3"

last_seen_tweets = {account: None for account in TARGET_ACCOUNTS}

def reply_to_tweet(tweet_id):
    try:
        client = tweepy.Client(
            consumer_key=API_KEY, consumer_secret=API_KEY_SECRET,
            access_token=ACCESS_TOKEN, access_token_secret=ACCESS_TOKEN_SECRET
        )
        response = client.create_tweet(text=REPLY_MESSAGE, in_reply_to_tweet_id=tweet_id)
        print(f" Successfully replied to tweet {tweet_id}!")
    except Exception as e:
        print(f"❌ Failed to send reply: {e}")

async def check_for_new_tweets():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    for account in TARGET_ACCOUNTS:
        try:
            print(f"Checking @{account}...")
            # Search Google for the latest index of this specific user's status updates
            search_url = f"https://www.google.com/search?q=site:x.com/{account}/status/"
            response = requests.get(search_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Find all URLs matching an X status ID link
                links = soup.find_all('a', href=True)
                tweet_ids = []
                
                for link in links:
                    href = link['href']
                    match = re.search(r'x\.com/' + account + r'/status/(\d+)', href)
                    if match:
                        tweet_ids.append(match.group(1))
                
                if tweet_ids:
                    # The highest ID or first ID returned represents their latest post
                    latest_id = max(tweet_ids) 
                    
                    # First run initialization
                    if last_seen_tweets[account] is None:
                        last_seen_tweets[account] = latest_id
                        print(f"Bookmarked latest tweet for @{account}: {latest_id}")
                        continue
                    
                    # If they dropped a newer tweet id
                    if int(latest_id) > int(last_seen_tweets[account]):
                        print(f"🚨 NEW TWEET DETECTED from @{account}!")
                        last_seen_tweets[account] = latest_id
                        reply_to_tweet(latest_id)
            else:
                print(f"⚠️ Google search query throttled (Status {response.status_code})")
                
        except Exception as e:
            print(f"Error checking @{account}: {e}")

async def main():
    print("🤖 Campaign Bot active. Monitoring CoD channels...")
    while True:
        await check_for_new_tweets()
        print("Waiting 60 seconds before next check...\n")
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
