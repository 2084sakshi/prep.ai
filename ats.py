import os
from dotenv import load_dotenv
import streamlit as st
from PyPDF2 import PdfReader
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-pro")

# Extract raw text from PDF
def get_rawtext(uploaded_file):
    """Extract text from uploaded PDF file."""
    text = ""
    try:
        pdfreader = PdfReader(uploaded_file)
        for page in pdfreader.pages:
            text += page.extract_text()
            text += "\n"
        if not text:
            raise ValueError("No text could be extracted from the PDF.")
    except Exception as e:
        st.error(f"Error reading PDF file: {e}")
        return None
    return text

# ATS check using AI (without FAISS)
def ats_check_ai_based(resume_text, job_role, desc):
    """Generate ATS analysis based on resume text, job role, and job description using generative AI."""
    # Prepare generative AI prompt based on resume and job description
    prompt = f"""
    You are a professional ATS (Applicant Tracking System) resume analyzer, specializing in matching resumes with job descriptions.

    Analyze the following resume for the specified job role and provide a detailed analysis of the resume's compatibility with the job description.

    **Job Role**: {job_role}

    **Resume Text**: 
    {resume_text}

    **Job Description**:
    {desc}

    **Instructions**:
    1. **ATS Compatibility Score**: Provide a numerical score from 0 to 100 representing how well the resume matches the job description in terms of ATS compatibility.
    2. **Missing Skills**: Identify and list the skills that are missing from the resume compared to the job description.
    3. **Optimization Suggestions**: Provide **highly specific recommendations** for improving the resume by addressing the missing skills and aligning the content with job requirements to increase ATS compatibility.
    """

    # Get the response from the AI model
    response = model.generate_content(prompt)
    return response.text


# Streamlit app setup
def main():
    st.write("Welcome to the ATS Checker! 🚀")
    st.write("Upload your resume and provide the job role and description to get valuable insights and optimize your resume for ATS.")
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
    job_role = st.text_input("Enter the job role you are applying for")
    desc = st.text_area("Enter the job description")
    btn = st.button("Analyze")

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
                result = ats_check_ai_based(resume_text, job_role, desc)
                st.write(result)
            else:
                st.error("Failed to extract text from the PDF. Please try again with a different file.")

if __name__ == "__main__":
    main()
