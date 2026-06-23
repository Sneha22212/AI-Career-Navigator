from google import genai
from dotenv import load_dotenv
from flask import Flask, render_template, request, send_file
import os
load_dotenv()
import pdfplumber
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet

# GEMINI CONFIG

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# FLASK CONFIG

app = Flask(__name__)

latest_report = {}

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# HOME PAGE

@app.route("/")
def home():
    return render_template("index.html")

# RESUME UPLOAD

@app.route("/upload", methods=["POST"])
def upload():

    # Resume file
    file = request.files["resume"]

    # Target role
    target_role = request.form["target_role"]

    # Job Description
    job_description = request.form.get(
      "job_description",
      ""
    )

    if file.filename == "":
        return "No file selected"

    # Save PDF
    filepath = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    file.save(filepath)

    print("Saved at:", filepath)

    # PDF TEXT EXTRACTION

    extracted_text = ""

    with pdfplumber.open(filepath) as pdf:

        for page in pdf.pages:

            text = page.extract_text()

            if text:
                extracted_text += text + "\n"

    # GEMINI PROMPT

    prompt = f"""
You are an expert ATS system and career mentor.

Analyze the resume according to the target role.

TARGET ROLE:
{target_role}

JOB DESCRIPTION:
{job_description}

IMPORTANT RULES:

1. Do NOT use markdown.
2. Do NOT use * symbols.
3. Do NOT use # symbols.
4. Keep output clean.
5. Follow exact format.

FORMAT:

ATS_SCORE: <number>

===ROLE_MATCH===

Strong Match
OR
Moderate Match
OR
Weak Match

===JD_MATCH_SCORE===

85%

===MISSING_KEYWORDS===

suggest some missing keywords according to the role 4-5, with numbering 

===JD_IMPROVEMENTS===

give important3-4 improvement tips

===SUMMARY===

2-3 line professional summary of the candidate.

===STRENGTHS===

Provide strengths only.
Do not add numbering.

===WEAKNESSES===

Provide weaknesses only.
Do not add numbering. 

===TOP_SKILLS===

Provide skill names only.
Do not add numbering.

===MISSING_SKILLS===

Provide missing skill names only.
Do not add numbering. 

===INTERVIEW_QUESTIONS===

Provide 5-6 interview questions.
Do not add numbering. 

===SUGGESTED_PROJECTS===

Provide 3-4 project names only.
Do not add numbering.

===CAREER_IMPROVEMENT_SUGGESTIONS===

Provide important suggestions only.
Do not add numbering. 

===CAREER_ROADMAP===

steps for roadmap

Generate a personalized career roadmap for the target role.
The roadmap should contain 5 logical steps that help the candidate reach the target role.

IMPORTANT:

Be consistent.

If the same resume and target role are analyzed again,
the ATS score and role match should remain nearly identical.

Do not randomly change scores.

Resume:

{extracted_text}
"""

    # GEMINI RESPONSE

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    ai_analysis = response.text

    print(ai_analysis)

    # SECTION PARSING

    sections = {}

    current_section = "START"

    sections[current_section] = []

    for line in ai_analysis.splitlines():

        line = line.strip()

        if line.startswith("===") and line.endswith("==="):

            current_section = line

            sections[current_section] = []

        else:

            if line != "":
                sections[current_section].append(line)

    # ATS SCORE

    ats_score = "N/A"

    for line in ai_analysis.splitlines():

        if line.startswith("ATS_SCORE:"):

            ats_score = line.split(":")[1].strip()

            break
        
    # ROLE MATCH

    role_match = "N/A"

    role_match_section = sections.get(
        "===ROLE_MATCH===",
        []
    )

    if len(role_match_section) > 0:

        role_match = role_match_section[0]

    # =========================
    # SKILLS RADAR CHART

    skills = [
        "Python",
        "SQL",
        "ML",
        "Projects",
        "Communication"
    ]

    scores = [90, 80, 85, 75, 70]

    angles = np.linspace(
        0,
        2 * np.pi,
        len(skills),
        endpoint=False
    ).tolist()

    scores += scores[:1]
    angles += angles[:1]

    fig = plt.figure(figsize=(6,6))

    ax = plt.subplot(111, polar=True)

    ax.plot(
        angles,
        scores,
        linewidth=2
    )
    ax.fill(
        angles,
        scores,
        alpha=0.25
    )

    ax.set_xticks(
        angles[:-1]
    )

    ax.set_xticklabels(
        skills
    )

    chart_path = os.path.join(
        "static",
        "charts",
        "radar.png"
    )

    plt.savefig(
        chart_path,
        bbox_inches="tight"
    )

    plt.close()

    # JD MATCH SCORE

    jd_match_score = "N/A"

    jd_section = sections.get(
      "===JD_MATCH_SCORE===",
      []
    )

    if len(jd_section) > 0:

      jd_match_score = jd_section[0]


    global latest_report

    latest_report = {

      "ats_score": ats_score,

      "target_role": target_role,

      "role_match": role_match,

      "jd_match_score": jd_match_score,

      "summary": sections.get(
        "===SUMMARY===",
        []
      ),

      "strengths": sections.get(
        "===STRENGTHS===",
        []
      ),

      "weaknesses": sections.get(
        "===WEAKNESSES===",
        []
      ),

      "top_skills": sections.get(
        "===TOP_SKILLS===",
        []
      ),

      "missing_skills": sections.get(
        "===MISSING_SKILLS===",
        []
      )
    }

    # RENDER RESULT PAGE

    ring_degree = int(float(ats_score) * 3.6)

    return render_template(

        "result.html",

        ats_score=ats_score,
        ring_degree=ring_degree,
        target_role=target_role,
        role_match=role_match,
        jd_match_score=jd_match_score,

        missing_keywords=sections.get(
          "===MISSING_KEYWORDS===",
          []
        ),

        jd_improvements=sections.get(
          "===JD_IMPROVEMENTS===",
          []
        ),  

        summary=sections.get(
            "===SUMMARY===",
            []
        ),

        strengths=sections.get(
            "===STRENGTHS===",
            []
        ),

        weaknesses=sections.get(
            "===WEAKNESSES===",
            []
        ),

        top_skills=sections.get(
            "===TOP_SKILLS===",
            []
        ),

        missing_skills=sections.get(
            "===MISSING_SKILLS===",
            []
        ),

        interview_questions=sections.get(
            "===INTERVIEW_QUESTIONS===",
            []
        ),

        suggested_projects=sections.get(
            "===SUGGESTED_PROJECTS===",
            []
        ),

        career_suggestions=sections.get(
            "===CAREER_IMPROVEMENT_SUGGESTIONS===",
            []
        ),

        career_roadmap=sections.get(
            "===CAREER_ROADMAP===",
            []
)
    )

