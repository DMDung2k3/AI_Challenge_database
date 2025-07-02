-- init-db.sql
-- Khởi tạo database cho AI Challenge

-- Tạo extensions cần thiết
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Tạo schema chính
CREATE SCHEMA IF NOT EXISTS ai_challenge;

-- Bảng users
CREATE TABLE IF NOT EXISTS ai_challenge.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Bảng sessions
CREATE TABLE IF NOT EXISTS ai_challenge.sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES ai_challenge.users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Bảng videos metadata
CREATE TABLE IF NOT EXISTS ai_challenge.videos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename VARCHAR(255) NOT NULL,
    original_path TEXT,
    file_size BIGINT,
    duration FLOAT,
    fps FLOAT,
    resolution VARCHAR(20),
    format VARCHAR(10),
    uploaded_by UUID REFERENCES ai_challenge.users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending'
);

-- Bảng keyframes
CREATE TABLE IF NOT EXISTS ai_challenge.keyframes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_id UUID REFERENCES ai_challenge.videos(id) ON DELETE CASCADE,
    frame_number INTEGER NOT NULL,
    timestamp_seconds FLOAT NOT NULL,
    image_path TEXT NOT NULL,
    features JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes để tối ưu hiệu suất
CREATE INDEX IF NOT EXISTS idx_videos_status ON ai_challenge.videos(status);
CREATE INDEX IF NOT EXISTS idx_videos_created_at ON ai_challenge.videos(created_at);
CREATE INDEX IF NOT EXISTS idx_keyframes_video_id ON ai_challenge.keyframes(video_id);
CREATE INDEX IF NOT EXISTS idx_keyframes_timestamp ON ai_challenge.keyframes(timestamp_seconds);
CREATE INDEX IF NOT EXISTS idx_sessions_token ON ai_challenge.sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_sessions_expires ON ai_challenge.sessions(expires_at);

-- Insert dữ liệu test
INSERT INTO ai_challenge.users (username, email, password_hash) 
VALUES ('admin', 'admin@example.com', crypt('admin123', gen_salt('bf')))
ON CONFLICT (username) DO NOTHING;

-- Thông báo hoàn thành
SELECT 'Database initialized successfully!' as message;