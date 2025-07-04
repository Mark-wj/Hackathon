-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50) DEFAULT 'job_seeker',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User profiles table
CREATE TABLE user_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    phone VARCHAR(20),
    location VARCHAR(255),
    summary TEXT,
    skills TEXT[],
    experience_years INTEGER,
    education JSONB,
    work_experience JSONB,
    resume_file_path VARCHAR(500),
    linkedin_url VARCHAR(255),
    github_url VARCHAR(255),
    portfolio_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Companies table
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    industry VARCHAR(100),
    size VARCHAR(50),
    location VARCHAR(255),
    website VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Jobs table
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    posted_by INTEGER REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    requirements TEXT,
    skills_required TEXT[],
    experience_level VARCHAR(50),
    job_type VARCHAR(50),
    location VARCHAR(255),
    salary_min INTEGER,
    salary_max INTEGER,
    is_remote BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    posted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

-- Applications table
CREATE TABLE applications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    job_id INTEGER REFERENCES jobs(id),
    cover_letter TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    match_score FLOAT,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, job_id)
);

-- Match history table
CREATE TABLE match_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    job_id INTEGER REFERENCES jobs(id),
    match_score FLOAT,
    skill_match_score FLOAT,
    experience_match_score FLOAT,
    location_match_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_jobs_active ON jobs(is_active);
CREATE INDEX idx_applications_user ON applications(user_id);
CREATE INDEX idx_applications_job ON applications(job_id);
CREATE INDEX idx_match_history_user ON match_history(user_id);
