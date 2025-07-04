import requests

# Check jobs without authentication
response = requests.get("http://localhost:5000/api/jobs/search")
data = response.json()

print(f"Total jobs in database: {data['total']}")
print(f"Jobs returned: {len(data['jobs'])}")

if data['jobs']:
    print("\nFirst few jobs:")
    for i, job in enumerate(data['jobs'][:3]):
        print(f"\nJob {i+1}: {job['title']}")
        print(f"Skills required: {job['skills_required']}")
        print(f"Location: {job['location']}")
