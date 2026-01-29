import re

def quick_slot_fill(question: str, slots: dict) -> dict:
    q = question.lower().strip()

    # -------- project type --------
    if q in ["new project", "new", "fresh project"]:
        slots["project_type"] = "new project"

    elif q in ["enhancement", "existing project", "upgrade"]:
        slots["project_type"] = "enhancement"

    # -------- business goal --------
    if "mvp" in q:
        slots["business_goal"] = "MVP"

    elif "startup" in q:
        slots["business_goal"] = "Startup project"

    elif "scal" in q:
        slots["business_goal"] = "Scaling"

    elif "automat" in q:
        slots["business_goal"] = "Automation"

    # -------- technology --------
    if any(t in q for t in ["react", "flutter", "android", "ios", "mobile", "web", "ai", "ml", "python", "node"]):
        slots["technology"] = question

    # -------- timeline --------
    if "month" in q or "week" in q or "immediate" in q:
        slots["timeline"] = question

    # -------- budget --------
    if "$" in q or "k" in q or "lakh" in q or "crore" in q:
        slots["budget"] = question

    # -------- email --------
    if re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", q):
        slots["email"] = question

    # -------- phone --------
    if re.search(r"\+?\d[\d\s\-]{7,}", q):
        slots["phone"] = question

    # -------- name --------
    if slots.get("name") is None and q.isalpha() and len(q) < 20:
        slots["name"] = question

    return slots


QUESTION_TO_SLOT = {
    "project_type": "project_type",
    "business_goal": "business_goal",
    "technology": "technology",
    "timeline": "timeline",
    "budget": "budget",
    "name": "name",
    "email": "email",
    "company": "company",
    "phone": "phone"
}

