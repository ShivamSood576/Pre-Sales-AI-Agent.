# AI-Powered RAG Chatbot with Calendar Booking

A FastAPI-based conversational AI chatbot that combines Retrieval-Augmented Generation (RAG) with intelligent calendar booking capabilities. The system uses Google's Gemini AI for natural language understanding and integrates with Google Calendar for automated appointment scheduling.

## Features

- 🤖 **RAG-based Chat**: Leverages LangChain and FAISS for intelligent document retrieval and question answering
- 📅 **Calendar Integration**: Automated booking through Google Calendar API with conflict detection
- 🧠 **Intent Detection**: Smart classification of user queries (project-related vs. general inquiries)
- 💬 **Session Management**: Redis-based persistent chat sessions with slot filling
- 🎯 **Lead Qualification**: Automated discovery flow for gathering user information
- ⏰ **Smart Scheduling**: Finds available time slots based on working hours and existing bookings
- 📧 **Email Validation**: Built-in email validation for contact information

## Tech Stack

- **Framework**: FastAPI
- **AI/ML**: LangChain, Google Gemini (gemini-1.5-flash)
- **Vector Store**: FAISS
- **Database**: Redis
- **APIs**: Google Calendar API
- **Document Processing**: PyPDF

## Prerequisites

- Python 3.10+
- Redis server
- Google Cloud Project with Calendar API enabled
- Google OAuth 2.0 credentials

## Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd <repo-name>
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   # Google API
   GOOGLE_API_KEY=your_gemini_api_key_here
   GOOGLE_CLIENT_SECRET_FILE=client_secret.json
   GOOGLE_TOKEN_FILE=token.json
   
   # Calendar Settings
   CALENDAR_ID=primary
   CALENDAR_TIME_ZONE=Asia/Kolkata
   
   # Redis
   REDIS_URL=redis://localhost:6379/0
   ```

5. **Set up Google Calendar API**
   
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Google Calendar API
   - Create OAuth 2.0 credentials (Desktop app)
   - Download credentials and save as `client_secret.json` in the project root
   - **Note**: Do NOT commit `client_secret.json` to version control

6. **Prepare your documents**
   
   Place your PDF documents in the `data/pdfs/` directory:
   ```bash
   mkdir -p data/pdfs
   # Copy your PDF files to data/pdfs/
   ```

7. **Ingest documents into vector store**
   ```bash
   python ingest.py
   ```

## Usage

### Starting the Server

1. **Start Redis** (if not already running)
   ```bash
   redis-server
   ```

2. **Run the FastAPI application**
   ```bash
   uvicorn app15_book:app --reload --port 8000
   ```

3. **Access the API**
   - API: `http://localhost:8000`
   - Interactive docs: `http://localhost:8000/docs`
   - Alternative docs: `http://localhost:8000/redoc`

### API Endpoints

#### Chat Endpoint
```bash
POST /chat
```

**Request Body:**
```json
{
  "question": "What services do you offer?",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "answer": "We offer...",
  "session_id": "session-uuid"
}
```

#### Upload PDF
```bash
POST /upload-pdf
```

Upload PDF files to add to the knowledge base.

#### Admin: View Session
```bash
GET /admin/session/{session_id}
```

View complete session history and extracted slots.

#### Admin: List Sessions
```bash
GET /admin/sessions
```

List all active sessions.

## Project Structure

```
.
├── app15_book.py          # Main FastAPI application
├── booking_agent.py       # Calendar booking logic
├── calendar_service.py    # Google Calendar API integration
├── google_auth.py         # Google OAuth authentication
├── function.py            # Core utility functions (intent detection, slot extraction)
├── question_flow.py       # Discovery flow configuration
├── prompt.py              # AI prompts for different tasks
├── slots.py               # Slot filling logic
├── slot_utils.py          # Slot management utilities
├── ingest.py              # PDF ingestion script
├── phase3.py              # Streamlit UI (commented)
├── data/
│   └── pdfs/              # PDF documents for RAG
├── vectorstore/           # FAISS vector store (generated)
├── .env                   # Environment variables (create this)
├── .gitignore             # Git ignore rules
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Configuration

### Working Hours
Modify in [booking_agent.py](booking_agent.py):
```python
work_hours=(9, 18)  # 9 AM to 6 PM
slot_minutes=30     # 30-minute slots
```

### Time Zone
Set in `.env`:
```env
CALENDAR_TIME_ZONE=Asia/Kolkata
```

### Session TTL
Modify in [app15_book.py](app15_book.py):
```python
SESSION_TTL = 60 * 60 * 24  # 24 hours
```

## How It Works

1. **User sends a message** → System detects intent (project-related or general)
2. **RAG retrieval** → Relevant documents are retrieved from FAISS vector store
3. **Intent-based routing**:
   - **Project queries**: Uses discovery flow to gather user information
   - **General queries**: Direct RAG-based response
4. **Slot filling** → Extracts name, email, phone, project details
5. **Lead qualification** → When enough information is gathered, offers booking
6. **Calendar booking** → User selects time slot → Event created in Google Calendar

## Development

### Running Tests
```bash
# Add your test command here
pytest
```

### Code Style
```bash
# Format code
black .

# Lint code
flake8 .
```

## Security Notes

⚠️ **Important**: Never commit sensitive files:
- `client_secret.json` - Google OAuth credentials
- `token.json` - OAuth tokens
- `.env` - Environment variables
- PDF files containing sensitive information

These are already excluded in `.gitignore`.

## Troubleshooting

### Redis Connection Error
- Ensure Redis is running: `redis-cli ping` should return `PONG`
- Check Redis URL in `.env`

### Google Calendar API Error
- Verify `client_secret.json` exists and is valid
- Re-authenticate: delete `token.json` and restart the app
- Check Calendar API is enabled in Google Cloud Console

### Vector Store Not Found
- Run `python ingest.py` to create the vector store
- Ensure PDFs exist in `data/pdfs/`

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- LangChain for the RAG framework
- Google Gemini for AI capabilities
- FastAPI for the web framework
- FAISS for vector similarity search

## Contact

For questions or support, please open an issue in the repository.
