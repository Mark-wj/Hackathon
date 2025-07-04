import requests
import json

# Base URL
BASE_URL = "http://localhost:5000/api"

# Login
login_data = {
    "email": "testuser@example.com",
    "password": "password123"
}

response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
if response.status_code != 200:
    print("Failed to login")
    exit(1)

token = response.json()["access_token"]
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Jobs that match your skills
jobs = [
    {
        "title": "Full Stack Developer - React & Python",
        "company_name": "Tech Innovators Kenya",
        "description": "We need a full stack developer proficient in React and Python to build modern web applications.",
        "requirements": "3+ years experience with React and Python backends",
        "skills_required": ["javascript", "react", "python", "django", "postgresql"],
        "experience_level": "mid",
        "job_type": "full_time",
        "location": "Nairobi, Kenya",
        "salary_min": 80000,
        "salary_max": 150000,
        "is_remote": True
    },
    {
        "title": "Frontend Developer - React/Tailwind",
        "company_name": "Digital Solutions Ltd",
        "description": "Join our team to create beautiful UIs with React and Tailwind CSS.",
        "requirements": "Strong skills in React and modern CSS frameworks",
        "skills_required": ["javascript", "react", "tailwind css"],
        "experience_level": "mid",
        "job_type": "full_time",
        "location": "Nairobi, Kenya",
        "salary_min": 70000,
        "salary_max": 120000,
        "is_remote": False
    },
    {
        "title": "Python Backend Developer",
        "company_name": "DataTech Africa",
        "description": "Looking for a Python developer experienced with Flask and Django frameworks.",
        "requirements": "Experience with Python web frameworks and PostgreSQL",
        "skills_required": ["python", "flask", "django", "postgresql"],
        "experience_level": "senior",
        "job_type": "full_time",
        "location": "Nairobi, Kenya",
        "salary_min": 90000,
        "salary_max": 160000,
        "is_remote": True
    },
    {
        "title": "Junior Full Stack Developer",
        "company_name": "StartupHub Nairobi",
        "description": "Great opportunity for a developer with React and Python skills.",
        "requirements": "Basic knowledge of React and Python",
        "skills_required": ["javascript", "react", "python"],
        "experience_level": "entry",
        "job_type": "full_time",
        "location": "Nairobi, Kenya",
        "salary_min": 40000,
        "salary_max": 70000,
        "is_remote": False
    },
    {
        "title": "React Developer with Python Knowledge",
        "company_name": "WebCraft Kenya",
        "description": "Build responsive web applications using React, with occasional Python backend work.",
        "requirements": "Strong React skills, basic Python knowledge",
        "skills_required": ["javascript", "react", "tailwind css", "python"],
        "experience_level": "mid",
        "job_type": "full_time",
        "location": "Nairobi, Kenya",
        "salary_min": 75000,
        "salary_max": 130000,
        "is_remote": True
    }
]

# Add all jobs
for job in jobs:
    response = requests.post(f"{BASE_URL}/jobs/", json=job, headers=headers)
    if response.status_code == 201:
        print(f"✓ Created job: {job['title']}")
    else:
        print(f"✗ Failed to create job: {job['title']}")
        print(f"  Error: {response.json()}")

print("\n✅ Jobs created successfully!")
print("Now go back to the web interface and click 'Find My Best Matches' - you should see great matches!")
