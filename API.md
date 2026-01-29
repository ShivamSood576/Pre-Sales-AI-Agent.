# API Documentation

Complete API reference for the AI RAG Chatbot.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, no authentication is required. For production, implement API key authentication or OAuth.

## Endpoints

### 1. Chat with Bot

**POST** `/chat`

Send a message to the chatbot and receive an AI-generated response.

**Request Body:**
```json
{
  "question": "What services do you offer?",
  "session_id": "optional-uuid-here"
}
```

**Response:**
```json
{
  "answer": "We offer a wide range of software development services...",
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Status Codes:**
- `200 OK` - Success
- `400 Bad Request` - Invalid request
- `500 Internal Server Error` - Server error

**Example:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What technologies do you use?"
  }'
```

---

### 2. Upload PDF

**POST** `/upload-pdf`

Upload PDF files to add to the knowledge base.

**Request:**
- Content-Type: `multipart/form-data`
- Field: `file` (PDF file)

**Response:**
```json
{
  "message": "PDF uploaded and ingested successfully",
  "filename": "document.pdf"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/upload-pdf" \
  -F "file=@/path/to/document.pdf"
```

---

### 3. Get Available Slots

**GET** `/slots`

Retrieve available calendar slots for booking.

**Query Parameters:**
- `days_ahead` (optional, default: 7) - Number of days to look ahead
- `duration` (optional, default: 30) - Meeting duration in minutes

**Response:**
```json
{
  "slots": [
    {
      "start": "2026-01-30T09:00:00+05:30",
      "end": "2026-01-30T09:30:00+05:30",
      "display": "30 Jan, 09:00 AM - 09:30 AM"
    },
    {
      "start": "2026-01-30T10:00:00+05:30",
      "end": "2026-01-30T10:30:00+05:30",
      "display": "30 Jan, 10:00 AM - 10:30 AM"
    }
  ]
}
```

**Example:**
```bash
curl "http://localhost:8000/slots?days_ahead=3&duration=60"
```

---

### 4. Book Meeting

**POST** `/book`

Book a calendar meeting.

**Request Body:**
```json
{
  "start_time": "2026-01-30T09:00:00+05:30",
  "duration_minutes": 30,
  "title": "Consultation Meeting",
  "description": "Project discussion",
  "attendee_email": "client@example.com"
}
```

**Response:**
```json
{
  "message": "Meeting booked successfully",
  "event_id": "abc123xyz",
  "event_link": "https://calendar.google.com/calendar/event?eid=..."
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/book" \
  -H "Content-Type: application/json" \
  -d '{
    "start_time": "2026-01-30T09:00:00+05:30",
    "duration_minutes": 30,
    "title": "Consultation",
    "attendee_email": "client@example.com"
  }'
```

---

## Admin Endpoints

### 5. Get Session Details

**GET** `/admin/session/{session_id}`

Retrieve complete session history and extracted information.

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "messages": [
    {
      "role": "user",
      "content": "I need a mobile app"
    },
    {
      "role": "assistant",
      "content": "I'd be happy to help! What's your name?"
    }
  ],
  "slots": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "service_type": "mobile development"
  },
  "discovery_phase": "gathering_info",
  "intent": "project"
}
```

**Example:**
```bash
curl "http://localhost:8000/admin/session/550e8400-e29b-41d4-a716-446655440000"
```

---

### 6. List All Sessions

**GET** `/admin/sessions`

Get a list of all active sessions.

**Query Parameters:**
- `limit` (optional, default: 50) - Max sessions to return

**Response:**
```json
{
  "sessions": [
    {
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "last_activity": "2026-01-29T14:30:00",
      "message_count": 5,
      "has_slots": true
    }
  ],
  "total": 1
}
```

**Example:**
```bash
curl "http://localhost:8000/admin/sessions?limit=100"
```

---

### 7. Delete Session

**DELETE** `/admin/session/{session_id}`

Delete a session and its history.

**Response:**
```json
{
  "message": "Session deleted successfully",
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Example:**
```bash
curl -X DELETE "http://localhost:8000/admin/session/550e8400-e29b-41d4-a716-446655440000"
```

---

## Health Check

### 8. Health Status

**GET** `/health`

Check if the service is running and dependencies are available.

**Response:**
```json
{
  "status": "healthy",
  "redis": "connected",
  "vectorstore": "available",
  "timestamp": "2026-01-29T14:30:00"
}
```

**Example:**
```bash
curl "http://localhost:8000/health"
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message description"
}
```

**Common Error Codes:**
- `400` - Bad Request (invalid parameters)
- `404` - Not Found (session/resource doesn't exist)
- `422` - Validation Error (invalid request body)
- `500` - Internal Server Error

---

## Rate Limiting

Currently no rate limiting is implemented. For production:
- Implement rate limiting middleware
- Recommended: 100 requests per minute per IP
- Return `429 Too Many Requests` when exceeded

---

## WebSocket Support (Future)

For real-time chat streaming:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Response:', data.answer);
};

ws.send(JSON.stringify({
  question: "Tell me about your services",
  session_id: "my-session-id"
}));
```

---

## Interactive Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## SDKs and Client Libraries

### Python Client Example

```python
import requests

class ChatbotClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session_id = None
    
    def chat(self, question):
        response = requests.post(
            f"{self.base_url}/chat",
            json={
                "question": question,
                "session_id": self.session_id
            }
        )
        data = response.json()
        self.session_id = data["session_id"]
        return data["answer"]
    
    def get_slots(self, days_ahead=7):
        response = requests.get(
            f"{self.base_url}/slots",
            params={"days_ahead": days_ahead}
        )
        return response.json()["slots"]

# Usage
client = ChatbotClient()
answer = client.chat("What services do you offer?")
print(answer)
```

### JavaScript Client Example

```javascript
class ChatbotClient {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
    this.sessionId = null;
  }

  async chat(question) {
    const response = await fetch(`${this.baseUrl}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question,
        session_id: this.sessionId
      })
    });
    const data = await response.json();
    this.sessionId = data.session_id;
    return data.answer;
  }

  async getSlots(daysAhead = 7) {
    const response = await fetch(
      `${this.baseUrl}/slots?days_ahead=${daysAhead}`
    );
    const data = await response.json();
    return data.slots;
  }
}

// Usage
const client = new ChatbotClient();
const answer = await client.chat('What services do you offer?');
console.log(answer);
```

---

## Webhooks (Future Enhancement)

Configure webhooks to receive notifications:

```json
{
  "event": "booking_created",
  "data": {
    "session_id": "...",
    "event_id": "...",
    "start_time": "2026-01-30T09:00:00+05:30"
  },
  "timestamp": "2026-01-29T14:30:00"
}
```

---

## Best Practices

1. **Session Management**: Always include `session_id` for continued conversations
2. **Error Handling**: Implement retry logic with exponential backoff
3. **Timeout**: Set reasonable timeouts (30s recommended)
4. **Caching**: Cache responses when appropriate
5. **Validation**: Validate inputs before sending to API

---

## Support

For API issues or questions:
- Check the interactive docs at `/docs`
- Open an issue on GitHub
- Review error messages carefully

---

Last updated: January 29, 2026
