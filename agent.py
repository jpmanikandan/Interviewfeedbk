from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage

class InterviewAgent:
    def __init__(self, api_key):
        self.llm = ChatOpenAI(
            model="gpt-4o",  # Or gpt-3.5-turbo if preferred
            temperature=0.7,
            openai_api_key=api_key
        )
        self.conversation_history = []

    def generate_question(self, resume_text, job_description, history):
        """
        Generates the next interview question based on context.
        """
        system_prompt = """You are an expert technical interviewer. 
        Your goal is to assess the candidate's suitability for the role based on their resume and the job description.
        
        Resume Context:
        {resume_text}
        
        Job Description:
        {job_description}
        
        Instructions:
        1. Ask one clear, relevant question at a time.
        2. Start with an introduction if the history is empty.
        3. Dig deeper into their experience, specific skills mentioned in the resume, or requirements in the JD.
        4. If the candidate's answer is vague, ask a follow-up question.
        5. Keep the tone professional but encouraging.
        6. Do not repeat questions.
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human", "Generate the next question or response.")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        response = chain.invoke({
            "resume_text": resume_text,
            "job_description": job_description,
            "history": history
        })
        
        return response

    def generate_report(self, resume_text, job_description, history):
        """
        Generates a final evaluation report.
        """
        system_prompt = """You are a Senior Hiring Manager. 
        Review the following interview transcript and generate a detailed candidate evaluation report.
        
        Resume Context:
        {resume_text}
        
        Job Description:
        {job_description}
        
        Interview Transcript:
        {transcript}
        
        Report Structure:
        1. **Candidate Summary**: Brief overview of the candidate's profile.
        2. **Strengths**: Key technical and soft skills demonstrated.
        3. **Weaknesses/Areas for Improvement**: Gaps identified during the interview.
        4. **Rating**: Score out of 10 based on fit for the role.
        5. **Recommendation**: Hire, No Hire, or Next Round.
        """
        
        # Convert history to a readable transcript string
        transcript = ""
        for msg in history:
            role = "Interviewer" if isinstance(msg, AIMessage) else "Candidate"
            transcript += f"{role}: {msg.content}\n"

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt)
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        report = chain.invoke({
            "resume_text": resume_text,
            "job_description": job_description,
            "transcript": transcript
        })
        
        return report

    def evaluate_candidate(self, resume_text, job_description):
        """
        Evaluates a single candidate without an interactive interview.
        Returns a JSON-compatible dictionary.
        """
        system_prompt = """You are an expert Technical Recruiter.
        Evaluate the candidate's resume against the Job Description.
        
        Resume:
        {resume_text}
        
        Job Description:
        {job_description}
        
        Return a JSON object with the following fields:
        - name: Candidate's name (extract from resume)
        - score: Integer (0-100) representing fit
        - summary: 2-sentence summary of the candidate
        - strengths: List of strings
        - weaknesses: List of strings
        
        Ensure the output is valid JSON. Do not include markdown formatting like ```json.
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt)
        ])
        
        # Use simple StrOutputParser and manual JSON parsing for robustness, 
        # or JsonOutputParser if available. For now, we'll rely on the prompt.
        chain = prompt | self.llm | StrOutputParser()
        
        response = chain.invoke({
            "resume_text": resume_text,
            "job_description": job_description
        })
        
        # Clean up potential markdown formatting
        response = response.replace("```json", "").replace("```", "").strip()
        
        import json
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback if JSON fails
            return {
                "name": "Unknown",
                "score": 0,
                "summary": "Error parsing AI response.",
                "strengths": [],
                "weaknesses": []
            }
