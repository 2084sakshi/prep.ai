import os
from dotenv import load_dotenv
import streamlit as st
from fpdf import FPDF
from io import BytesIO
import google.generativeai as genai

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-pro")

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Roadmap', 0, 1, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(4)

    def chapter_subtitle(self, subtitle):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, subtitle, 0, 1, 'L')
        self.ln(2)

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 5, body)
        self.ln(2)

    def chapter_list(self, items):
        self.set_font('Arial', '', 12)
        for item in items:
            self.cell(0, 5, f'- {item}', 0, 1, 'L')
        self.ln(2)

def sanitize_text(text):
    replacements = {
        '\u2013': '-',   # en dash
        '\u2014': '-',   # em dash
        '\u2022': '-',   # bullet
        '\u2018': "'",   # left single quotation mark
        '\u2019': "'",   # right single quotation mark
        '\u201c': '"',   # left double quotation mark
        '\u201d': '"',   # right double quotation mark
        # Add more replacements as needed
    }
    for search, replace in replacements.items():
        text = text.replace(search, replace)
    return text

def generate_pdf(content):
    pdf = PDF()
    pdf.add_page()

    content = sanitize_text(content)

    lines = content.split('\n')
    for line in lines:
        if line.startswith('**'):
            if line.startswith('**Step'):
                pdf.chapter_title(line.replace('**', '').strip())
            else:
                pdf.chapter_subtitle(line.replace('**', '').strip())
        elif line.startswith('* '):
            items = line.split('* ')[1:]
            pdf.chapter_list(items)
        else:
            pdf.chapter_body(line.strip())

    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer.getvalue()
def main():
    st.title("Roadmap Generator 🛣️")
    st.write("GENERATE A ROADMAP FOR YOUR CAREER !")

    input = st.selectbox("Select a tech career role", [
        "AI Engineer",
        "Machine Learning Engineer",
        "Data Scientist",
        "Computer Vision Specialist",
        "Cybersecurity Analyst",
        "Penetration Tester",
        "Security Architect",
        "Incident Responder",
        "Cloud Architect",
        "Cloud Engineer",
        "DevOps Engineer",
        "Cloud Security Engineer",
        "Data Analyst",
        "Business Intelligence Analyst",
        "Data Engineer",
        "Data Visualization Specialist",
        "Blockchain Developer",
        "Cryptocurrency Analyst",
        "NFT Developer",
        "Smart Contract Auditor",
        "E-commerce Manager",
        "Digital Marketing Specialist",
        "Social Media Marketing Manager",
        "Content Marketing Specialist",
        "UX Designer",
        "UI Designer",
        "UX Researcher",
        "Conversion Rate Optimization (CRO) Specialist",
        "Full Stack Developer",
        "Front-end Developer",
        "Back-end Developer",
        "Mobile Developer",
        "Healthcare Data Analyst",
        "Health Informatics Specialist",
        "Telemedicine Engineer",
        "Medical Device Software Engineer",
        "Sustainability Manager",
        "Environmental Consultant",
        "Climate Change Analyst",
        "Renewable Energy Engineer",
        "Educational Technology Specialist",
        "Instructional Designer",
        "Online Learning Developer",
        "Learning Management System (LMS) Administrator"
    ], index=0, format_func=lambda x: x)

    prompt = f"""
    You are an expert Career Advisor.
    Generate a career roadmap for the given career role: {input}. The roadmap should be structured in four steps.
    Provide resources with links if possible at each step. 

    1. **Step 1: Acquire Foundational Knowledge and Skills**
        - List relevant workshops, bootcamps, online courses, and educational degrees for {input}.
        - Describe the key skills required at this level for {input}, including both technical and soft skills.
        - Include resources such as websites, books, and online communities for further learning in {input}.

    2. **Step 2: Apply Knowledge and Gain Hands-On Experience**
        - Recommend practical projects and challenges to build hands-on experience in {input}.
        - Suggest ways to apply the knowledge in real-world scenarios for {input}, such as internships, volunteer work, and freelance projects.
        - Provide resources such as internship platforms, freelance marketplaces, and portfolio-building tools for {input}.

    3. **Step 3: Job Search and Networking Strategies**
        - Offer advice on searching for job opportunities in {input}, including using job boards and company websites.
        - Give tips and tricks for networking in {input}, such as attending industry events, joining professional associations, and leveraging social media.
        - Include resources like job search websites, networking platforms, and industry groups for {input}.

    4. **Step 4: Stay Relevant and Updated in the Field**
        - Discuss the importance of continuous professional development in {input} and how to stay relevant in a rapidly changing industry.
        - Recommend continuous learning opportunities for {input}, including advanced courses and industry-recognized certifications.
        - Suggest ways to stay updated with industry news and developments in {input}.
    """

    if 'response' not in st.session_state:
        st.session_state.response = ""

    if st.button("Generate Roadmap"):
        if not input:
            st.error("Please enter a valid career field.")
            return

        try:
            response = model.generate_content(prompt)
            st.session_state.response = response.text  # Store the response in session state
        except Exception as e:
            st.error(f"An error occurred while generating the content: {str(e)}")

    # Display the response if available
    if st.session_state.response:
        res = st.session_state.response
       

        if st.button('Generate PDF'):
            try:
                pdf_buffer = generate_pdf(res)
                st.download_button(
                    label='Download PDF',
                    data=pdf_buffer,
                    file_name=f"{input.replace(' ', '_')}_roadmap.pdf",
                    mime='application/pdf'
                )
            except Exception as e:
                st.error(f"An error occurred while generating the PDF: {str(e)}")
        st.markdown(res, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
