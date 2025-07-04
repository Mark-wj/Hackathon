import requests
import json

BASE_URL = "http://localhost:5000/api"

# Test users to create
users = [
    {
        "email": "admin@example.com",
        "password": "admin123",
        "first_name": "Admin",
        "last_name": "User",
        "role": "admin"
    },
    {
        "email": "employer@example.com",
        "password": "employer123",
        "first_name": "Employer",
        "last_name": "User",
        "role": "employer"
    },
    {
        "email": "jobseeker@example.com",
        "password": "seeker123",
        "first_name": "Job",
        "last_name": "Seeker",
        "role": "job_seeker"
    }
]

for user_data in users:
    # Register user
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    
    if response.status_code == 201:
        print(f"✓ Created {user_data['role']}: {user_data['email']}")
        
        # For admin user, we need to manually update the role in the database
        # since registration defaults to job_seeker
        if user_data['role'] == 'admin':
            print("  Note: You need to manually update this user to admin role in the database")
            print("  Run: UPDATE users SET role = 'admin' WHERE email = 'admin@example.com';")
    else:
        print(f"✗ Failed to create {user_data['email']}: {response.json()}")

print("\nTo make the admin user, run this SQL command:")
print("psql -h localhost -U jobmatch_user -d job_matching_db -c \"UPDATE users SET role = 'admin' WHERE email = 'admin@example.com';\"")
print("\nTo make the employer user, run this SQL command:")
print("psql -h localhost -U jobmatch_user -d job_matching_db -c \"UPDATE users SET role = 'employer' WHERE email = 'employer@example.com';\"")
