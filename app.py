import streamlit as st
from utils import extract_text_from_pdf
from agent import InterviewAgent
from langchain_core.messages import HumanMessage, AIMessage

# Page Config
st.set_page_config(page_title="AI Interviewer Agent", layout="wide")

# Sidebar
with st.sidebar:
    st.title("Configuration")
    
    # Try to load from secrets
    if "OPENAI_API_KEY" in st.secrets:
        api_key = st.secrets["OPENAI_API_KEY"]
        st.success("API Key loaded from secrets")
    else:
        api_key = st.text_input("OpenAI API Key", type="password")
    job_description = st.text_area("Job Description (Optional)", height=200, placeholder="Paste the JD here...")
    
    if st.button("Reset Interview"):
        st.session_state.messages = []
        st.session_state.interview_active = False
        st.session_state.resume_text = ""
        st.rerun()

# Main Content
st.title("🤖 AI Interviewer Agent")
st.markdown("Upload your resume and get interviewed by an AI agent. Receive a detailed report at the end!")

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "interview_active" not in st.session_state:
    st.session_state.interview_active = False
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""

# File Upload
uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

if uploaded_file and api_key:
    if not st.session_state.interview_active and not st.session_state.messages:
        with st.spinner("Analyzing Resume..."):
            text = extract_text_from_pdf(uploaded_file)
            st.session_state.resume_text = text
            st.session_state.interview_active = True
            
            # Initialize Agent
            agent = InterviewAgent(api_key)
            
            # Generate First Question
            initial_question = agent.generate_question(
                st.session_state.resume_text, 
                job_description, 
                []
            )
            st.session_state.messages.append(AIMessage(content=initial_question))
            st.rerun()

# Chat Interface
if st.session_state.interview_active:
    # Display Chat History
    for msg in st.session_state.messages:
        if isinstance(msg, AIMessage):
            with st.chat_message("assistant"):
                st.write(msg.content)
        elif isinstance(msg, HumanMessage):
            with st.chat_message("user"):
                st.write(msg.content)

    # User Input
    if prompt := st.chat_input("Your answer..."):
        st.session_state.messages.append(HumanMessage(content=prompt))
        with st.chat_message("user"):
            st.write(prompt)

        # Check for exit condition (simple keyword for now, or button)
        if "end interview" in prompt.lower():
            st.session_state.interview_active = False
            st.rerun()
        
        # Check if we have asked 5 questions (initial + 4 follow-ups)
        ai_message_count = len([m for m in st.session_state.messages if isinstance(m, AIMessage)])
        
        if ai_message_count >= 5:
            st.session_state.interview_active = False
            st.success("Interview Completed! Please generate your report below.")
            st.rerun()
            
        else:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    agent = InterviewAgent(api_key)
                    response = agent.generate_question(
                        st.session_state.resume_text,
                        job_description,
                        st.session_state.messages
                    )
                    st.write(response)
                    st.session_state.messages.append(AIMessage(content=response))

# Final Report
if not st.session_state.interview_active and st.session_state.messages and api_key:
    st.divider()
    st.subheader("Interview Completed")
    if st.button("Generate Candidate Report"):
        with st.spinner("Generating Report..."):
            agent = InterviewAgent(api_key)
            report = agent.generate_report(
                st.session_state.resume_text,
                job_description,
                st.session_state.messages
            )
            st.markdown(report)
            
            # Option to download report
            st.download_button("Download Report", report, file_name="candidate_report.md")

elif not api_key:
    st.warning("Please enter your OpenAI API Key in the sidebar to start.")
