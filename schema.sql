-- Create a new database if it doesn't exist
CREATE DATABASE IF NOT EXISTS simple_db;

-- Create a dedicated user for the MCP server (avoiding root)
-- % allows connection from any host (needed for Lima -> Host port forwarding scenarios or Docker networks)
-- In production, you might restrict this to specific IPs.
CREATE USER IF NOT EXISTS 'mcp_user'@'%' IDENTIFIED BY 'mcp_password';

-- Grant privileges only on the specific database
GRANT ALL PRIVILEGES ON simple_db.* TO 'mcp_user'@'%';

-- Apply privilege changes
FLUSH PRIVILEGES;

-- Switch to the database
USE simple_db;

-- Create the tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert some sample data
INSERT INTO tasks (title, status) VALUES 
('Buy groceries', 'pending'),
('Walk the dog', 'completed'),
('Finish MCP project', 'in_progress');

-- Create student table
CREATE TABLE IF NOT EXISTS student (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone_number VARCHAR(50)
);

-- Insert sample students
INSERT INTO student (name, email, phone_number) VALUES 
('Alice Johnson', 'alice@example.com', '123-456-7890'),
('Bob Smith', 'bob@example.com', '987-654-3210'),
('Charlie Brown', 'charlie@example.com', '555-666-7777');
