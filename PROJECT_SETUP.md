# Web Scraper - Project Setup

This is a full-stack application with separate frontend and backend:

## Frontend (React + Vite + JavaScript)

- **Location**: `frontend/` directory
- **Technology**: React 19, Vite, Tailwind CSS v4, JavaScript
- **Port**: http://localhost:5173

## Backend (FastAPI + Python)

- **Location**: `backend/` directory  
- **Technology**: FastAPI, Python 3.9+, BeautifulSoup4, Google OAuth
- **Port**: http://localhost:8000

## Quick Start

### Backend Setup

\`\`\`bash
cd backend
python 3.12 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
\`\`\`

### Frontend Setup

\`\`\`bash
cd frontend
npm install
npm run dev
\`\`\`

## Project Files

### Backend Structure

\`\`\`
backend/
├── main.py              # FastAPI application
├── auth.py              # Google OAuth & JWT handling
├── requirements.txt     # Python dependencies
├── run.py              # Server startup script
├── test_scraper.py     # Test script
└── .env                # Environment variables
\`\`\`

### Frontend Structure

\`\`\`
frontend/
├── src/
│   ├── components/
│   │   ├── Header.jsx
│   │   ├── Sidebar.jsx
│   │   ├── Login.jsx
│   │   ├── Dashboard.jsx
│   ├── context/
│   │   └── AuthContext.jsx
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── package.json
├── vite.config.js
└── .env.example
\`\`\`

## Features

- ✅ Google OAuth 2.0 Authentication
- ✅ Web Scraping (Hacker News, BBC News)
- ✅ Real-time Data Fetching
- ✅ Responsive Dashboard UI
- ✅ JWT Token Management
- ✅ Modern React with Hooks
- ✅ Tailwind CSS v4 Styling
