import uvicorn

if __name__ == "__main__":
    print("🚀 Starting Web Scraper API...")
    print("📡 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔄 Interactive API: http://localhost:8000/redoc")
    
    uvicorn.run(
        "main:app",  # Import string format enables proper reload and workers
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )
