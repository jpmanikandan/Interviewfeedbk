from reportlab.pdfgen import canvas
import os

def create_resume(filename, name, skills, experience):
    c = canvas.Canvas(filename)
    c.drawString(100, 800, f"Name: {name}")
    c.drawString(100, 780, f"Skills: {skills}")
    c.drawString(100, 760, f"Experience: {experience}")
    c.save()

resumes = [
    ("resume_alice.pdf", "Alice Smith", "Python, Django, SQL", "5 years backend dev"),
    ("resume_bob.pdf", "Bob Jones", "React, Node.js, CSS", "3 years frontend dev"),
    ("resume_charlie.pdf", "Charlie Brown", "Java, Spring, AWS", "7 years enterprise dev"),
    ("resume_david.pdf", "David Lee", "Python, Machine Learning, PyTorch", "2 years AI researcher"),
    ("resume_eve.pdf", "Eve White", "Project Management, Agile, Jira", "10 years PM")
]

for filename, name, skills, experience in resumes:
    create_resume(filename, name, skills, experience)
    print(f"Created {filename}")
