-- Initial database setup script
-- This script runs when the PostgreSQL container starts for the first time

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Ensure the user has proper permissions
GRANT ALL PRIVILEGES ON DATABASE class_connect_db TO class_connect_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO class_connect_user;

-- Database is ready for migrations
