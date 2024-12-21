import streamlit as st
import roadmap
import resume
import ats
import tech
import interview

#py -m streamlit run main.py
# Set page configuration at the very beginning
st.set_page_config(
    page_title="prep.ai",
    page_icon="🎓",
    layout="wide",
)

class MultiApp:
    def __init__(self):
        self.apps = [{"title": "Home", "function": self.home_page}]

    def add_app(self, title, func):
        self.apps.append({
            "title": title,
            "function": func
        })

    def run(self):
        choice = st.sidebar.selectbox(
            'Go to',
            [app['title'] for app in self.apps]
        )

        for app in self.apps:
            if app['title'] == choice:
                app['function']()

    def home_page(self):
        st.title('Welcome to prep.ai')
        st.write('''
        🚀 Welcome to prep.ai, your ultimate companion in the journey to land your dream job! Here's what you can do with prep.ai:
        
        - **Roadmap Generator**: 🗺️ Get a personalized learning roadmap to guide you through the skills and knowledge you need.
        - **Resume Analyzer**: 📄 Upload your resume and get instant feedback to improve it.
        - **ATS Checker**: 🎯 Check how well your resume matches the job description and optimize it for Applicant Tracking Systems (ATS).
        - **HR Chatbot**: 🤖 Practice HR interview questions with a smart, interactive chatbot.
        - **Tech Assistant**: 🛠️ Dive deep into technical interview questions and coding scenarios to sharpen your skills.
        
        🌟 Select an option from the sidebar to get started on your path to career success!
        ''')


app = MultiApp()

st.sidebar.title('Navigation')
app.add_app("Roadmap Generator", roadmap.main)
app.add_app("Resume Analyzer", resume.main)
app.add_app("ATS Checker", ats.main)
app.add_app("HR Chatbot", interview.main)
app.add_app("Tech Assistant", tech.main)

app.run()
