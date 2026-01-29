from langchain.prompts import ChatPromptTemplate

rag_prompt = ChatPromptTemplate.from_template("""
You are a professional pre-sales and support assistant for Xicom Technologies.

Using the information provided in the context, give a clear, detailed, and structured response.
If multiple services or capabilities are mentioned, list them in bullet points.
Write in a professional, business-friendly tone suitable for potential clients.

<context>
{context}
</context>

Question: {input}

Answer:
""")


intent_prompt = ChatPromptTemplate.from_template("""
Classify the user's intent.

User message:
"{input}"

Respond with ONLY one word:
- project (if user wants to build, develop, hire, cost, timeline, solution, app, website, AI, etc.)
- general (if informational, browsing, company info, services, etc.)
""")

slot_prompt = ChatPromptTemplate.from_template("""
Extract structured information from the user message.

User message:
"{input}"

Return a VALID JSON with ONLY these keys.
If a value is not mentioned, use null.

Keys:
project_type (new project | enhancement | null)
business_goal
technology
timeline
budget
name
email
company
phone
""")