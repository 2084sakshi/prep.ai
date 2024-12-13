import os
from dotenv import load_dotenv
import google.generativeai as genai
import streamlit as st

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

seed_questions = """
1. "Tell me about yourself. (General intro, highlight relevant skills & experience)"
2.Why would you be a good fit for our team? (Team dynamics, collaborative spirit)"
3. "Describe a time you had to overcome a significant challenge at work. (Problem-solving, resilience)"
4. "Give an example of when you had to work in a team to achieve a common goal. (Teamwork, collaboration)"
5. "How do you prioritize tasks when faced with multiple deadlines? (Time management, organization)"
6. "Tell me about a time you made a mistake. What did you learn from it? (Self-awareness, learning from errors)"
7. "What are your strengths and how do they apply to this role? (Self-assessment, relevant skills)"
8. "How do you handle stress and pressure in a professional environment? (Stress management, coping skills)"
9. "Where do you see your career progressing in the next 5 years? (Career goals, ambition)"
10. "What do you like to do in your free time? (Personality, cultural fit, well-roundedness)"
11.If a client was upset, how would you handle the situation?( Scenario-based, judgment, communication)"
"""

# Function to generate HR questions based on seed questions
def get_questions(title, years):
    prompt = f"""
    Based on the following examples, generate 5 new HR interview questions for a {title} with {years} years of experience in the field:

    Seed Questions:
    {seed_questions}

    **Note:** Be highly dependent on the seed bank questions to understand what is considered in the output.

    **Format for Output:** 
    Please provide exactly 5 questions in the following format:
    1."Question 1"
    2. "Question 2"
    3. "Question 3"
    4. "Question 4"
    5. "Question 5"
    
    Make sure the questions are formatted as a list of bullet points, with no extra text or explanations.

    Generate 5 new HR interview questions for the specified role and experience level:
    """
    
    # Call Google Gemini API to generate questions
    response = genai.GenerativeModel("gemini-pro").generate_content(prompt)
    print("Raw API Response (HR Questions):\n", response.text)
    return response.text.split("\n")

# Function to generate feedback and improved answers
def generate_feedback(job_title, experience):
    feedback_text = ""
    for i, response in enumerate(st.session_state.responses):
        question = response['question']
        answer = response.get('text', "No answer provided.")
        
        feedback_prompt = (
            f"You are an experienced HR interviewer and analyze your response to a behavioral question for {job_title} role with {experience} years of experience. "
            f"Give feedback on the response provided by the interviewee in 4-5 sentences. This feedback will help the interviewee understand their strengths and areas for improvement in future interviews. "
            f"Also, provide an improved answer which will help the interviewee in the future.\n\n"
            f"**Question:** {question}\n\n"
            f"**Your Answer:** {answer}\n\n"
            f"**Feedback:**"
        )

        feedback_response = genai.GenerativeModel("gemini-pro").generate_content(feedback_prompt)
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
