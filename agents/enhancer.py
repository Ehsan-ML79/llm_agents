from typing import Dict, List
from llms.metis_llm import MetisGeminiLLM
from prompts import (
    IMPROVE_RESUME_TEMPLATE,
    DETECT_GAPS_TEMPLATE,
    SUGGEST_SUBFIELDS_TEMPLATE,
)

# Initialize LLM once per module
llm = MetisGeminiLLM(api_key="${METIS_API_KEY}", model_name="gemini-1.5-flash")


def enhance_and_suggest(resume_text: str, job_description: str, target_role: str) -> Dict:
    """
    1) Improve resume for target_role
    2) Detect gaps vs job_description
    3) Suggest subfields for each missing skill
    Returns a dict with keys: improved_resume, gaps, upskill_recommendations
    """
    # 1. Improve Resume
    prompt = IMPROVE_RESUME_TEMPLATE.format(role=target_role, resume=resume_text)
    improved_resume = llm.invoke(prompt).content

    # 2. Detect Gaps
    prompt = DETECT_GAPS_TEMPLATE.format(resume=improved_resume, job=job_description)
    gaps_text = llm.invoke(prompt).content
    # Parse gaps: assume newline-separated
    gaps = [line.strip() for line in gaps_text.splitlines() if line.strip()]

    # 3. Suggest Subfields
    prompt = SUGGEST_SUBFIELDS_TEMPLATE.format(skills=", ".join(gaps))
    subfields_text = llm.invoke(prompt).content
    # Parsing into dict is left as TODO
    upskill_recommendations: Dict[str, List[str]] = {}  # TODO: parse subfields_text

    return {
        "improved_resume": improved_resume,
        "gaps": gaps,
        "upskill_recommendations": upskill_recommendations,
    }