# Troubleshooting Guide

Common issues and solutions for the Web Scraper Dashboard.

## 🚨 Common Issues

### Backend Issues

#### 1. Python Virtual Environment Issues

**Problem**: `python -m venv venv` fails
**Solutions**:
\`\`\`bash
# Try with python3
python3 -m venv venv

# On Ubuntu/Debian, install venv
sudo apt-get install python3-venv

# On macOS with Homebrew
brew install python
\`\`\`

#### 2. Dependencies Installation Fails

**Problem**: `pip install -r requirements.txt` fails
**Solutions**:
\`\`\`bash
# Upgrade pip first
pip install --upgrade pip

# Install with verbose output to see errors
pip install -r requirements.txt -v

# Try installing dependencies one by one
pip install fastapi uvicorn requests beautifulsoup4
\`\`\`

#### 3. Google Auth Library Issues

**Problem**: `google-auth` installation fails
**Solutions**:
\`\`\`bash
# Install build tools (Ubuntu/Debian)
sudo apt-get install build-essential python3-dev

# Install build tools (macOS)
xcode-select --install

# Install with no cache
pip install --no-cache-dir google-auth
\`\`\`
