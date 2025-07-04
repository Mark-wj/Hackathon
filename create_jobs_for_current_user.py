import requests
import json

# Base URL
BASE_URL = "http://localhost:5000/api"

# Login with YOUR account
email = input("Enter your email (or press Enter for marknjenga25@gmail.com): ").strip()
if not email:
    email = "marknjenga25@gmail.com"

password = input("Enter your password: ").strip()

login_data = {
    "email": email,
    "password": password
}

response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
if response.status_code != 200:
    print(f"Failed to login: {response.json()}")
    exit(1)

token = response.json()["access_token"]
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

print(f"\nLogged in as: {email}")

# Jobs that match the skills shown in debug output
# Using lowercase to ensure matching works
jobs = [
    {
        "title": "Full Stack Developer - React & Python",
        "company_name": "Tech Innovators Kenya",
        "description": "We need a full stack developer proficient in React and Python to build modern web applications.",
        "requirements": "3+ years experience with React and Python backends",
        "skills_required": ["javascript", "react", "python", "django", "postgresql"],
        "experience_level": "mid",
        "job_type": "full_time",
        "location": "Nakuru, Kenya",  # Matching your location
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
        "location": "Nairobi, Kenya",  # Different location but remote
        "salary_min": 70000,
        "salary_max": 120000,
        "is_remote": True
    },
    {
        "title": "Python Backend Developer",
        "company_name": "DataTech Africa",
        "description": "Looking for a Python developer experienced with Flask and Django frameworks.",
        "requirements": "Experience with Python web frameworks and PostgreSQL",
        "skills_required": ["python", "flask", "django", "postgresql"],
        "experience_level": "senior",
        "job_type": "full_time",
        "location": "Nakuru, Kenya",
        "salary_min": 90000,
        "salary_max": 160000,
        "is_remote": False
    },
    {
        "title": "React Native Developer",
        "company_name": "MobileTech Kenya",
        "description": "Build mobile apps with React Native and JavaScript.",
        "requirements": "Experience with React and mobile development",
        "skills_required": ["javascript", "react"],
        "experience_level": "mid",
        "job_type": "full_time",
        "location": "Nakuru, Kenya",
        "salary_min": 75000,
        "salary_max": 130000,
        "is_remote": True
    },
    {
        "title": "Django Web Developer",
        "company_name": "WebCraft Solutions",
        "description": "Create robust web applications using Django and PostgreSQL.",
        "requirements": "Strong Django and database skills",
        "skills_required": ["python", "django", "postgresql"],
        "experience_level": "mid",
        "job_type": "full_time",
        "location": "Nakuru, Kenya",
        "salary_min": 85000,
        "salary_max": 140000,
        "is_remote": False
    }
]

# Add all jobs
success_count = 0
for job in jobs:
    response = requests.post(f"{BASE_URL}/jobs/", json=job, headers=headers)
    if response.status_code == 201:
        print(f"✓ Created job: {job['title']}")
        success_count += 1
    else:
        print(f"✗ Failed to create job: {job['title']}")
        print(f"  Error: {response.json()}")

print(f"\n✅ Successfully created {success_count} jobs!")
print("\nNow go back to the web interface and click 'Find My Best Matches' - you should see matches!")
