import requests
import json

def test_api():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Web Scraper API...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health Check: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return
    
    # Test news scraping
    try:
        response = requests.get(f"{base_url}/scrape/news")
        data = response.json()
        print(f"✅ News Scraping: {response.status_code}")
        print(f"   Success: {data['success']}")
        print(f"   Items scraped: {len(data['data'])}")
        
        if data['data']:
            print(f"   Sample item: {data['data'][0]['title'][:50]}...")
    except Exception as e:
        print(f"❌ News Scraping Failed: {e}")

if __name__ == "__main__":
    test_api()
