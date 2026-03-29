CREATE DATABASE student_tracker;
USE student_tracker;
CREATE TABLE subjects (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100),
  is_major BOOLEAN DEFAULT FALSE
);

CREATE TABLE study_logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  subject_id INT,
  date DATE,
  hours FLOAT,
  completed BOOLEAN,
  notes TEXT,
  FOREIGN KEY (subject_id) REFERENCES subjects(id)
);

CREATE TABLE streaks (
  subject_id INT PRIMARY KEY,
  current_streak INT DEFAULT 0,
  longest_streak INT DEFAULT 0,
  last_updated DATE,
  FOREIGN KEY (subject_id) REFERENCES subjects(id)
);

CREATE TABLE goals (
  id INT AUTO_INCREMENT PRIMARY KEY,
  subject_id INT,
  type VARCHAR(20),
  target_hours FLOAT,
  reward TEXT,
  punishment TEXT,
  FOREIGN KEY (subject_id) REFERENCES subjects(id)
);