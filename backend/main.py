from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import os
from dotenv import load_dotenv
from auth import verify_google_token, create_jwt_token, get_current_user

load_dotenv()

app = FastAPI(title="Web Scraper API", version="1.0.0")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ScrapedItem(BaseModel):
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    timestamp: str

class ScrapeResponse(BaseModel):
    success: bool
    data: List[ScrapedItem]
    message: str
    scraped_at: str

class ScrapeRequest(BaseModel):
    url: str
    scrape_type: str = "news"  # news, products, weather

# Authentication models
class GoogleAuthRequest(BaseModel):
    token: str

class AuthResponse(BaseModel):
    success: bool
    token: str
    user: dict
    message: str

@app.get("/")
async def root():
    return {"message": "Web Scraper API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

def scrape_news_headlines():
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # BBC News allows scraping according to robots.txt
        response = requests.get('https://www.bbc.com/news', headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        
        # Find news articles
        news_items = soup.find_all('div', {'data-testid': 'liverpool-card'})[:10]
        
        for item in news_items:
            try:
                title_elem = item.find('h2')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    
                    # Try to find description
                    desc_elem = item.find('p')
                    description = desc_elem.get_text(strip=True) if desc_elem else ""
                    
                    # Try to find URL
                    link_elem = item.find('a')
                    url = f"https://www.bbc.com{link_elem.get('href')}" if link_elem and link_elem.get('href') else ""
                    
                    articles.append(ScrapedItem(
                        title=title,
                        description=description,
                        url=url,
                        timestamp=datetime.now().isoformat()
                    ))
            except Exception as e:
                continue
        
        return articles
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scraping news: {str(e)}")

def scrape_hacker_news():
    
    try:
        response = requests.get('https://news.ycombinator.com/', timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        
        # Find story rows
        story_rows = soup.find_all('tr', class_='athing')[:15]
        
        for row in story_rows:
            try:
                title_elem = row.find('span', class_='titleline')
                if title_elem:
                    title_link = title_elem.find('a')
                    if title_link:
                        title = title_link.get_text(strip=True)
                        url = title_link.get('href', '')
                                                
                        if url.startswith('item?'):
                            url = f"https://news.ycombinator.com/{url}"
                        
                        articles.append(ScrapedItem(
                            title=title,
                            description="Hacker News Story",
                            url=url,
                            timestamp=datetime.now().isoformat()
                        ))
            except Exception as e:
                continue
        
        return articles
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scraping Hacker News: {str(e)}")

# Authentication endpoints
@app.post("/auth/google", response_model=AuthResponse)
async def google_auth(auth_request: GoogleAuthRequest):
    
    try:
        # Verify Google token
        user_data = verify_google_token(auth_request.token)
        
        # Create JWT token
        jwt_token = create_jwt_token(user_data)
        
        return AuthResponse(
            success=True,
            token=jwt_token,
            user={
                'id': user_data['sub'],
                'email': user_data['email'],
                'name': user_data['name'],
                'picture': user_data['picture']
            },
            message="Authentication successful"
        )
    
    except Exception as e:
        return AuthResponse(
            success=False,
            token="",
            user={},
            message=f"Authentication failed: {str(e)}"
        )

@app.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    
    return {
        "success": True,
        "user": current_user
    }

@app.post("/scrape", response_model=ScrapeResponse)
async def scrape_data(request: ScrapeRequest, current_user: dict = Depends(get_current_user)):
    
    try:
        scraped_data = []
        
        if request.scrape_type == "news":
            if "bbc.com" in request.url.lower():
                scraped_data = scrape_news_headlines()
            elif "news.ycombinator.com" in request.url.lower():
                scraped_data = scrape_hacker_news()
            else:
                scraped_data = scrape_hacker_news()
        
        return ScrapeResponse(
            success=True,
            data=scraped_data,
            message=f"Successfully scraped {len(scraped_data)} items",
            scraped_at=datetime.now().isoformat()
        )
    
    except Exception as e:
        return ScrapeResponse(
            success=False,
            data=[],
            message=f"Error: {str(e)}",
            scraped_at=datetime.now().isoformat()
        )

@app.get("/scrape/news", response_model=ScrapeResponse)
async def quick_scrape_news(current_user: dict = Depends(get_current_user)):
    
    try:
        scraped_data = scrape_hacker_news()  # Using Hacker News as it's more reliable
        
        return ScrapeResponse(
            success=True,
            data=scraped_data,
            message=f"Successfully scraped {len(scraped_data)} news items",
            scraped_at=datetime.now().isoformat()
        )
    
    except Exception as e:
        return ScrapeResponse(
            success=False,
            data=[],
            message=f"Error: {str(e)}",
            scraped_at=datetime.now().isoformat()
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
