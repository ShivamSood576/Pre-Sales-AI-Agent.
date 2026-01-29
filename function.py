from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from prompt import intent_prompt,slot_prompt,rag_prompt
import json
from enum import Enum
import re
from question_flow import QUESTION_FLOWs
from dotenv import load_dotenv
load_dotenv()
import os
from email_validator import validate_email, EmailNotValidError


QUESTION_FLOW=QUESTION_FLOWs


class Intent(str, Enum):
    PROJECT = "project"
    GENERAL = "general"

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.2,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)


def extract_slots(question: str) -> dict:
    chain = slot_prompt | llm
    response = chain.invoke({"input": question}).content

    try:
        return json.loads(response)
    except Exception:
        return {}
    
def merge_slots(existing: dict, extracted: dict) -> dict:
    for key, value in extracted.items():
        if key in existing and existing[key] is None and value:
            existing[key] = value
    return existing



def is_discovery_in_progress(slots: dict) -> bool:
    return any(
        slots.get(k) is None
        for k in ["project_type", "business_goal", "technology", "timeline", "budget"]
    )

def final_confirmation_message():
    return (
        "✅ Thank you for sharing the details!\n\n"
        "Our team will contact you shortly to discuss your requirements.\n\n"
        "In the meantime, feel free to ask me anything about Xicom, "
        "our services, development process, or past work."
    )

def is_discovery_complete(slots: dict) -> bool:
    return all(
        slots.get(k)
        for k in [
            "project_type",
            "business_goal",
            "technology",
            "timeline",
            "budget",
            "name",
            "email",
            "company",
            "phone"
        ]
    )

def next_question(slots: dict):
    for key, question in QUESTION_FLOW:
        if slots.get(key) is None:
            return question
    return None


def qualify_lead(slots: dict) -> str:
    if slots["timeline"] and slots["budget"]:
        return "High Intent"
    if slots["project_type"] or slots["business_goal"]:
        return "Medium Intent"
    return "Low Intent"




def looks_like_contact_info(text: str) -> bool:
    # email
    if re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text):
        return True

    # phone number (8+ digits)
    if re.fullmatch(r"\+?\d[\d\s\-]{7,}", text):
        return True

    return False


# def detect_intent(question: str) -> Intent:
#     q = question.lower()

#     project_keywords = [
#         "build", "develop", "create", "make",
#         "need a", "looking for",
#         "app", "website", "software",
#         "hire", "cost", "pricing", "estimate",
#         "timeline", "budget"
#     ]

#     if any(k in q for k in project_keywords):
#         return Intent.PROJECT

#     return Intent.GENERAL

def detect_intent(text: str) -> Intent:
    text = text.lower()

    # ❌ HARD BLOCK – career / jobs
    career_keywords = [
        "job", "jobs", "vacancy", "career", "hiring",
        "opening", "openings", "internship", "recruitment"
    ]
    if any(k in text for k in career_keywords):
        return Intent.GENERAL

    # ✅ PROJECT intent keywords
    project_keywords = [
        "build", "create", "project",
        "website", "app", "application", "software",
        "system", "platform", "solution","build", "develop", "create", 
        "make","need a", "looking for",
        "app", "website", "software"
    ]

    if any(k in text for k in project_keywords):
        return Intent.PROJECT

    return Intent.GENERAL


def normalize_and_validate_email(email: str) -> str | None:
    """
    Returns normalized email if valid, else None
    """
    try:
        v = validate_email(email, check_deliverability=True)
        return v.email  # normalized (lowercase, trimmed)
    except EmailNotValidError:
        return None