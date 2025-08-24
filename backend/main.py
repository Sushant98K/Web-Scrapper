from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
from dotenv import load_dotenv
from auth import verify_google_token, create_jwt_token, get_current_user

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Web Scraper API", version="1.0.0")

origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]

# Enable CORS (for local React frontend development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Vite/React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# Pydantic Models (Data Schemas)
# ----------------------------

class ScrapedItem(BaseModel):
    """Represents a single scraped item (news, quote, etc.)."""
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    timestamp: str

class ScrapeResponse(BaseModel):
    """Standardized response format for scraping endpoints."""
    success: bool
    data: List[ScrapedItem]
    message: str
    scraped_at: str

class ScrapeRequest(BaseModel):
    """Request payload for scraping data."""
    url: str
    scrape_type: str = "news"  # Supported: news, quotes, products, weather

# Authentication models
class GoogleAuthRequest(BaseModel):
    """Request payload containing Google OAuth token."""
    token: str

class AuthResponse(BaseModel):
    """Response format after successful/failed authentication."""
    success: bool
    token: str
    user: dict
    message: str

# ----------------------------
# Utility Routes
# ----------------------------

@app.get("/")
async def root():
    """Root endpoint to confirm API is running."""
    return {"message": "Web Scraper API is running!"}

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring service availability."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# ----------------------------
# Scraping Functions
# ----------------------------

def scrape_news_headlines():
    """Scrape top BBC News headlines (respects robots.txt)."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get('https://www.bbc.com/news', headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []

        # Extract top news articles
        news_items = soup.find_all('div', {'data-testid': 'liverpool-card'})[:10]

        for item in news_items:
            try:
                title_elem = item.find('h2')
                if title_elem:
                    title = title_elem.get_text(strip=True)

                    desc_elem = item.find('p')
                    description = desc_elem.get_text(strip=True) if desc_elem else ""

                    link_elem = item.find('a')
                    url = f"https://www.bbc.com{link_elem.get('href')}" if link_elem else ""

                    articles.append(ScrapedItem(
                        title=title,
                        description=description,
                        url=url,
                        timestamp=datetime.now().isoformat()
                    ))
            except Exception:
                continue

        return articles

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scraping news: {str(e)}")


def scrape_hacker_news():
    """Scrape latest stories from Hacker News front page."""
    try:
        response = requests.get('https://news.ycombinator.com/', timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []

        story_rows = soup.find_all('tr', class_='athing')[:15]

        for row in story_rows:
            try:
                title_elem = row.find('span', class_='titleline')
                if title_elem:
                    title_link = title_elem.find('a')
                    if title_link:
                        title = title_link.get_text(strip=True)
                        url = title_link.get('href', '')

                        # Convert relative links to absolute URLs
                        if url.startswith('item?'):
                            url = f"https://news.ycombinator.com/{url}"

                        articles.append(ScrapedItem(
                            title=title,
                            description="Hacker News Story",
                            url=url,
                            timestamp=datetime.now().isoformat()
                        ))
            except Exception:
                continue

        return articles

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scraping Hacker News: {str(e)}")


def scrape_quotes():
    """Scrape quotes from quotes.toscrape.com."""
    try:
        response = requests.get("https://quotes.toscrape.com/", timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        quotes_data = []

        quotes = soup.find_all("div", class_="quote")[:10]
        for q in quotes:
            try:
                text_elem = q.find("span", class_="text")
                author_elem = q.find("small", class_="author")

                if text_elem and author_elem:
                    quotes_data.append(ScrapedItem(
                        title=text_elem.get_text(strip=True),
                        description=f"By {author_elem.get_text(strip=True)}",
                        url="https://quotes.toscrape.com/",
                        timestamp=datetime.now().isoformat()
                    ))
            except Exception:
                continue

        return quotes_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scraping quotes: {str(e)}")

# ----------------------------
# Authentication Endpoints
# ----------------------------

@app.post("/auth/google", response_model=AuthResponse)
async def google_auth(auth_request: GoogleAuthRequest):
    """Authenticate user with Google OAuth token and issue JWT."""
    try:
        user_data = verify_google_token(auth_request.token)
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
    """Retrieve info about the currently authenticated user."""
    return {"success": True, "user": current_user}

# ----------------------------
# Scraping Endpoints (Protected)
# ----------------------------

@app.post("/scrape", response_model=ScrapeResponse)
async def scrape_data(request: ScrapeRequest, current_user: dict = Depends(get_current_user)):
    """General scraping endpoint (requires authentication)."""
    try:
        scraped_data = []

        if request.scrape_type == "news":
            if "bbc.com" in request.url.lower():
                scraped_data = scrape_news_headlines()
            elif "news.ycombinator.com" in request.url.lower():
                scraped_data = scrape_hacker_news()
            else:
                scraped_data = scrape_hacker_news()

        elif request.scrape_type == "quotes":
            scraped_data = scrape_quotes()

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
    """Quick endpoint to scrape news headlines (Hacker News)."""
    try:
        scraped_data = scrape_hacker_news()
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


@app.get("/scrape/quotes", response_model=ScrapeResponse)
async def quick_scrape_quotes(current_user: dict = Depends(get_current_user)):
    """Quick endpoint to scrape quotes."""
    try:
        scraped_data = scrape_quotes()
        return ScrapeResponse(
            success=True,
            data=scraped_data,
            message=f"Successfully scraped {len(scraped_data)} quotes",
            scraped_at=datetime.now().isoformat()
        )
    except Exception as e:
        return ScrapeResponse(
            success=False,
            data=[],
            message=f"Error: {str(e)}",
            scraped_at=datetime.now().isoformat()
        )

# ----------------------------
# App Entry Point
# ----------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
