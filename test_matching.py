import requests
import json

BASE_URL = "http://localhost:5000/api"

# Login
login_response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "testuser@example.com",
    "password": "password123"
})

if login_response.status_code != 200:
    print("Login failed")
    exit(1)

token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get profile
profile = requests.get(f"{BASE_URL}/users/profile", headers=headers).json()
print("Profile completed:", profile.get('profile') is not None)
print("Has skills:", bool(profile.get('profile', {}).get('skills')))

# Get all jobs
jobs = requests.get(f"{BASE_URL}/jobs/search").json()
print(f"Total jobs available: {jobs['total']}")

# Try to get matches with min score 0
matches_response = requests.post(
    f"{BASE_URL}/ai/match-jobs",
    headers={**headers, "Content-Type": "application/json"},
    json={"min_match_score": 0}
)

print(f"Match API response status: {matches_response.status_code}")
if matches_response.status_code == 200:
    matches_data = matches_response.json()
    print(f"Matches found: {matches_data.get('total_matches', 0)}")
else:
    print(f"Error: {matches_response.json()}")
