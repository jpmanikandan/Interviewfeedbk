import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

import streamlit as st
import pandas as pd
from utils import extract_text_from_pdf
from agent import InterviewAgent
from langchain_core.messages import HumanMessage, AIMessage

# Page Config
st.set_page_config(page_title="AI Interviewer Agent", layout="wide")

# Sidebar
with st.sidebar:
    st.title("Configuration")
    
    # Mode Selection
    mode = st.radio("Select Mode", ["Interactive Interview", "Bulk Screening"])
    
    # API Key
    # Try to load from .env, then secrets, but allow manual override
    env_key = os.getenv("OPENAI_API_KEY", "")
    secrets_key = st.secrets.get("OPENAI_API_KEY", "")
    
    source = "Manual"
    default_api_key = ""
    
    if env_key:
        default_api_key = env_key
        source = "Environment (.env)"
    elif secrets_key:
        default_api_key = secrets_key
        source = "Secrets (secrets.toml)"
        
    api_key = st.text_input("OpenAI API Key", value=default_api_key, type="password")

    if api_key:
        if api_key == default_api_key:
            st.caption(f"✅ Key loaded from {source}")
        else:
            st.caption("✏️ Key manually entered")
    else:
        st.warning("Please enter your OpenAI API Key to proceed.")
    
    job_description = st.text_area("Job Description", height=200, placeholder="Paste the JD here...")
    
    if mode == "Interactive Interview":
        if st.button("Reset Interview"):
            st.session_state.messages = []
            st.session_state.interview_active = False
            st.session_state.resume_text = ""
            st.rerun()

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "interview_active" not in st.session_state:
    st.session_state.interview_active = False
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""

# --- INTERACTIVE INTERVIEW MODE ---
if mode == "Interactive Interview":
    st.title("🤖 AI Interviewer Agent")
    st.markdown("Upload your resume and get interviewed by an AI agent.")

    # File Upload
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

    if uploaded_file and api_key and job_description:
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

            # Check for exit condition
            if "end interview" in prompt.lower():
                st.session_state.interview_active = False
                st.rerun()
            
            # Check if we have asked 5 questions
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
                st.download_button("Download Report", report, file_name="candidate_report.md")

# --- BULK SCREENING MODE ---
elif mode == "Bulk Screening":
    st.title("🚀 Bulk Resume Screening")
    st.markdown("Upload multiple resumes to screen and rank them against the Job Description.")
    
    uploaded_files = st.file_uploader("Upload Resumes (PDF)", type=["pdf"], accept_multiple_files=True)
    
    if uploaded_files and api_key and job_description:
        if st.button(f"Screen {len(uploaded_files)} Candidates"):
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            agent = InterviewAgent(api_key)
            
            for i, file in enumerate(uploaded_files):
                status_text.text(f"Processing {file.name}...")
                
                # Extract Text
                text = extract_text_from_pdf(file)
                
                if "Error reading PDF" in text:
                    st.error(f"Failed to read {file.name}")
                    continue
                
                # Evaluate
                evaluation = agent.evaluate_candidate(text, job_description)
                evaluation["filename"] = file.name
                results.append(evaluation)
                
                # Update Progress
                progress_bar.progress((i + 1) / len(uploaded_files))
            
            status_text.text("Processing Complete!")
            
            # Process Results
            if results:
                df = pd.DataFrame(results)
                
                # Sort by Score
                df = df.sort_values(by="score", ascending=False).reset_index(drop=True)
                
                st.divider()
                st.subheader("🏆 Top 10 Candidates")
                
                # Display Top 10 Cards
                top_10 = df.head(10)
                
                for index, row in top_10.iterrows():
                    with st.expander(f"#{index+1} {row['name']} - Score: {row['score']}/100"):
                        st.write(f"**Summary:** {row['summary']}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("✅ **Strengths**")
                            for s in row['strengths']:
                                st.write(f"- {s}")
                        with col2:
                            st.write("⚠️ **Weaknesses**")
                            for w in row['weaknesses']:
                                st.write(f"- {w}")
                                
                st.divider()
                st.subheader("📊 Full Rankings")
                st.dataframe(
                    df[["score", "name", "filename", "summary"]],
                    use_container_width=True,
                    hide_index=True
                )
                
                # Download CSV
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "Download Full Report (CSV)",
                    csv,
                    "candidates_ranking.csv",
                    "text/csv",
                    key='download-csv'
                )

    elif not api_key:
        st.warning("Please enter your OpenAI API Key in the sidebar.")
    elif not job_description:
        st.warning("Please enter a Job Description in the sidebar.")
