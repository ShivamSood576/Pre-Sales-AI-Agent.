
# ------------------------------------------------
# CHAT ROUTE (AUTO SESSION)
# ------------------------------------------------
import os
import json
import redis
from uuid import uuid4
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# LangChain imports (STABLE)
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import ChatPromptTemplate
from enum import Enum
from email_validator import validate_email, EmailNotValidError
from datetime import datetime

from requests import session
from function import detect_intent,extract_slots,merge_slots,is_discovery_in_progress,qualify_lead,looks_like_contact_info,normalize_and_validate_email,is_discovery_complete
from question_flow import QUESTION_FLOWs
from slots import quick_slot_fill
from prompt import intent_prompt,slot_prompt,rag_prompt
from booking_agent import BookingAgent
booking_agent = BookingAgent()


# ------------------------------------------------
# ENV
# ------------------------------------------------
load_dotenv()

VECTOR_DIR = "vectorstore"
PDF_DIR = "data/pdfs"
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
SESSION_TTL = 60 * 60 * 24  # 24 hours

os.makedirs(PDF_DIR, exist_ok=True)

# ------------------------------------------------
# REDIS (safe init)
# ------------------------------------------------
try:
    redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
    print("✅ Redis connected")
except Exception as e:
    print("❌ Redis not available:", e)
    redis_client = None

# ------------------------------------------------
# FASTAPI
# ------------------------------------------------
app = FastAPI(title="Xicom RAG Chatbot")

# ------------------------------------------------
# REQUEST / RESPONSE MODELS
# ------------------------------------------------
class ChatRequest(BaseModel):
    question: str
    session_id: str | None = None   # OPTIONAL


class ChatResponse(BaseModel):
    answer: str
    session_id: str

class Intent(str, Enum):
    PROJECT = "project"
    GENERAL = "general"
# ------------------------------------------------
# SESSION HELPERS
# ------------------------------------------------

def get_session(session_id: str):
    if not redis_client:
        return {
            "messages": [],
            "slots": {}
        }

    data = redis_client.get(session_id)
    if data:
        return json.loads(data)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    data = redis_client.get(session_id)
    if data:
        return json.loads(data)
    session = {
        "messages": [],
        "current_question": None,
        "discovery_started": False,
        "discovery_paused": False,
        "created_at": now,            # 👈 NEW
        "last_updated_at": now,       # 👈 NEW
        "booking": {
        "asked": False,
        "slots": [],
        "selected_slot": None
         },
        "slots": {
            "project_type": None,
            "business_goal": None,
            "technology": None,
            "timeline": None,
            "budget": None,
            "name": None,
            "email": None,
            "company": None,
            "phone": None
        }
    }

    redis_client.setex(session_id, SESSION_TTL, json.dumps(session))
    return session


def save_session(session_id: str, session_data: dict):
    if redis_client:
        redis_client.setex(
            session_id,
            SESSION_TTL,
            json.dumps(session_data)
        )

# ------------------------------------------------
# LLM & EMBEDDINGS
# ------------------------------------------------
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.2
)

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)


def is_yes(text: str) -> bool:
    return text in {"yes", "y", "yeah", "yep", "sure", "ok", "continue"}

# ------------------------------------------------
# VECTOR STORE
# ------------------------------------------------
if not os.path.exists(VECTOR_DIR):
    raise RuntimeError("❌ Vectorstore not found. Run ingest.py first.")

vectorstore = FAISS.load_local(
    VECTOR_DIR,
    embeddings,
    allow_dangerous_deserialization=True
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 7})






#import this
QUESTION_FLOW=QUESTION_FLOWs




# ------------------------------------------------
# RAG CHAIN
# ------------------------------------------------
document_chain = create_stuff_documents_chain(
    llm=llm,
    prompt=rag_prompt
)

qa_chain = create_retrieval_chain(
    retriever=retriever,
    combine_docs_chain=document_chain
)




