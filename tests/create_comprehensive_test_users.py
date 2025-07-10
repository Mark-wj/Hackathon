#!/usr/bin/env python3
"""
Comprehensive Role Testing Script for Job Matching Platform
==========================================================

This script creates test users for different roles and provides testing scenarios
for your hackathon job matching application.

Roles to test:
- job_seeker (default)
- employer  
- admin

Usage:
1. Run this script to create test users
2. Use the provided test scenarios to validate role functionality
3. Check role-based access controls
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.user import User, UserProfile
from app.models.job import Company, Job
from datetime import datetime

def create_test_users():
    """Create test users for each role"""
    
    app = create_app()
    
    with app.app_context():
        # Clear existing test users (optional)
        print("🧹 Cleaning up existing test users...")
        User.query.filter(User.email.like('%test%')).delete()
        db.session.commit()
        
        test_users = []
        
        # 1. JOB SEEKER TEST USERS
        print("\n👤 Creating Job Seeker Test Users...")
        
        job_seekers = [
            {
                'email': 'jobseeker1@test.com',
                'password': 'password123',
                'first_name': 'Alice',
                'last_name': 'Johnson',
                'role': 'job_seeker',
                'profile': {
                    'phone': '+1234567890',
                    'location': 'New York, NY',
                    'summary': 'Experienced software developer looking for new opportunities',
                    'skills': ['Python', 'JavaScript', 'React', 'Node.js'],
                    'experience_years': 3,
                    'education': [
                        {
                            'degree': 'Bachelor of Computer Science',
                            'institution': 'Tech University',
                            'year': 2020
                        }
                    ],
                    'work_experience': [
                        {
                            'company': 'StartupXYZ',
                            'position': 'Junior Developer',
                            'duration': '2020-2023',
                            'description': 'Developed web applications using React and Node.js'
                        }
                    ]
                }
            },
            {
                'email': 'jobseeker2@test.com',
                'password': 'password123',
                'first_name': 'Bob',
                'last_name': 'Smith',
                'role': 'job_seeker',
                'profile': {
                    'phone': '+1234567891',
                    'location': 'San Francisco, CA',
                    'summary': 'Data scientist with machine learning expertise',
                    'skills': ['Python', 'Machine Learning', 'SQL', 'TensorFlow'],
                    'experience_years': 5,
                    'education': [
                        {
                            'degree': 'Master of Data Science',
                            'institution': 'Data Institute',
                            'year': 2018
                        }
                    ]
                }
            }
        ]
        
        for user_data in job_seekers:
            user = User(
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                role=user_data['role']
            )
            user.set_password(user_data['password'])
            db.session.add(user)
            db.session.flush()  # Get the user ID
            
            # Create profile
            profile = UserProfile(
                user_id=user.id,
                **user_data['profile']
            )
            db.session.add(profile)
            test_users.append(user)
            print(f"✅ Created job seeker: {user.email}")
        
        # 2. EMPLOYER TEST USERS
        print("\n🏢 Creating Employer Test Users...")
        
        employers = [
            {
                'email': 'employer1@test.com',
                'password': 'password123',
                'first_name': 'Carol',
                'last_name': 'Davis',
                'role': 'employer',
                'profile': {
                    'phone': '+1234567892',
                    'location': 'Austin, TX',
                    'summary': 'HR Manager at TechCorp, recruiting top talent'
                }
            },
            {
                'email': 'employer2@test.com',
                'password': 'password123',
                'first_name': 'David',
                'last_name': 'Wilson',
                'role': 'employer',
                'profile': {
                    'phone': '+1234567893',
                    'location': 'Seattle, WA',
                    'summary': 'Startup founder looking for early employees'
                }
            }
        ]
        
        for user_data in employers:
            user = User(
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                role=user_data['role']
            )
            user.set_password(user_data['password'])
            db.session.add(user)
            db.session.flush()
            
            # Create profile
            profile = UserProfile(
                user_id=user.id,
                **user_data['profile']
            )
            db.session.add(profile)
            test_users.append(user)
            print(f"✅ Created employer: {user.email}")
        
        # 3. ADMIN TEST USERS
        print("\n🔧 Creating Admin Test Users...")
        
        admins = [
            {
                'email': 'admin@test.com',
                'password': 'admin123',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'admin',
                'profile': {
                    'phone': '+1234567894',
                    'location': 'Remote',
                    'summary': 'Platform administrator'
                }
            }
        ]
        
        for user_data in admins:
            user = User(
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                role=user_data['role']
            )
            user.set_password(user_data['password'])
            db.session.add(user)
            db.session.flush()
            
            # Create profile
            profile = UserProfile(
                user_id=user.id,
                **user_data['profile']
            )
            db.session.add(profile)
            test_users.append(user)
            print(f"✅ Created admin: {user.email}")
        
        # Commit all changes
        db.session.commit()
        
        print(f"\n🎉 Successfully created {len(test_users)} test users!")
        return test_users

def print_test_credentials():
    """Print test user credentials for easy reference"""
    
    print("\n" + "="*60)
    print("🔑 TEST USER CREDENTIALS")
    print("="*60)
    
    print("\n👤 JOB SEEKERS:")
    print("• jobseeker1@test.com / password123 (Alice Johnson)")
    print("• jobseeker2@test.com / password123 (Bob Smith)")
    
    print("\n🏢 EMPLOYERS:")
    print("• employer1@test.com / password123 (Carol Davis)")
    print("• employer2@test.com / password123 (David Wilson)")
    
    print("\n🔧 ADMIN:")
    print("• admin@test.com / admin123 (Admin User)")
    
    print("\n" + "="*60)

def role_test_scenarios():
    """Print comprehensive test scenarios for each role"""
    
    print("\n" + "="*60)
    print("🧪 ROLE TESTING SCENARIOS")
    print("="*60)
    
    print("\n1️⃣ JOB SEEKER ROLE TESTING")
    print("-" * 40)
    print("✅ SHOULD BE ABLE TO:")
    print("• Register and login")
    print("• View and edit profile")
    print("• Upload resume")
    print("• Search and browse jobs")
    print("• Apply to jobs")
    print("• View application history")
    print("• Receive job recommendations")
    print("• Update skills and experience")
    
    print("\n❌ SHOULD NOT BE ABLE TO:")
    print("• Post jobs")
    print("• View other users' applications")
    print("• Access employer dashboard")
    print("• Access admin panel")
    print("• Manage job postings")
    
    print("\n2️⃣ EMPLOYER ROLE TESTING")
    print("-" * 40)
    print("✅ SHOULD BE ABLE TO:")
    print("• Register and login")
    print("• Create company profile")
    print("• Post job listings")
    print("• Edit/delete own job postings")
    print("• View applications for their jobs")
    print("• Search candidate profiles")
    print("• Manage application status")
    print("• View hiring analytics")
    
    print("\n❌ SHOULD NOT BE ABLE TO:")
    print("• Apply to jobs")
    print("• View other employers' job applications")
    print("• Access admin panel")
    print("• Manage other users' accounts")
    print("• Delete jobs posted by others")
    
    print("\n3️⃣ ADMIN ROLE TESTING")
    print("-" * 40)
    print("✅ SHOULD BE ABLE TO:")
    print("• Access admin dashboard")
    print("• Manage all users")
    print("• View all job postings")
    print("• Moderate content")
    print("• View system analytics")
    print("• Manage platform settings")
    print("• Handle user reports")
    print("• Access all application data")
    
    print("\n❌ SHOULD NOT BE ABLE TO:")
    print("• Apply to jobs (unless also job_seeker)")
    print("• Post jobs (unless also employer)")
    
    print("\n4️⃣ SECURITY TESTING")
    print("-" * 40)
    print("🔒 ACCESS CONTROL TESTS:")
    print("• Try accessing admin routes as job_seeker")
    print("• Try accessing employer routes as job_seeker")
    print("• Try viewing other users' private data")
    print("• Test JWT token expiration")
    print("• Test password security")
    print("• Test role escalation attempts")
    
    print("\n5️⃣ INTEGRATION TESTING")
    print("-" * 40)
    print("🔄 WORKFLOW TESTS:")
    print("• Complete job posting to application flow")
    print("• Test AI matching algorithms")
    print("• Test notification system")
    print("• Test resume upload and parsing")
    print("• Test search and filtering")
    
    print("\n" + "="*60)

def run_basic_role_tests():
    """Run basic automated tests for role functionality"""
    
    app = create_app()
    
    with app.app_context():
        print("\n🤖 RUNNING BASIC ROLE TESTS...")
        
        # Test 1: Check if users exist
        job_seeker = User.query.filter_by(email='jobseeker1@test.com').first()
        employer = User.query.filter_by(email='employer1@test.com').first()
        admin = User.query.filter_by(email='admin@test.com').first()
        
        print("\n📊 USER VERIFICATION:")
        print(f"• Job Seeker exists: {'✅' if job_seeker else '❌'}")
        print(f"• Employer exists: {'✅' if employer else '❌'}")
        print(f"• Admin exists: {'✅' if admin else '❌'}")
        
        if job_seeker:
            print(f"• Job Seeker role: {job_seeker.role}")
            print(f"• Job Seeker profile: {'✅' if job_seeker.profile else '❌'}")
        
        if employer:
            print(f"• Employer role: {employer.role}")
            print(f"• Employer profile: {'✅' if employer.profile else '❌'}")
        
        if admin:
            print(f"• Admin role: {admin.role}")
            print(f"• Admin profile: {'✅' if admin.profile else '❌'}")
        
        # Test 2: Password verification
        print("\n🔐 PASSWORD VERIFICATION:")
        if job_seeker:
            print(f"• Job Seeker password: {'✅' if job_seeker.check_password('password123') else '❌'}")
        if employer:
            print(f"• Employer password: {'✅' if employer.check_password('password123') else '❌'}")
        if admin:
            print(f"• Admin password: {'✅' if admin.check_password('admin123') else '❌'}")

if __name__ == '__main__':
    print("🚀 STARTING ROLE TESTING SETUP...")
    
    # Create test users
    create_test_users()
    
    # Print credentials
    print_test_credentials()
    
    # Print test scenarios
    role_test_scenarios()
    
    # Run basic tests
    run_basic_role_tests()
    
    print("\n✨ ROLE TESTING SETUP COMPLETE!")
    print("You can now start testing your application with different roles.")