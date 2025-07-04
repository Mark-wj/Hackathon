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

# Get user profile to see their skills
profile_response = requests.get(f"{BASE_URL}/users/profile", headers=headers)
user_profile = profile_response.json()

print("Your profile:")
print(f"Skills: {user_profile.get('profile', {}).get('skills', [])}")
print(f"Location: {user_profile.get('profile', {}).get('location', '')}")
print(f"Experience Years: {user_profile.get('profile', {}).get('experience_years', 0)}")

# Create jobs that match the user's skills
user_skills = user_profile.get('profile', {}).get('skills', [])
user_location = user_profile.get('profile', {}).get('location', 'Nairobi, Kenya')

# Create some matching jobs
matching_jobs = [
    {
        "title": "Full Stack Developer",
        "company_name": "Tech Solutions Kenya",
        "description": "Looking for a developer with your exact skill set!",
        "requirements": "Experience with modern web technologies",
        "skills_required": user_skills[:3] if user_skills else ["python", "flask"],  # Use user's top 3 skills
        "experience_level": "mid",
        "job_type": "full_time",
        "location": user_location,
        "salary_min": 60000,
        "salary_max": 100000,
        "is_remote": True
    },
    {
        "title": "Backend Developer",
        "company_name": "Innovation Hub",
        "description": "Join our team to build scalable applications",
        "requirements": "Strong backend development skills",
        "skills_required": user_skills[:2] if user_skills else ["python"],  # Use user's top 2 skills
        "experience_level": "mid",
        "job_type": "full_time",
        "location": user_location,
        "salary_min": 70000,
        "salary_max": 120000,
        "is_remote": False
    }
]

# Add jobs
for job in matching_jobs:
    response = requests.post(f"{BASE_URL}/jobs/", json=job, headers=headers)
    if response.status_code == 201:
        print(f"Created job: {job['title']}")
    else:
        print(f"Failed to create job: {job['title']}")
        print(response.json())

print("\nNow try finding matches again!")
