import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")  # Update your .env to use GEMINI_API_KEY

# Use Gemini model (1.5 Flash or Pro)
llm = ChatGoogleGenerativeAI(
    temperature=0.1,
    model="gemini-2.0-flash",  # or "gemini-1.5-pro"
    google_api_key=api_key
)

def improve_resume(resume_text: str, target_role: str) -> str:
    """Use Gemini to improve the resume for a given role."""
    template = (
        "You are a resume expert. Rewrite the following resume to improve clarity and alignment "
        "with the role of {role}. Use a professional tone. Enhance formatting, but keep the same content.\n\n"
        "Resume:\n{resume}"
    )

    prompt = ChatPromptTemplate.from_template(template)
    messages = prompt.format_messages(role=target_role, resume=resume_text)

    return llm.invoke(messages).content

def detect_gaps(resume_text: str, job_description: str) -> str:
    """Detect skill or experience gaps using Gemini."""
    prompt = (
        "You are a career advisor. Compare the resume to the job description. "
        "List clearly what skills/experience/certifications are missing in the resume:\n\n"
        "Resume:\n{resume}\n\nJob Description:\n{job}"
    ).format(resume=resume_text, job=job_description)

    return llm.invoke([HumanMessage(content=prompt)]).content
