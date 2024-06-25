import streamlit as st
from PyPDF2 import PdfReader
import os

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.faiss import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

import google.generativeai as genai
load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-pro")

def res(pdf):
    text = ""
    try:
        pdfreader = PdfReader(pdf)
        for page in pdfreader.pages:
            text += page.extract_text()
        if not text:
            raise ValueError("No text could be extracted from the PDF.")
    except Exception as e:
        st.error(f"Error reading PDF file: {e}")
        return None
    return text
 
def get_text(text):
    try:
        textsplit = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
        chunk = textsplit.split_text(text)
        return chunk
    except Exception as e:
        st.error(f"Error splitting text: {e}")
        return None

def get_vector(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")
    
def get_converse():
    try:
        prompttemplate = """
        You are a professional and experienced resume analyzer. Given the context of a resume, provide a detailed analysis including the following aspects:

1. **Resume Score**: Develop a scoring system based on various factors like keyword matching, skill strength, and formatting. Provide a quick overall assessment of the resume's effectiveness.
3. Top 3 Job Roles: Identify the top 3 job roles that the candidate is best suited for based on their experience, skills, and qualifications.
3.Conclusion/Summary: Provide a concise summary of the overall resume, summarizing the candidate's potential and the key takeaways from the analysis.
4. Good Points: Highlight the strengths of the resume, including notable achievements, relevant skills, and well-presented sections.
5. Areas of Improvement: Identify any weaknesses or areas that need improvement, such as missing information, unclear descriptions, or formatting issues. Provide specific suggestions on how to improve the resume, including tips on better structuring, enhancing descriptions, and adding relevant information.
6.Recommended Skills to Learn: Considering the candidate's current skillset and potential career paths suggested in point 1, recommend additional skills that would be valuable to learn. If possible, include relevant learning resources (online courses, tutorials, certifications) for each recommended skill.

        Context:\n {context}\n
        Answer: """
        
        modele = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
        prompt = PromptTemplate(template=prompttemplate, input_variables=["context"])
        chain = load_qa_chain(llm=modele, prompt=prompt, chain_type="stuff")

        return chain
    except Exception as e:
        st.error(f"Error creating conversational chain: {e}")
        return None

def analyze(text_chunks):
    try:
        embed = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        new_db = FAISS.load_local("faiss_index", embed, allow_dangerous_deserialization=True)
        chain = get_converse()
        docs = new_db.similarity_search(text_chunks)
        if chain:
            docs = [str(doc) for doc in docs]
            response = chain.invoke({"input_documents": docs, "question": text_chunks})
            if response and "output_text" in response:
                st.write(response["output_text"])
            else:
                st.error("Error analyzing resume: No valid response")
    except Exception as e:
        st.error(f"Error analyzing resume: {e}")


def main():
    st.title("Resume Checker")
    st.write("Welcome to Resume Checker!")
    st.write("Our app is designed to help you understand your resume and make it better. 😊")
    st.write("Upload your resume in PDF format to get started. 📄")
   
    pdf = st.file_uploader("Upload File", type=['pdf'])
    submit = st.button("Submit")
    if submit:
        if pdf:
            text = res(pdf)
            if text:
                chunk = get_text(text)
                if chunk:
                    get_vector(chunk)
                    st.success("Resume uploaded successfully")
                    analyze(chunk)
        else:
            st.warning("Please upload a file")

if __name__ == "__main__":
    main()
