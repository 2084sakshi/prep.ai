import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-pro")
def get_technical_questions(role, company, additional_info=None, desired_questions=12):
    prompt = f"""
    Generate {desired_questions} concise technical interview questions for a {role} position at {company}, each with 4 multiple-choice options.
    1. Direct Knowledge Questions - Test basic knowledge with single-word or simple answers.
    2. Scenario-Based Questions - Present a scenario requiring application of knowledge to solve it.
    3. Problem-Solving Questions - Pose a problem or challenge to assess problem-solving skills.
    4. other - Ask questions that are relevant to the role and company and test the candidate's understanding of the domain.

    Each question should be followed by 4 options, and the correct answer should be clearly specified as the full answer text, not just the letter.
    The format should be as follows:
    Question: <question>
    a) <option 1>
    b) <option 2>
    c) <option 3>
    d) <option 4>
    Correct Answer: <correct answer text>

    Please ensure that the questions are brief and directly relevant to the {role} at {company}.
    Consider {additional_info} for aligning questions with specific interview expectations.
    """

    # Generate response
    try:
        response = model.generate_content(prompt)
    except Exception as e:
        st.error(f"An error occurred while generating general questions: {e}")
        return []

    # Debugging: Print the raw response for inspection
    print("Raw API Response (General Questions):\n", response.text)

    # Initialize questions list
    questions = []
    
    # Split by double newlines to get question blocks
    blocks = response.text.strip().split("\n\n")

    for block in blocks:
        lines = block.strip().split("\n")
        
        if len(lines) < 6:  # We expect at least 6 lines: question + 4 options + correct answer
            print("Malformed question block, skipping:\n", block)
            continue

        # Extract the question (first line) and options (next four lines)
        question_line = lines[0].strip()
        options = [line.strip() for line in lines[1:5]]  # The next four lines should be options
        correct_answer_line = lines[5].strip()
        
        # Check for the correct format and assign question and answer
        question_text = question_line
        if "Question:" in question_line:
            question_text = question_line.split("Question: ", 1)[1].strip()

        # Validate the options and correct answer format
        if len(options) != 4 or not correct_answer_line.startswith("Correct Answer:"):
            print("Malformed question block, skipping:\n", block)
            continue
        
        correct_answer_text = correct_answer_line.split("Correct Answer: ", 1)[1].strip()

        questions.append({
            "question": question_text,
            "options": options,
            "correct_answer": correct_answer_text
        })

    return questions

def display_question():
    # Ensure question_no is within the bounds of the questions list
    question_no = st.session_state.question_no
    questions = st.session_state.questions
    
    # Check if questions have been properly stored
    if not isinstance(questions, list) or not all(isinstance(q, dict) for q in questions):
        st.error("Questions data is not properly formatted. Please check the question generation.")
        return

    # Access current question data
    question_data = questions[question_no]  # This should be a dictionary

    # Display the question text
    st.write(f"**Question {question_no + 1}:** {question_data['question']}")
    
    # Display the options as radio buttons
    selected_option = st.radio(
        "Select an option:",
        options=question_data["options"],
        key=f"selected_option_{question_no}"
    )
    
    # Submit button to record answer
    if st.button("Submit Answer", key=f"submit_{question_no}"):
        if selected_option:
            # Store the user's selected option
            st.session_state.responses.append({
                "question": question_data["question"],
                "selected_option": selected_option,
                "correct_answer": question_data["correct_answer"]
            })
            st.session_state.question_no += 1
            st.rerun()  # Rerun to show the next question
        else:
            st.warning("Please select an option before submitting.")

def generate_feedback(responses):
    total_questions = len(responses)
    correct_answers = 0  # Initialize correct answers counter
    detailed_feedback = []  # For detailed feedback per question

    for response in responses:
        feedback_entry = {}
        feedback_entry["question"] = response["question"]
        feedback_entry["selected_option"] = response["selected_option"]
        feedback_entry["correct_answer"] = response["correct_answer"]
        
        # Remove any leading letter option (e.g., "a) ") for comparison
        selected_core_text = response["selected_option"].split(")", 1)[-1].strip()
        correct_core_text = response["correct_answer"].split(")", 1)[-1].strip()
        
        # Compare core texts for correctness
        if selected_core_text == correct_core_text:
            feedback_entry["feedback"] = "✅ Correct! Well done!"
            correct_answers += 1  # Increment correct answers counter
        else:
            feedback_entry["feedback"] = f"❌ Incorrect! The correct answer is: **{response['correct_answer']}**"

        detailed_feedback.append(feedback_entry)

    # Prepare overall performance summary
    performance_summary = []
    performance_summary.append(f"You answered **{total_questions}** questions in total.")
    performance_summary.append(f"You got **{correct_answers}** correct and **{total_questions - correct_answers}** incorrect.")
    
    if total_questions > 0:
        accuracy = correct_answers / total_questions
        performance_summary.append(f"Your accuracy is **{accuracy:.2%}**.")
        if accuracy < 0.6:  # Example threshold
            performance_summary.append("Consider reviewing the topics covered in the questions.")

    return detailed_feedback, performance_summary

def main():
    st.title("🧑‍💻 Technical Interview Assistant")
    st.subheader("Ready to tackle your interview? Let’s begin!")

    # Input Section for Company, Role, and Additional Info
    company = st.text_input("🏢 Enter the Company Name")
    role = st.text_input("💼 Enter the Job Role")
    additional_info = st.text_area("💡 Enter any additional info about the role or interview focus")
    start = st.button("🚀 Start Interview")

    # Initialize questions and reset session state on button click
    if start and company and role:
        questions = get_technical_questions(role, company, additional_info)  # Make sure this function is defined elsewhere

        if questions:  # Check if questions were retrieved successfully
            st.session_state["questions"] = questions
            st.session_state["responses"] = []  
            st.session_state["question_no"] = 0  # Initialize question index
            st.rerun()  # Refresh to display the first question
        else:
            st.error("Failed to retrieve questions. Please try again.")

    # Display questions if they have been initialized
    if "questions" in st.session_state:
        if st.session_state.question_no < len(st.session_state.questions):
            display_question()
        else:
            st.write("Thank you for your responses!")
            
            # Generate feedback for all collected responses
            detailed_feedback, performance_summary = generate_feedback(st.session_state.responses)

            # Display detailed feedback for each question
            for entry in detailed_feedback:
                st.write(f"**Question:** {entry['question']}")
                st.write(f"**Your Answer:** {entry['selected_option']}")
                st.write(entry["feedback"])
                st.write("---")  # Separator for readability
            
            # Display overall performance summary
            for line in performance_summary:
                st.write(line)


if __name__ == "__main__":
    main()