# DOWNLOAD PDF

# DOWNLOAD PDF

@app.route("/download-report")
def download_report():

    pdf_path = "career_report.pdf"

    doc = SimpleDocTemplate(pdf_path)

    styles = getSampleStyleSheet()

    content = []

    # TITLE

    content.append(
        Paragraph(
            "AI Career Navigator Report",
            styles["Title"]
        )
    )

    content.append(Spacer(1,20))

    # BASIC INFO

    content.append(
        Paragraph(
            f"ATS Score: {latest_report.get('ats_score','N/A')}",
            styles["BodyText"]
        )
    )

    content.append(
        Paragraph(
            f"Target Role: {latest_report.get('target_role','N/A')}",
            styles["BodyText"]
        )
    )

    content.append(
        Paragraph(
            f"JD Match Score: {latest_report.get('jd_match_score','N/A')}",
            styles["BodyText"]
        )
    )

    content.append(
        Paragraph(
            f"Role Match: {latest_report.get('role_match','N/A')}",
            styles["BodyText"]
        )
    )

    content.append(Spacer(1,20))

    # SUMMARY

    content.append(
        Paragraph(
            "Candidate Summary",
            styles["Heading2"]
        )
    )

    for item in latest_report.get(
        "summary",
        []
    ):

        content.append(
            Paragraph(
                item,
                styles["BodyText"]
            )
        )

    content.append(Spacer(1,15))

    # TOP SKILLS

    content.append(
        Paragraph(
            "Top Skills",
            styles["Heading2"]
        )
    )

    for item in latest_report.get(
        "top_skills",
        []
    ):

        content.append(
            Paragraph(
                f"• {item}",
                styles["BodyText"]
            )
        )

    content.append(Spacer(1,15))

    # MISSING SKILLS

    content.append(
        Paragraph(
            "Missing Skills",
            styles["Heading2"]
        )
    )

    for item in latest_report.get(
        "missing_skills",
        []
    ):

        content.append(
            Paragraph(
                f"• {item}",
                styles["BodyText"]
            )
        )

    content.append(Spacer(1,15))

    # STRENGTHS

    content.append(
        Paragraph(
            "Strengths",
            styles["Heading2"]
        )
    )

    for item in latest_report.get(
        "strengths",
        []
    ):

        content.append(
            Paragraph(
                f"• {item}",
                styles["BodyText"]
            )
        )

    content.append(Spacer(1,15))

    # WEAKNESSES

    content.append(
        Paragraph(
            "Weaknesses",
            styles["Heading2"]
        )
    )

    for item in latest_report.get(
        "weaknesses",
        []
    ):

        content.append(
            Paragraph(
                f"• {item}",
                styles["BodyText"]
            )
        )

    doc.build(content)

    return send_file(
        pdf_path,
        as_attachment=True
    )


# RUN APP

if __name__ == "__main__":

    app.run(
        debug=True,
        port=5001
    )