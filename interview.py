import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-pro")

# Function to generate questions
def get_questions(title, years):
    prompt = f"Generate 5 HR interview questions for a {title} with {years} years of experience in the field. (only questions required). Pretend you are talking directly to the interviewee."
    response = model.generate_content(prompt)
    return response.text.split("\n")

# Function to generate feedback and improved answers
def generate_feedback(job_title, experience):
    feedback_text = ""
    for i, response in enumerate(st.session_state.responses):
        question = response['question']
        answer = response.get('text', "No answer provided.")
        
        prompt = (
            f"You are an experienced HR interviewer and analyze your response to a behavioral question for {job_title} role with {experience} years of experience. Give feedback on the response provided by the interviewee in 4-5 sentences. This feedback will help the interviewee understand their strengths and areas for improvement in future interviews. Also, provide an improved answer which will help the interviewee in the future.\n\n"
            f"**Question:** {question}\n\n"
            f"**Your Answer:** {answer}\n\n"
            f"**Feedback:**"
        )
        feedback_response = model.generate_content(prompt)
        feedback_text += f"Question {i + 1}: {question}\n\n"
        feedback_text += feedback_response.text + "\n\n\n"
    return feedback_text

# Display a question and accept responses
def display_question():
    question_no = st.session_state.question_no
    question = st.session_state.questions[question_no]
    
    st.write(f"Question {question_no + 1}: {question}")
    text_response = st.text_area("Your Answer (Text)")
    
    if st.button("Submit Answer"):
        st.session_state.responses.append({"text": text_response, "question": question})
        st.session_state.question_no += 1
        st.rerun()

# Main function
def main():
    st.header("HR Interview - SAM 👩‍💼👨‍💼")
    st.write("We're here to help you practice for your upcoming HR interviews. We'll guide you through a series of questions tailored to the job role and experience level you provide. 💼")
    
    job_title = st.text_input("Please enter the Job Title you're applying for:") 
    experience = st.text_input("How many years of experience do you have in this role?")

    st.write("\n**Important Notice:** You will have 1.5 minutes ⏳ to answer each question. Make sure you prepare your responses within this time frame to simulate real interview conditions. 🕒")
    
    start = st.button("Start Interview 🚀")
    if start and job_title and experience:
        st.session_state["questions"] = get_questions(job_title, experience)
        st.session_state["responses"] = []  
        st.session_state["question_no"] = 0
        st.rerun()
    else:
        st.write("To begin the interview, please fill in the job title and years of experience, then click 'Start Interview'. 🛠️")

    if "questions" in st.session_state:
        if st.session_state.question_no < len(st.session_state.questions):
            display_question()
        else:
            st.write("Thank you for your responses!")

        if st.button("FEEDBACK"):
            st.write("**Feedback and Review:** Here's a summary of your interview questions and your responses. 📝🔍")
            feedback_text = generate_feedback(job_title, experience)
            st.write(feedback_text)
    else:
        return

if __name__ == "__main__":
    main()
