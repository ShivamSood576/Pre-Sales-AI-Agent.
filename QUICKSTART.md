# Quick Start Guide

Get the AI RAG Chatbot running in 5 minutes!

## Prerequisites Check

- [ ] Python 3.10+ installed
- [ ] Redis installed
- [ ] Google Cloud account with Calendar API enabled
- [ ] Google OAuth credentials downloaded

## Step-by-Step Setup

### 1. Clone & Install (2 minutes)

```bash
# Clone the repository
git clone <your-repo-url>
cd <repo-name>

# Run the automated setup script
chmod +x setup.sh
./setup.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment (1 minute)

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your keys
# Required: GOOGLE_API_KEY (from Google AI Studio)
```

**Get Google API Key**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey)

### 3. Google Calendar Setup (1 minute)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project → Enable Calendar API → Create OAuth credentials
3. Download credentials → Save as `client_secret.json`

### 4. Add Documents (30 seconds)

```bash
# Place your PDF files
cp your-documents.pdf data/pdfs/

# Ingest into vector store
python ingest.py
```

### 5. Launch (30 seconds)

```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start the app
uvicorn app15_book:app --reload --port 8000
```

## Test It Out

Open your browser and visit:
- **API Docs**: http://localhost:8000/docs
- **Test Chat**:
  ```bash
  curl -X POST "http://localhost:8000/chat" \
    -H "Content-Type: application/json" \
    -d '{"question": "What services do you offer?"}'
  ```

## Common Issues

### Redis not connecting?
```bash
# Install Redis (macOS)
brew install redis
brew services start redis
```

### Import errors?
```bash
# Activate virtual environment
source venv/bin/activate
pip install -r requirements.txt
```

### Vector store not found?
```bash
# Make sure you have PDFs and run:
python ingest.py
```

## What's Next?

- Read the full [README.md](README.md) for detailed documentation
- Check [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
- Customize prompts in [prompt.py](prompt.py)
- Adjust working hours in [booking_agent.py](booking_agent.py)

## Need Help?

Open an issue on GitHub with:
- What you tried
- What happened
- Error messages
- Your OS and Python version

Happy building! 🚀
