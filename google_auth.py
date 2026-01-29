import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]
CLIENT_SECRET_FILE = os.getenv(
    "GOOGLE_CLIENT_SECRET_FILE",
    os.path.join(os.path.dirname(__file__), "client_secret.json"),
)
TOKEN_FILE = os.getenv("GOOGLE_TOKEN_FILE", "token.json")


def get_calendar_service():
    creds = None

    # Load existing token
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(
            TOKEN_FILE, SCOPES
        )

    # Authenticate if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE,
                SCOPES
            )
            creds = flow.run_local_server(
                port=8080,
                prompt="consent"
            )

        # Save token
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    service = build(
        "calendar",
        "v3",
        credentials=creds
    )

    return service
