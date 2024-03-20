import spacy
import pandas as pd
from pdfminer.high_level import extract_text
from docx import Document
import tempfile
import os

# Load spaCy's English-language model
nlp = spacy.load("en_core_web_sm")

# Read skills into a list from the CSV file
skills_df = pd.read_csv('C:/Users/saiha/OneDrive/Desktop/295 - workbook updates/jobeasy/jobeasy/core/skills.csv')
skills_list = skills_df.columns.tolist()  # Assumes the first row contains skill names

def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)

def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    return " ".join(paragraph.text for paragraph in doc.paragraphs)

def assign_skill_weights(text, skills_list, section_headings):
    skill_details = {}
    current_section = None
    section_headings_lower = {heading.lower(): heading for heading in section_headings}

    for line in text.split('\n'):
        line_clean = line.strip().lower()
        if line_clean in section_headings_lower:
            current_section = section_headings_lower[line_clean]
        weight = 0.5
        if current_section:
            if "skills" in current_section.lower():
                weight = 1.0
            elif "experience" in current_section.lower() or "work" in current_section.lower():
                weight = 0.8
        for word in line.split():
            word_lower = word.lower().strip(",. ")
            if word_lower in skills_list:
                if word_lower not in skill_details:
                    skill_details[word_lower] = {'weight': 0, 'sections': set()}
                skill_details[word_lower]['weight'] += weight
                skill_details[word_lower]['sections'].add(current_section)
    return skill_details

def process_resume(file_path, file_type, skills_list, section_headings):
    text = ''
    if file_type == 'pdf':
        text = extract_text_from_pdf(file_path)
    elif file_type == 'docx':
        text = extract_text_from_docx(file_path)
    skills_lower = [skill.lower() for skill in skills_list]
    skill_details = assign_skill_weights(text, skills_lower, section_headings)
    return skill_details

non_skill_keywords = ["jose", "engineering", "benchmark", "system", "sales", "money"]
section_headings = [
    "Work Experience", "Experience", "Professional Experience", "Employment History",
    "Education", "Academic Background", "Qualifications",
    "Skills", "Technical Skills", "Professional Skills", "Skill Highlights",
    "Certifications", "Licenses",
    "Projects", "Key Projects",
    "Awards", "Achievements", "Honors",
    "Publications",
    "Conferences", "Presentations",
    "Languages",
    "Volunteer Work", "Volunteer Experience",
    "Interests", "Hobbies", "Personal Interests",
    "References", "Professional References"
]

def analyze_resume_text(resume_text):
    # Assuming resume_text is a string containing the entire text of the resume
    skill_details = assign_skill_weights(resume_text, skills_list, section_headings)

    # Filter and sort skills
    filtered_skills = {skill: details for skill, details in skill_details.items() if skill not in non_skill_keywords}
    threshold_weight = 1.0
    skills_above_threshold = {skill: details for skill, details in filtered_skills.items() if details['weight'] >= threshold_weight}
    sorted_skills_above_threshold = sorted(skills_above_threshold.items(), key=lambda x: (-x[1]['weight'], x[0]))

    return sorted_skills_above_threshold[:10]  # Return top 10 skills