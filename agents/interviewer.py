from typing import List, Dict
from llms.metis_llm import MetisGeminiLLM
from prompts import INTERVIEW_Q_TEMPLATE

# Initialize LLM
llm = MetisGeminiLLM(api_key="tpsg-JwhFnuGQsuWfgM5q8xpOyCpmRWuI80n", model_name="gpt-4o")


def generate_interview_questions(jobs_cluster: List[Dict]) -> List[str]:
    """
    Generates a list of 5 interview questions for a given cluster of jobs.
    """
    # Summarize cluster
    companies = set(job['Company'] for job in jobs_cluster)
    prompt = INTERVIEW_Q_TEMPLATE.format(
        companies=", ".join(companies),
        role=jobs_cluster[0]['Job Title'] if jobs_cluster else ""
    )
    response = llm.invoke(prompt).content
    # Assume newline-separated questions
    questions = [q.strip() for q in response.splitlines() if q.strip()]
    return questions