-- Add email verification fields to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verification_token VARCHAR(255);

-- Add notification preferences to user_profiles
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS whatsapp_notifications BOOLEAN DEFAULT TRUE;
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS sms_notifications BOOLEAN DEFAULT TRUE;
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS email_notifications BOOLEAN DEFAULT TRUE;

-- Add document storage fields to applications
ALTER TABLE applications ADD COLUMN IF NOT EXISTS cv_document_path VARCHAR(500);
ALTER TABLE applications ADD COLUMN IF NOT EXISTS cover_letter_document_path VARCHAR(500);
ALTER TABLE applications ADD COLUMN IF NOT EXISTS offer_letter_path VARCHAR(500);

-- Create offer_documents table for custom uploads
CREATE TABLE IF NOT EXISTS offer_documents (
    id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES applications(id),
    document_type VARCHAR(50), -- 'offer_letter', 'contract', etc.
    file_path VARCHAR(500),
    uploaded_by INTEGER REFERENCES users(id),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
