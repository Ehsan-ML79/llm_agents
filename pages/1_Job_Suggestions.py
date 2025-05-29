import streamlit as st

st.title("🧠 Step 1: Job Title Suggestions")

st.markdown("Fill in your information below. The agent will suggest best job titles later.")

with st.form("job_suggestions_form"):
    name = st.text_input("Full Name")
    skills = st.text_area("Your Skills (comma-separated)")
    experience = st.text_area("Work Experience")
    education = st.text_input("Education")

    submitted = st.form_submit_button("Submit")

if submitted:
    st.success("✅ Info submitted! We'll suggest jobs once AI is connected.")

print("✅ 1_Job_Suggestions.py is loaded")
