
IMPROVE_RESUME_TEMPLATE = """\
You are a resume expert. Rewrite the following resume to improve clarity and alignment 
with the role of {role}. Use a professional tone. Enhance formatting, but keep the same content.

Resume:
{resume}
"""

DETECT_GAPS_TEMPLATE = """\
You are a career advisor. Compare the resume to the job description. 
List clearly what skills/experience/certifications are missing in the resume:

Resume:
{resume}

Job Description:
{job}
"""

SUGGEST_SUBFIELDS_TEMPLATE = """\
You are a learning guide. Given these missing skills: {skills}, 
return for each skill a list of 3–5 key subtopics or subfields the candidate should learn.
"""

INTERVIEW_Q_TEMPLATE = """\
You are an interview coach. For companies: {companies}, hiring for role: {role}, 
generate 5 tailored technical interview questions.
"""
