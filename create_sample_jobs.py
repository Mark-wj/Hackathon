import requests
import json

# Base URL
BASE_URL = "http://localhost:5000/api"

# First, login to get token
login_data = {
    "email": "testuser@example.com",
    "password": "password123"
}

response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
token = response.json()["access_token"]

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Sample jobs data
jobs = [
    {
        "title": "Senior Python Developer",
        "company_name": "TechCorp Kenya",
        "description": "We are looking for an experienced Python developer to join our team.",
        "requirements": "5+ years of Python experience, knowledge of Flask/Django",
        "skills_required": ["python", "flask", "django", "postgresql", "docker"],
        "experience_level": "senior",
        "job_type": "full_time",
        "location": "Nairobi, Kenya",
        "salary_min": 80000,
        "salary_max": 150000,
        "is_remote": True
    },
    {
        "title": "Junior Web Developer",
        "company_name": "StartupHub",
        "description": "Great opportunity for a junior developer to grow with our startup.",
        "requirements": "Basic knowledge of web development, eager to learn",
        "skills_required": ["html", "css", "javascript", "react"],
        "experience_level": "entry",
        "job_type": "full_time",
        "location": "Nairobi, Kenya",
        "salary_min": 30000,
        "salary_max": 50000,
        "is_remote": False
    },
    {
        "title": "Data Scientist",
        "company_name": "DataTech Solutions",
        "description": "Join our data science team to work on exciting ML projects.",
        "requirements": "Experience with machine learning and data analysis",
        "skills_required": ["python", "machine learning", "data science", "sql"],
        "experience_level": "mid",
        "job_type": "full_time",
        "location": "Nairobi, Kenya",
        "salary_min": 70000,
        "salary_max": 120000,
        "is_remote": True
    },
    {
        "title": "DevOps Engineer",
        "company_name": "CloudTech Africa",
        "description": "Looking for a DevOps engineer to manage our cloud infrastructure.",
        "requirements": "Experience with AWS, Docker, and Kubernetes",
        "skills_required": ["aws", "docker", "kubernetes", "python", "git"],
        "experience_level": "mid",
        "job_type": "full_time",
        "location": "Nairobi, Kenya",
        "salary_min": 75000,
        "salary_max": 130000,
        "is_remote": True
    }
]

# Create jobs
for job in jobs:
    response = requests.post(f"{BASE_URL}/jobs/", json=job, headers=headers)
    if response.status_code == 201:
        print(f"Created job: {job['title']}")
    else:
        print(f"Failed to create job: {job['title']}")
        print(response.json())

print("\nAll sample jobs created!")
