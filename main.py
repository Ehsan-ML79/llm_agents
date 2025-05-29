from agents import improve_resume, detect_gaps

def load_file(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as file:
        return file.read()

def write_file(path: str, content: str):
    with open(path, 'w', encoding='utf-8') as file:
        file.write(content)

def main():
    resume = load_file("sample_resume.txt")
    role = "Machine Learning Engineer"
    job_desc = load_file("sample_hiring.txt")

    print("\n--- Improving Resume ---")
    improved = improve_resume(resume, role)
    write_file("improved_resume.txt", improved)
    print("✅ Resume improved and saved to 'improved_resume.txt'")

    print("\n--- Detecting Gaps ---")
    gaps = detect_gaps(improved, job_desc)
    print(gaps)
    write_file("resume_gaps.txt", gaps)
    print("✅ Gaps analysis saved to 'resume_gaps.txt'")

if __name__ == "__main__":
    main()