-- Initial database setup script
-- This script runs when the PostgreSQL container starts for the first time

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Ensure the user has proper permissions
GRANT ALL PRIVILEGES ON DATABASE qr_survey_db TO qr_survey_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO qr_survey_user;

-- Database is ready for migrations
