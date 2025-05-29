RESUME_ANALYZER_PROMPT = """
Analyze this resume and identify:
1. Missing sections (Summary, Skills, Experience, Education, etc.)
2. Weak points that need improvement
3. Keywords missing for ATS optimization
4. Overall professional score (1-10)

Resume:
{resume_text}

Provide structured analysis in JSON format.
"""

RESUME_IMPROVER_PROMPT = """
Based on this analysis, improve the following resume section:
Section: {section}
Current Content: {content}
Issues: {issues}

Provide improved version that is:
- ATS-friendly
- Professional
- Quantified where possible
"""

JOB_MATCHER_PROMPT = """
Given this resume summary:
{resume_summary}

Find the best job titles and keywords to search for.
Return top 5 job titles and key skills to search.
"""