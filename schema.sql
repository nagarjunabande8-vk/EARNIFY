CREATE DATABASE IF NOT EXISTS earnify;
USE earnify;

CREATE TABLE IF NOT EXISTS users (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    email         VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role          ENUM('client', 'freelancer') NOT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS jobs (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    client_id        INT NOT NULL,
    title            VARCHAR(200) NOT NULL,
    description      TEXT NOT NULL,
    budget           DECIMAL(10, 2) NOT NULL,
    category         VARCHAR(100),
    skills_required  VARCHAR(255),
    deadline         DATE NULL,
    status           ENUM('open', 'closed') DEFAULT 'open',
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS applications (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    job_id          INT NOT NULL,
    freelancer_id   INT NOT NULL,
    cover_letter    TEXT,
    proposed_rate   DECIMAL(10, 2),
    status          ENUM('pending', 'accepted', 'rejected') DEFAULT 'pending',
    applied_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    FOREIGN KEY (freelancer_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_application (job_id, freelancer_id)
);

CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_category ON jobs(category);
CREATE INDEX idx_applications_job ON applications(job_id);
