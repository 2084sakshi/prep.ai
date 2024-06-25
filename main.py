import streamlit as st
import roadmap
import resume
import ats

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
            [app['title'] for app in self.apps],
            format_func=lambda app: app
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
    
    🌟 Select an option from the sidebar to get started on your path to career success!
    ''')


app = MultiApp()

st.sidebar.title('Navigation')
app.add_app("Roadmap Generator", roadmap.main)
app.add_app("Resume Analyzer", resume.main)
app.add_app("ATS Checker", ats.main)

app.run()