# AI Career Navigator

AI Career Navigator is an AI-powered resume analysis platform that helps students and professionals evaluate their resumes against a target role and job description.

The platform uses Gemini AI to provide ATS analysis, skill-gap detection, interview preparation, project recommendations, and personalized career guidance through an interactive dashboard.

## Features

* ATS Score Analysis
* Job Description Matching
* Role Match Evaluation
* Missing Skills Detection
* Missing Keywords Detection
* Candidate Strengths & Weaknesses
* Personalized Interview Questions
* AI-Based Project Suggestions
* Career Improvement Recommendations
* Career Roadmap Generation
* PDF Report Download
* Modern Interactive Dashboard

## Tech Stack

### Frontend

* HTML
* CSS
* JavaScript

### Backend

* Flask (Python)

### AI

* Google Gemini API

### Other Libraries

* pdfplumber
* reportlab
* matplotlib
* python-dotenv

## Project Workflow

1. Upload Resume (PDF)
2. Enter Target Role
3. Optionally Paste Job Description
4. Gemini AI Analyzes Resume
5. Dashboard Displays Results
6. Download Professional PDF Report

## Dashboard Insights

The dashboard provides:

* ATS Score
* JD Match Score
* Role Match
* Candidate Summary
* Strengths
* Weaknesses
* Top Skills
* Missing Skills
* Missing Keywords
* Interview Questions
* Suggested Projects
* Career Suggestions
* Career Roadmap

## Installation

Clone the repository:

```bash
git clone https://github.com/Sneha22212/AI-Career-Navigator.git
```

Move into the project folder:

```bash
cd AI-Career-Navigator
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
GEMINI_API_KEY=your_api_key_here
```

Run the application:

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5001
```

## Future Improvements

* Resume Score History
* Multiple Resume Comparison
* Resume Improvement Suggestions
* Industry-Specific Roadmaps
* AI Cover Letter Generator
* Deployment on Render/Railway

## Author

Sneha Jain

Final Year AIML Student

Built using Flask, Gemini AI and modern web technologies.