# ------------------------------------------------
# ROUTES
# ------------------------------------------------
@app.get("/")
def greeting():
    return {
        "message": "Hi 👋 Welcome to Xicom Technologies. How can I help you today?"
    }
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    question = request.question.strip()
    session_id = request.session_id or str(uuid4())
    q_lower = question.lower()

    if not question:
        return ChatResponse(answer="Please ask something.", session_id=session_id)

    session = get_session(session_id)
    session["last_updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    session["messages"].append({"role": "user", "content": question})

    intent = detect_intent(q_lower)

    def is_yes(text: str):
        return text in {"yes", "y", "yeah", "yep", "sure", "ok", "book"}

    # =====================================================
    # ✅ SLOT SELECTION (USER PICKS NUMBER)
    # =====================================================
    if session.get("booking", {}).get("slots"):
        if question.isdigit():
            idx = int(question) - 1
            slots = session["booking"]["slots"]

            if idx < 0 or idx >= len(slots):
                return ChatResponse(
                    answer="❌ Invalid slot number. Please choose again.",
                    session_id=session_id
                )

            # Convert ISO strings back to datetime
            start_str, end_str = slots[idx]
            start_time = datetime.fromisoformat(start_str)
            end_time = datetime.fromisoformat(end_str)
            email = session["leads"][-1]["email"]

            event = booking_agent.book_slot(
                start_time=start_time,
                duration_minutes=30,
                user_email=email,
                summary="Project Discussion"
            )

            meet_link = event.get("meet_link")

            session["booking"] = {
                "asked": False,
                "slots": [],
                "selected": start_time.isoformat()
            }

            session["messages"].append({
                "role": "assistant",
                "content": meet_link
            })

            save_session(session_id, session)
            return ChatResponse(answer=meet_link, session_id=session_id)

    # =====================================================
    # 📅 USER SAID YES → SHOW AVAILABLE SLOTS
    # =====================================================
    if session.get("booking", {}).get("asked") and is_yes(q_lower):
        slots = booking_agent.get_available_slots(
            days_ahead=2,
            duration_minutes=30
        )

        slots = slots[:10]

        if not slots:
            msg = "❌ No available slots."
            return ChatResponse(answer=msg, session_id=session_id)

        # Convert datetime tuples to ISO strings for JSON serialization
        session["booking"]["slots"] = [
            [start.isoformat(), end.isoformat()] for start, end in slots
        ]

        msg = "📅 Available slots:\n\n"
        for i, (start, end) in enumerate(slots, 1):
            msg += f"{i}. {start.strftime('%d %b %Y, %I:%M %p')}\n"

        msg += "\nReply with slot number."

        session["messages"].append({
            "role": "assistant",
            "content": msg
        })

        save_session(session_id, session)
        return ChatResponse(answer=msg, session_id=session_id)

    # =====================================================
    # ▶️ RESUME DISCOVERY AFTER PAUSE
    # =====================================================
    if session.get("discovery_paused"):
        if is_yes(q_lower):
            session["discovery_paused"] = False
            session["discovery_started"] = True

            for slot, q_text in QUESTION_FLOW:
                if session["slots"].get(slot) is None:
                    session["current_question"] = slot
                    save_session(session_id, session)
                    return ChatResponse(answer=q_text, session_id=session_id)

        result = qa_chain.invoke({"input": question})
        answer = result["answer"]
        save_session(session_id, session)
        return ChatResponse(answer=answer, session_id=session_id)

    # =====================================================
    # SLOT FILLING
    # =====================================================
    current_slot = session.get("current_question")

    if current_slot:
        if current_slot == "email":
            email = normalize_and_validate_email(question)
            if not email:
                return ChatResponse(
                    answer="❌ Please enter a valid email.",
                    session_id=session_id
                )
            session["slots"]["email"] = email
        else:
            session["slots"][current_slot] = question.strip()

        session["current_question"] = None

    elif session["discovery_started"]:
        session["slots"] = quick_slot_fill(question, session["slots"])
        extracted = extract_slots(question)
        session["slots"] = merge_slots(session["slots"], extracted)

    # =====================================================
    # START DISCOVERY
    # =====================================================
    if intent == Intent.PROJECT and not session["discovery_started"]:
        session["discovery_started"] = True

    # =====================================================
    # ASK NEXT QUESTION
    # =====================================================
    if session["discovery_started"] and session["current_question"] is None:
        for slot, q_text in QUESTION_FLOW:
            if session["slots"].get(slot) is None:
                session["current_question"] = slot
                save_session(session_id, session)
                return ChatResponse(answer=q_text, session_id=session_id)

    # =====================================================
    # ✅ DISCOVERY COMPLETE → ASK TO BOOK
    # =====================================================
    if session["discovery_started"] and is_discovery_complete(session["slots"]):
        session["discovery_started"] = False

        session.setdefault("leads", []).append({
            **session["slots"],
            "lead_type": qualify_lead(session["slots"]),
            "completed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        session["slots"] = {k: None for k in session["slots"]}

        session["booking"]["asked"] = True

        msg = "✅ Details saved.\n\nWould you like to book a meeting?"

        session["messages"].append({
            "role": "assistant",
            "content": msg
        })

        save_session(session_id, session)
        return ChatResponse(answer=msg, session_id=session_id)

    # =====================================================
    # GENERAL RAG MODE
    # =====================================================
    result = qa_chain.invoke({"input": question})
    answer = result["answer"]

    session["messages"].append({
        "role": "assistant",
        "content": answer
    })

    save_session(session_id, session)
    return ChatResponse(answer=answer, session_id=session_id)


@app.get("/admin/session/{session_id}")
def fetch_session_details(session_id: str):
    """
    Admin API to fetch full session conversation and slot data
    """

    if not redis_client:
        raise HTTPException(
            status_code=500,
            detail="Redis not available"
        )

    data = redis_client.get(session_id)

    if not data:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    session_data = json.loads(data)

    return {
        "session_id": session_id,
        "message_count": len(session_data.get("messages", [])),
        "messages": session_data.get("messages", []),
        "slots": session_data.get("slots", {})
    }



# ------------------------------------------------
# ADMIN: PDF UPLOAD
# ------------------------------------------------
@app.post("/admin/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")

    file_path = os.path.join(PDF_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    loader = PyPDFLoader(file_path)
    documents = loader.load()

    if not documents:
        raise HTTPException(status_code=400, detail="PDF has no readable content")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200
    )

    chunks = splitter.split_documents(documents)

    vectorstore = FAISS.load_local(
        VECTOR_DIR,
        embeddings,
        allow_dangerous_deserialization=True
    )

    vectorstore.add_documents(chunks)
    vectorstore.save_local(VECTOR_DIR)

    return {
        "message": f"PDF '{file.filename}' uploaded successfully",
        "chunks_added": len(chunks)
    }


@app.get("/admin/sessions_id")
def list_all_sessions():
    """
    Admin API to list all chat sessions with a summary
    """

    if not redis_client:
        raise HTTPException(
            status_code=500,
            detail="Redis not available"
        )

    sessions = []
    keys = redis_client.keys("*")

    for key in keys:
        # Skip non-session keys (like qa cache)
        if key.startswith("qa:"):
            continue

        try:
            raw = redis_client.get(key)
            if not raw:
                continue

            data = json.loads(raw)
            messages = data.get("messages", [])
            leads = data.get("leads", [])

            # Get latest completed project (if any)
            latest_lead = leads[-1] if leads else {}

            summary = {
                "session_id": key,
                "created_at": data.get("created_at"),
                "last_updated_at": data.get("last_updated_at"),

                # ✅ READ FROM LEADS, NOT slots
                "lead_type": latest_lead.get("lead_type", "Unknown"),
                "name": latest_lead.get("name"),
                "email": latest_lead.get("email"),
                "phone": latest_lead.get("phone"),
                "project_type": latest_lead.get("project_type"),
                "business_goal": latest_lead.get("business_goal"),

                # ✅ EXTRA USEFUL INFO
                "total_projects": len(leads),
                "message_count": len(messages),
                "last_message": messages[-1]["content"] if messages else None
            }

        

            sessions.append(summary)

        except Exception:
            # Ignore corrupted or non-session keys
            continue

    return {
        "total_sessions": len(sessions),
        "sessions": sessions
    }

