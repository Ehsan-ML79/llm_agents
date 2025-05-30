# from typing import List, Dict, Optional
# from langchain.tools import Tool
# from playwright.sync_api import sync_playwright
# import pandas as pd
# import os

# def _scrape_jobs_playwright(query: str, max_results: int = 10) -> List[Dict]:
#     """
#     Uses Playwright to fetch job postings from Indeed for the given query.
#     Returns a list of dicts: {title, company, location, snippet, url}
#     """
#     results = []
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=True)
#         page = browser.new_page()
#         page.goto(f"https://www.indeed.com/jobs?q={query}")
#         job_cards = page.query_selector_all(".jobsearch-SerpJobCard")[:max_results]
#         for card in job_cards:
#             title = card.query_selector("h2.title").inner_text().strip()
#             company = card.query_selector(".company").inner_text().strip()
#             location = card.query_selector(".location").inner_text().strip()
#             snippet = card.query_selector(".summary").inner_text().strip()
#             link = card.query_selector("a.jobtitle").get_attribute("href")
#             results.append({
#                 "title": title,
#                 "company": company,
#                 "location": location,
#                 "snippet": snippet,
#                 "url": f"https://www.indeed.com{link}",
#             })
#         browser.close()
#     return results

# # Expose as a LangChain Tool
# scrape_jobs_tool = Tool(
#     name="scrape_jobs",
#     func=_scrape_jobs_playwright,
#     description="Scrape up to `max_results` job postings from Indeed for a given query. Returns list of job dicts."
# )

# # Orchestration function
# def scrape_jobs(query: str, max_results: int = 10) -> List[Dict]:
#     """
#     Wrapper around the scrape_jobs_tool for direct use.
#     """
#     return _scrape_jobs_playwright(query, max_results)




# def search_jobs(
#     query: Optional[str] = None,
#     csv_path: Optional[str] = None, #("../data/sample100.csv")
#     max_results: int = 10
# ) -> List[Dict]:
#     """
#     If csv_path is provided and exists, loads jobs from that CSV.
#     Otherwise falls back to scraping Indeed for `query`.
#     """
#     if csv_path and os.path.exists(csv_path):
#         return load_jobs_from_csv(csv_path)
#     elif query:
#         return _scrape_jobs_playwright(query, max_results)
#     else:
#         raise ValueError("Either query or csv_path must be provided.")

# # Expose scraping as a tool if you still want it under LangChain agents:
# scrape_jobs_tool = Tool(
#     name="scrape_jobs",
#     func=lambda q, max_results=10: search_jobs(query=q, max_results=max_results),
#     description="Scrape Indeed or, if given a CSV path, load jobs from CSV."
# )

# llm_agents/agents/searcher.py

from typing import List, Dict, Optional
import os
import logging
import pandas as pd

logger = logging.getLogger(__name__)

def load_resume_text(resume_path: str) -> str:
    """Load resume text from a .txt file."""
    try:
        with open(resume_path, "r", encoding="utf-8") as f:
            text = f.read()
            logger.info(f"Loaded resume from {resume_path}")
            return text
    except Exception as e:
        logger.error(f"Failed to read resume: {e}")
        return ""

def score_job_against_resume(job: Dict, resume_text: str) -> int:
    """
    Score a job posting based on keyword overlap with resume.
    Higher score = more relevant.
    """
    score = 0
    resume_words = set(resume_text.lower().split())

    # Consider these fields from job CSV
    keys_to_check = ['skills', 'Job Title', 'Job Description', 'location', 'Role']

    for key in keys_to_check:
        job_value = job.get(key, "")
        job_words = set(str(job_value).lower().split())
        overlap = resume_words.intersection(job_words)
        score += len(overlap)

    return score

def load_jobs_from_csv(path: str) -> List[Dict]:
    df = pd.read_csv(path)
    return df.to_dict(orient="records")

def find_matching_jobs_from_resume(
    resume_path: str,
    csv_path: str,
    max_results: int = 10
) -> List[Dict]:
    """
    High-level function: load resume and CSV, then return best-matching jobs.
    """
    resume_text = load_resume_text(resume_path)
    if not resume_text:
        return []

    jobs = load_jobs_from_csv(csv_path)

    if not jobs:
        logger.warning("No jobs loaded from CSV.")
        return []

    # Score all jobs
    scored_jobs = []
    for job in jobs:
        score = score_job_against_resume(job, resume_text)
        job['match_score'] = score
        scored_jobs.append(job)

    # Sort and return top results
    sorted_jobs = sorted(scored_jobs, key=lambda x: x['match_score'], reverse=True)
    return sorted_jobs[:max_results]

