-- Initialize database tables for EcoLearn AI

-- Users table for local authentication (email/password only)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    avatar_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Learning paths table
CREATE TABLE IF NOT EXISTS learning_paths (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    topic VARCHAR(255) NOT NULL,
    difficulty VARCHAR(50) DEFAULT 'beginner',
    content TEXT,
    progress INTEGER DEFAULT 0,
    total_sessions INTEGER DEFAULT 0,
    completed_sessions INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Carbon metrics table
CREATE TABLE IF NOT EXISTS carbon_metrics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    learning_path_id INTEGER REFERENCES learning_paths(id) ON DELETE SET NULL,
    session_duration INTEGER NOT NULL,
    carbon_footprint FLOAT NOT NULL,
    device_type VARCHAR(50) DEFAULT 'laptop',
    energy_consumed FLOAT,
    trees_contribution FLOAT,
    session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tree plantations table
CREATE TABLE IF NOT EXISTS tree_plantations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    trees_planted INTEGER NOT NULL,
    carbon_offset FLOAT NOT NULL,
    location VARCHAR(255),
    tree_species VARCHAR(255),
    plantation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    certificate_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User stats table
CREATE TABLE IF NOT EXISTS user_stats (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    total_learning_time INTEGER DEFAULT 0,
    total_carbon_footprint FLOAT DEFAULT 0,
    total_trees_planted INTEGER DEFAULT 0,
    total_carbon_offset FLOAT DEFAULT 0,
    paths_completed INTEGER DEFAULT 0,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    experience_points INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_learning_paths_user_id ON learning_paths(user_id);
CREATE INDEX IF NOT EXISTS idx_carbon_metrics_user_id ON carbon_metrics(user_id);
CREATE INDEX IF NOT EXISTS idx_tree_plantations_user_id ON tree_plantations(user_id);
CREATE INDEX IF NOT EXISTS idx_user_stats_user_id ON user_stats(user_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);