-- Drop existing tables if they exist
DROP TABLE IF EXISTS audit_log;
DROP TABLE IF EXISTS votes;
DROP TABLE IF EXISTS candidates;
DROP TABLE IF EXISTS users;

-- Create fresh tables with new schema
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    province VARCHAR(50) NOT NULL,
    district VARCHAR(50) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP
);

-- Rest of your tables remain the same...
CREATE TABLE candidates (
    candidate_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    province VARCHAR(50) NOT NULL,
    district VARCHAR(50) NOT NULL,
    party VARCHAR(50)
);

CREATE TABLE votes (
    vote_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    candidate_id INTEGER REFERENCES candidates(candidate_id),
    preference INTEGER CHECK (preference IN (1, 2, 3)),
    vote_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE audit_log (
    log_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    action VARCHAR(50) NOT NULL,
    description TEXT,
    action_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);