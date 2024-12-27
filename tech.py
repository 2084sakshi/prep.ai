import streamlit as st
import os
from dotenv import load_dotenv
import json
import google.generativeai as genai
import re

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-pro")

'''
def sanitize_output(text):
    # Escape backslashes
    sanitized = text.replace("\\", "\\\\")    
    # Remove newlines, carriage returns, and any unwanted whitespace in ASCII art or other multiline content
    sanitized = sanitized.replace("\n", " ").replace("\r", "")  # Remove newlines and carriage returns   
    # Remove non-JSON control characters (ASCII 0-31, 127)
    sanitized = re.sub(r'[\x00-\x1F\x7F]', '', sanitized)    
    # Replace multiple spaces with a single space
    sanitized = re.sub(r'\s+', ' ', sanitized)  
    sanitized = sanitized.replace("'", '"')
    # Escape double quotes
    sanitized = sanitized.replace('"', '\\"')    
    return sanitized
'''


import json
import streamlit as st

def generate_questions(topic, difficulty, num_questions=10):
    prompt = f"""
    You are an expert question generator for technical interviews. Generate exactly {num_questions} questions on the topic "{topic}" at the "{difficulty}" difficulty level.

    Each question should:
    1. Cover fundamental to advanced concepts within the topic.
    2. Be a mix of multiple-choice, code interpretation, problem-solving, and practical applications.
    3. Include clear options ("a" to "d") and an explanation for the correct answer.
    4. Balance difficulty: 3-4 basic, 3-4 intermediate, and 2-3 advanced questions.
    5. Focus on key concepts like data structures, algorithms, and practical applications.

    Each question must include:
    - A concise question text.
    - Four multiple-choice options labeled "a", "b", "c", "d".
    - The correct answer identified by the full text of the option.
    - A brief explanation for why the correct answer is correct.

    ### Format Specification:
    Return ONLY a valid JSON array with the following structure. Do NOT include any text before or after the JSON array. Do NOT add explanations, preambles, or formatting notes. Return only valid array. JSON format:
    [
        {{
            "question": "<question_text>",
            "options": {{
                "a": "<option_1>",
                "b": "<option_2>",
                "c": "<option_3>",
                "d": "<option_4>"
            }},
            "correct_answer": "<correct_option_text>",  # where correct_option_text is 'a: option_1', 'b: option_2', etc.
            "explanation": "<brief_explanation>"
        }},
        ...
    ]
    """

    try:
        response = model.generate_content(prompt)  # Replace with your API call method
        print("Raw response: ",response.text)
        # Directly convert response to JSON
        if hasattr(response, "content"):
            questions = json.loads(response.content)
        elif hasattr(response, "text"):
            questions = json.loads(response.text)
        else:
            questions = json.loads(str(response))  # Fallback for string representation

        return questions
    except Exception as e:
        st.error(f"Error generating or parsing questions: {e}")
        return []



def display_question():
    question_no = st.session_state.question_no
    questions = st.session_state.questions

    # Ensure we have valid questions loaded
    if not isinstance(questions, list) or not all("question" in q and "options" in q for q in questions):
        st.error("Questions are not properly formatted. Please check the generation step.")
        return

    # Access current question data
    question_data = questions[question_no]

    # Display the question text
    st.write(f"**Question {question_no + 1}:** {question_data['question']}")

    # Display the options as radio buttons
    selected_option = st.radio(
        "Select an option:",
        options=list(question_data["options"].values()),
        key=f"selected_option_{question_no}"
    )

    # Submit button to record answer
    if st.button("Submit Answer", key=f"submit_{question_no}"):
        if selected_option:
            # Store the user's selected option
            st.session_state.responses.append({
                "question": question_data["question"],
                "selected_option": selected_option,
                "correct_answer": question_data["correct_answer"],
                "explanation": question_data["explanation"]
            })
            st.session_state.question_no += 1
            st.rerun()  # Rerun to show the next question
        else:
            st.warning("Please select an option before submitting.")


def generate_feedback(responses):
    total_questions = len(responses)
    correct_answers = 0
    detailed_feedback = []

    for response in responses:
        feedback_entry = {}
        feedback_entry["question"] = response["question"]
        feedback_entry["selected_option"] = response["selected_option"]
        feedback_entry["correct_answer"] = response["correct_answer"]
        feedback_entry["explanation"] = response["explanation"]

        # Extract the answer text from the correct answer (e.g., "a: SELECT" -> "SELECT")
        correct_answer_text = response["correct_answer"].split(":")[1].strip()

        # Compare the selected answer with the correct answer text
        if response["selected_option"] == correct_answer_text:
            feedback_entry["feedback"] = "✅ Correct! Well done!"
            correct_answers += 1
        else:
            # Format the correct answer with its option
            correct_option = response["correct_answer"].split(":")[0]  # Extract the option letter (e.g., 'a', 'b', etc.)
            feedback_entry["feedback"] = f"❌ Incorrect! The correct answer is: **{correct_option}: {correct_answer_text}**"

        detailed_feedback.append(feedback_entry)

    # Display overall performance summary
    st.write("### Performance Summary")
    st.write(f"- Total Questions: **{total_questions}**")
    st.write(f"- Correct Answers: **{correct_answers}**")
    st.write(f"- Incorrect Answers: **{total_questions - correct_answers}**")
    if total_questions > 0:
        accuracy = correct_answers / total_questions
        st.write(f"- Accuracy: **{accuracy:.2%}**")
        if accuracy < 0.6:
            st.warning("Consider reviewing the topics covered in the questions.")

    # Display detailed feedback for each question
    st.write("### Detailed Feedback")
    for feedback in detailed_feedback:
        st.write(f"**Question:** {feedback['question']}")
        st.write(f"- Selected Answer: {feedback['selected_option']}")
        st.write(f"- Correct Answer: {feedback['correct_answer']}")
        st.write(f"- Explanation: {feedback['explanation']}")
        st.write(feedback["feedback"])


def main():
    st.title("🧑‍💻 Technical Interview Assistant")
    st.subheader("Generate and answer technical questions tailored to your needs!")

    # Initialize session state
    if "questions" not in st.session_state:
        st.session_state.questions = []
    if "responses" not in st.session_state:
        st.session_state.responses = []
    if "question_no" not in st.session_state:
        st.session_state.question_no = 0

    topic = st.text_input("📚 Enter the Topic")
    difficulty = st.selectbox("🎯 Select Difficulty Level", ["Easy", "Medium", "Hard"])
    start = st.button("Generate Questions")

    if start and topic and difficulty:
        questions = generate_questions(topic, difficulty)
        if questions:
            st.session_state.questions = questions
            st.session_state.responses = []
            st.session_state.question_no = 0
            st.rerun()
        else:
            st.error("No questions generated. Please try again.")

    if "questions" in st.session_state and st.session_state.question_no < len(st.session_state.questions):
        display_question()
    elif "responses" in st.session_state and st.session_state.question_no >= len(st.session_state.questions):
        generate_feedback(st.session_state.responses)


if __name__ == "__main__":
    main()
