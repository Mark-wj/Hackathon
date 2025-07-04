import requests
import json
import sys

BASE_URL = "http://localhost:5000/api"

# Get token from command line or use default
email = sys.argv[1] if len(sys.argv) > 1 else "testuser@example.com"
password = sys.argv[2] if len(sys.argv) > 2 else "password123"

print(f"Logging in as: {email}")

# Login
login_response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": email,
    "password": password
})

if login_response.status_code != 200:
    print(f"Login failed: {login_response.text}")
    exit(1)

token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get profile
print("\n=== CHECKING PROFILE ===")
profile_response = requests.get(f"{BASE_URL}/users/profile", headers=headers)
profile = profile_response.json()

print(f"Profile response status: {profile_response.status_code}")
print(f"Has profile object: {'profile' in profile}")
if 'profile' in profile:
    print(f"Profile skills: {profile['profile'].get('skills', 'NO SKILLS')}")
    print(f"Profile location: {profile['profile'].get('location', 'NO LOCATION')}")
    print(f"Experience years: {profile['profile'].get('experience_years', 'NO EXPERIENCE')}")
    print(f"Profile fields: {list(profile['profile'].keys())}")

# Check jobs
print("\n=== CHECKING JOBS ===")
jobs_response = requests.get(f"{BASE_URL}/jobs/search")
jobs = jobs_response.json()
print(f"Total jobs in database: {jobs.get('total', 0)}")

# Try matching with detailed error handling
print("\n=== TESTING MATCH ENDPOINT ===")
match_response = requests.post(
    f"{BASE_URL}/ai/match-jobs",
    headers={**headers, "Content-Type": "application/json"},
    json={"min_match_score": 0}
)

print(f"Match endpoint status: {match_response.status_code}")
print(f"Match response: {match_response.text}")

if match_response.status_code == 200:
    matches = match_response.json()
    print(f"Matches found: {matches.get('total_matches', 0)}")
    if matches.get('matches'):
        print("\nFirst match:")
        print(json.dumps(matches['matches'][0], indent=2))
