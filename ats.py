
import google.generativeai as genai
import os
from dotenv import load_dotenv
import streamlit as st
from PyPDF2 import PdfReader

# Load environment variables
load_dotenv()

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-pro")

def get_rawtext(uploaded_file):
    """Extract text from uploaded PDF file."""
    text = ""
    try:
        pdfreader = PdfReader(uploaded_file)
        for page in pdfreader.pages:
            text += page.extract_text()
        if not text:
            raise ValueError("No text could be extracted from the PDF.")
    except Exception as e:
        st.error(f"Error reading PDF file: {e}")
        return None
    return text

def ats_check(resume_text, job_role, desc):
    """Generate ATS analysis based on resume text, job role, and job description."""
    prompt = f"""
    **Act as a professional Applicant Tracking System (ATS) resume analyzer with expertise in tech roles, software development, and tech consulting.** 

    **Analyze the following resume for the job role of {job_role} based on the provided job description.**

    **Resume Text:**
    {resume_text}

    **Job Description:**
    {desc}

    **Please provide the following output information:**

    1. **ATS Compatibility Score:**
    - Provide a percentage score indicating the resume's compatibility with various ATS.
    - Explain the factors affecting the score (e.g., formatting, keywords).
    - Indicate whether the resume is likely to pass or fail ATS screening based on the score.

    2. **Keyword Analysis:**
    - Identify skills and experience mentioned in the resume that are relevant to the job description. Categorize them as "Present" or "Missing" based on the job description.
    - Explain the importance of each "Present" skill for the job role.
    - Highlight any particularly relevant skills not explicitly mentioned in the resume but demonstrably possessed based on the experience section (e.g., leadership skills gained through project management).
    - Provide a list of "Missing" skills that would significantly improve the resume's match with the job description.

    3. **Formatting and Structure Analysis:**
    - Assess the resume's formatting and structure, including:
        - Header, footer, and margin optimization.
        - Use of fonts, headings, and bullets.
        - Overall readability and ATS compatibility.

    4. **ATS Recommendation Report:**
    - Provide specific recommendations on how to optimize the resume for ATS compatibility, including:
        - Adjusting formatting and structure for better parsability.
        - Adding relevant keywords identified as "Missing" in the analysis.
        - Highlighting transferable skills that demonstrate the missing keywords.
    """
    response = model.generate_content(prompt)
    return response.text

def main():
    st.write("Welcome to the ATS Checker! 🚀")
    st.write("Upload your resume and provide the job role and description to get valuable insights and optimize your resume for Applicant Tracking Systems (ATS). 💼")

    st.write("Upload your resume and provide the job role and description to get started.")

    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
    job_role = st.text_input("Enter the job role you are applying for")
    desc = st.text_area("Enter the job description")
    btn = st.button("Submit")

    if btn:
        if uploaded_file is None:
            st.warning("Please upload a PDF file to continue.")
        elif not job_role.strip():
            st.warning("Please enter the job role to continue.")
        elif not desc.strip():
            st.warning("Please enter the job description to continue.")
        else:
            st.write("Processing your resume...")
            resume_text = get_rawtext(uploaded_file)
            if resume_text:
                result = ats_check(resume_text, job_role, desc)
                st.write(result)
            else:
                st.error("Failed to extract text from the PDF. Please try again with a different file.")

if __name__ == "__main__":
    main()