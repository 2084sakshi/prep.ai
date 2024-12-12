import os
from dotenv import load_dotenv
import streamlit as st
from PyPDF2 import PdfReader
from langchain_community.vectorstores.faiss import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import OpenAI
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
        if not text:
            raise ValueError("No text could be extracted from the PDF.")
    except Exception as e:
        st.error(f"Error reading PDF file: {e}")
        return None
    return text

# Semantic search setup using FAISS
def create_faiss_index(resume_text, job_description):
    """Create a FAISS index from resume and job description."""
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    # Split text into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    resume_chunks = splitter.split_text(resume_text)
    job_desc_chunks = splitter.split_text(job_description)

    docs = resume_chunks + job_desc_chunks
    # Create FAISS index using the embeddings model
    vectorstore = FAISS.from_texts(texts=docs, embedding=embeddings)
    return vectorstore

# Query the FAISS index
def query_faiss_index(vectorstore, question):
    """Query the FAISS index with a specific question."""
    retriever = vectorstore.as_retriever()
    results = retriever.get_relevant_documents(question)
    return results

# Enhanced ATS check function
def ats_check(resume_text, job_role, desc):
    """Generate ATS analysis based on resume text, job role, and job description."""
    vectorstore = create_faiss_index(resume_text, desc)

    # Semantic search for matching skills
    relevant_skills = query_faiss_index(vectorstore, f"What skills are relevant for a {job_role}?")
    extracted_skills = "\n".join([res.page_content for res in relevant_skills])

    prompt = f"""
    You are a professional ATS (Applicant Tracking System) resume analyzer, specializing in matching resumes with job descriptions. Analyze the following resume for the job role , and provide a detailed and accurate analysis with specific recommendations for optimization.

    **Job Role**: {job_role}

    **Resume Text**: 
    {resume_text}

    **Job Description**:
    {desc}

    **Relevant Skills Extracted from Resume**:
    {extracted_skills}

    **Instructions**:
    1. **ATS Compatibility Score**: Provide a numerical score from 0 to 100 representing how well the resume matches the job description in terms of ATS compatibility. 
    2. **Missing Skills**: List specific skills or keywords from the job description that are missing or insufficiently represented in the resume. Include both technical and soft skills, if applicable.
    3. **Optimization Suggestions**: Provide **highly specific recommendations** for improving the resume to increase its chances of passing through an ATS. 
   
    """

    response = model.generate_content(prompt)
    return response.text

# Streamlit app setup
def main():
    st.write("Welcome to the ATS Checker! 🚀")
    st.write("Upload your resume and provide the job role and description to get valuable insights and optimize your resume for ATS.")

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
