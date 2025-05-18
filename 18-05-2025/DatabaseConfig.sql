create database E_TBS;

-- data that i need READY from TBS
CREATE TABLE `E_TBS`.`students` (
  `student_id` VARCHAR(15) NOT NULL,
  `national_id` VARCHAR(8) NOT NULL,
  `first_name` VARCHAR(45) NOT NULL,
  `last_name` VARCHAR(45) NOT NULL,
  `email` VARCHAR(100) NULL,
  `phone_number` VARCHAR(8) NULL,
  `date_of_birth` DATE NULL,
  `student_level` ENUM('Freshman', 'Sophomore', 'Junior', 'Senior') NULL,
  `major` VARCHAR(45) NULL,
  `minor` VARCHAR(45) NULL,
  `student_status` ENUM('Active', 'Graduated', 'Suspended') NULL,
  PRIMARY KEY (`student_id`),
  UNIQUE INDEX `national_id_UNIQUE` (`national_id` ASC) VISIBLE,
  UNIQUE INDEX `email_UNIQUE` (`email` ASC) VISIBLE
);

CREATE TABLE `E_TBS`.`professors` (
  `professor_id` VARCHAR(15) NOT NULL,
  `national_id` VARCHAR(8) NOT NULL,
  `first_name` VARCHAR(45) NOT NULL,
  `last_name` VARCHAR(45) NOT NULL,
  `email` VARCHAR(100) NULL,
  `phone_number` VARCHAR(8) NULL,
  `date_of_birth` DATE NULL,
  `department` VARCHAR(45) NULL,
  `office_location` VARCHAR(45) NULL,
  PRIMARY KEY (`professor_id`),
  UNIQUE INDEX `national_id_UNIQUE` (`national_id` ASC) VISIBLE,
  UNIQUE INDEX `email_UNIQUE` (`email` ASC) VISIBLE
);

CREATE TABLE `E_TBS`.`courses` (
  `course_code` VARCHAR(10) NOT NULL,
  `course_name` VARCHAR(100) NOT NULL,
  `semester` ENUM('Fall', 'Spring') NOT NULL,
  `level` ENUM('Freshman', 'Sophomore', 'Junior', 'Senior') NOT NULL,
  `credits` INT NOT NULL,
  `has_tutorial` BOOLEAN NOT NULL DEFAULT FALSE,
  PRIMARY KEY (`course_code`)
);

CREATE TABLE `E_TBS`.`student_courses` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `student_id` VARCHAR(10) NOT NULL,
  `course_code` VARCHAR(10) NOT NULL,
  `group_id` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `student_idx` (`student_id` ASC),
  INDEX `course_idx` (`course_code` ASC),
  CONSTRAINT `fk_student`
    FOREIGN KEY (`student_id`)
    REFERENCES `E_TBS`.`students` (`student_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_course`
    FOREIGN KEY (`course_code`)
    REFERENCES `E_TBS`.`courses` (`course_code`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE `E_TBS`.`course_professors` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `course_code` VARCHAR(10) NOT NULL,
  `professor_id` VARCHAR(15) NOT NULL,
  `session_type` ENUM('Lecture', 'Tutorial') NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `course_idx` (`course_code` ASC),
  INDEX `professor_idx` (`professor_id` ASC),
  CONSTRAINT `fk_course_prof`
    FOREIGN KEY (`course_code`)
    REFERENCES `E_TBS`.`courses` (`course_code`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_professor`
    FOREIGN KEY (`professor_id`)
    REFERENCES `E_TBS`.`professors` (`professor_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE `E_TBS`.`classrooms` (
  `room_id` VARCHAR(10) NOT NULL,
  `room_name` VARCHAR(50) NOT NULL,
  `room_type` ENUM('Classroom', 'Lab', 'Amphitheater') NOT NULL,
  `capacity` SMALLINT UNSIGNED NOT NULL,
  `has_AC` TINYINT(1) NOT NULL DEFAULT 0,
  `has_projector` TINYINT(1) NOT NULL DEFAULT 0,
  `has_lights` TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`room_id`),
  INDEX `room_type_idx` (`room_type` ASC)
);

CREATE TABLE `E_TBS`.`sessions` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `course_professor_id` INT NOT NULL,
  `classroom_id` VARCHAR(10) NOT NULL,
  `day_of_week` ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday') NOT NULL,
  `start_time` TIME NOT NULL,
  `end_time` TIME NOT NULL,
  `duration` TINYINT UNSIGNED NOT NULL,
  `group_id` VARCHAR(10) NOT NULL,
  `status` ENUM('empty', 'waiting', 'full') NOT NULL DEFAULT 'empty',
  PRIMARY KEY (`id`),
  INDEX `course_professor_idx` (`course_professor_id` ASC),
  INDEX `classroom_idx` (`classroom_id` ASC),
  CONSTRAINT `fk_course_professor`
    FOREIGN KEY (`course_professor_id`)
    REFERENCES `E_TBS`.`course_professors` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_classroom`
    FOREIGN KEY (`classroom_id`)
    REFERENCES `E_TBS`.`classrooms` (`room_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `chk_time_logic`
    CHECK (`end_time` > `start_time`)
);


-- Athentication 
CREATE TABLE `E_TBS`.`student_users` (
  `student_id` VARCHAR(15) NOT NULL,
  `username` VARCHAR(50) UNIQUE NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `email` VARCHAR(100) UNIQUE NOT NULL,
  `notification_email` VARCHAR(100) NULL,
  `phone_number` VARCHAR(15) NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`student_id`),
  INDEX `username_idx` (`username` ASC),
  INDEX `email_idx` (`email` ASC),
  CONSTRAINT `fk_student_user`
    FOREIGN KEY (`student_id`)
    REFERENCES `E_TBS`.`students` (`student_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE `E_TBS`.`professor_users` (
  `professor_id` VARCHAR(15) NOT NULL,
  `username` VARCHAR(50) UNIQUE NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `email` VARCHAR(100) UNIQUE NOT NULL,
  `notification_email` VARCHAR(100) NULL,
  `phone_number` VARCHAR(15) NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`professor_id`),
  INDEX `username_idx` (`username` ASC),
  INDEX `email_idx` (`email` ASC),
  CONSTRAINT `fk_professor_user`
    FOREIGN KEY (`professor_id`)
    REFERENCES `E_TBS`.`professors` (`professor_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE `E_TBS`.`email_verifications` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `email` VARCHAR(100) UNIQUE NOT NULL,
  `hashed_code` VARCHAR(255) NOT NULL,
  `expires_at` TIMESTAMP NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `expires_idx` (`expires_at` ASC)
);


-- Attendance
CREATE TABLE `E_TBS`.`attendance_sessions` (
    `attendance_session_id` INT AUTO_INCREMENT PRIMARY KEY, 
    `course_professor_id` INT NOT NULL,                     
    `session_date` DATE NOT NULL,                           
    `start_time` TIME NOT NULL,                             
    `end_time` TIME NOT NULL,                               
    `location` VARCHAR(50) NULL,                            
    `details` TEXT NULL,                                    
    `attendance_csv_url` VARCHAR(255) NULL,                 
    `finalized_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,     
    FOREIGN KEY (`course_professor_id`) REFERENCES `E_TBS`.`course_professors`(`id`) ON DELETE CASCADE
);

CREATE TABLE `E_TBS`.`attendance_tracking` (
    `attendance_id` INT AUTO_INCREMENT PRIMARY KEY,            
    `attendance_session_id` INT NOT NULL,                      
    `student_id` VARCHAR(10) NOT NULL,                         
    `status` ENUM('Present', 'Absent') NOT NULL,               
    `address_of_attendance` VARCHAR(255) NULL,                 
    `attendance_time` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    `modified_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,  
    FOREIGN KEY (`attendance_session_id`) REFERENCES `E_TBS`.`attendance_sessions`(`attendance_session_id`) ON DELETE CASCADE,
    FOREIGN KEY (`student_id`) REFERENCES `E_TBS`.`students`(`student_id`) ON DELETE CASCADE
);


-- Discussion
CREATE TABLE `E_TBS`.`discussions` (
    `discussion_id` INT AUTO_INCREMENT PRIMARY KEY,   
    `course_professor_id` INT NOT NULL,              
    `student_id` VARCHAR(10) NOT NULL,               
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`course_professor_id`) REFERENCES `E_TBS`.`course_professors`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`student_id`) REFERENCES `E_TBS`.`students`(`student_id`) ON DELETE CASCADE
);

CREATE TABLE `E_TBS`.`discussion_messages` (
    `message_id` INT AUTO_INCREMENT PRIMARY KEY,   
    `discussion_id` INT NOT NULL,                   
    `sender_id` VARCHAR(10) NOT NULL,               
    `sender_type` ENUM('Student', 'Professor') NOT NULL,  
    `message` TEXT NOT NULL,                        
    `sent_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
    FOREIGN KEY (`discussion_id`) REFERENCES `E_TBS`.`discussions`(`discussion_id`) ON DELETE CASCADE
);


-- Professor announcement
CREATE TABLE `E_TBS`.`professor_announcement` (
    `announcement_id` INT AUTO_INCREMENT PRIMARY KEY,
    `course_professor_id` INT NOT NULL,
    `title` VARCHAR(255) NOT NULL,
    `content` TEXT NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`course_professor_id`) REFERENCES `E_TBS`.`course_professors`(`id`) ON DELETE CASCADE
);


-- QUIZ
CREATE TABLE `E_TBS`.`quizzes` (
    `quiz_id` INT AUTO_INCREMENT PRIMARY KEY,
    `course_professor_id` INT NOT NULL,
    `title` VARCHAR(255) NOT NULL,
    `description` TEXT,
    `duration` INT NOT NULL,
    `date` DATE NOT NULL,
    `start_time` TIME NOT NULL,
    `question_weight` INT NOT NULL,
    `number_of_questions` INT NOT NULL,
    `grade` DECIMAL(5,2) NOT NULL,
    `quiz_type` ENUM('Single Choice', 'Multiple Choice') NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `pdf_url` VARCHAR(255) DEFAULT NULL,
    `grades_csv_url` VARCHAR(255) DEFAULT NULL,
    `finalized_at` TIMESTAMP DEFAULT NULL,
    FOREIGN KEY (`course_professor_id`) REFERENCES `E_TBS`.`course_professors`(`id`) ON DELETE CASCADE
);

CREATE TABLE `E_TBS`.`quiz_questions` (
    `question_id` INT AUTO_INCREMENT PRIMARY KEY,
    `quiz_id` INT NOT NULL,
    `question_text` TEXT NOT NULL,
    FOREIGN KEY (`quiz_id`) REFERENCES `E_TBS`.`quizzes`(`quiz_id`) ON DELETE CASCADE
);

CREATE TABLE `E_TBS`.`quiz_choices` (
    `choice_id` INT AUTO_INCREMENT PRIMARY KEY,
    `question_id` INT NOT NULL,
    `choice_text` TEXT NOT NULL,
    `is_correct` BOOLEAN NOT NULL,
    FOREIGN KEY (`question_id`) REFERENCES `E_TBS`.`quiz_questions`(`question_id`) ON DELETE CASCADE
);

CREATE TABLE `E_TBS`.`student_quiz_submissions` (
    `submission_id` INT AUTO_INCREMENT PRIMARY KEY,
    `quiz_id` INT NOT NULL,
    `student_id` VARCHAR(10) NOT NULL,
    `grade` DECIMAL(5,2) NOT NULL,
    `submitted_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `note` TEXT DEFAULT NULL,
    FOREIGN KEY (`quiz_id`) REFERENCES `E_TBS`.`quizzes`(`quiz_id`) ON DELETE CASCADE,
    FOREIGN KEY (`student_id`) REFERENCES `E_TBS`.`students`(`student_id`) ON DELETE CASCADE
);


-- Assignment
CREATE TABLE `E_TBS`.`assignments` (
    `assignment_id` INT AUTO_INCREMENT PRIMARY KEY,
    `course_professor_id` INT NOT NULL,
    `title` VARCHAR(255) NOT NULL,
    `description` TEXT,
    `grade` DECIMAL(5,2),
    `document_url` VARCHAR(255),
    `deadline` TIMESTAMP NOT NULL,
    `grades_csv_url` VARCHAR(255),
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`course_professor_id`) REFERENCES `E_TBS`.`course_professors`(`id`) ON DELETE CASCADE
);

CREATE TABLE `E_TBS`.`assignment_submissions` (
    `submission_id` INT AUTO_INCREMENT PRIMARY KEY,
    `assignment_id` INT NOT NULL,
    `student_id` VARCHAR(10) NOT NULL,
    `answer_text` TEXT,
    `answer_file_url` VARCHAR(255),
    `submission_time` TIMESTAMP NOT NULL,
    FOREIGN KEY (`assignment_id`) REFERENCES `E_TBS`.`assignments`(`assignment_id`) ON DELETE CASCADE,
    FOREIGN KEY (`student_id`) REFERENCES `E_TBS`.`students`(`student_id`) ON DELETE CASCADE
);

CREATE TABLE `E_TBS`.`assignment_grades` (
    `grade_id` INT AUTO_INCREMENT PRIMARY KEY,
    `assignment_id` INT NOT NULL,
    `student_id` VARCHAR(10) NOT NULL,
    `batch_submission_time` TIMESTAMP NOT NULL,
    `grade` DECIMAL(5,2),
    FOREIGN KEY (`assignment_id`) REFERENCES `E_TBS`.`assignments`(`assignment_id`) ON DELETE CASCADE,
    FOREIGN KEY (`student_id`) REFERENCES `E_TBS`.`students`(`student_id`) ON DELETE CASCADE
);


-- Course materials
CREATE TABLE `E_TBS`.`course_materials` (
    `material_id` INT AUTO_INCREMENT PRIMARY KEY,
    `course_professor_id` INT NOT NULL,
    `title` VARCHAR(255) NOT NULL,
    `document_url` VARCHAR(255) NOT NULL,
    `is_published` BOOLEAN DEFAULT FALSE,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `published_at` TIMESTAMP DEFAULT NULL,
    FOREIGN KEY (`course_professor_id`) REFERENCES `E_TBS`.`course_professors`(`id`) ON DELETE CASCADE
);


-- Discussion Forum
CREATE TABLE `E_TBS`.`forum_posts` (
    `post_id` INT AUTO_INCREMENT PRIMARY KEY,
    `professor_id` VARCHAR(10) NOT NULL,
    `title` VARCHAR(255) NOT NULL,
    `content` TEXT NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`professor_id`) REFERENCES `E_TBS`.`professors`(`professor_id`) ON DELETE CASCADE
);

CREATE TABLE `E_TBS`.`forum_comments` (
    `comment_id` INT AUTO_INCREMENT PRIMARY KEY,
    `post_id` INT NOT NULL,
    `professor_id` VARCHAR(10) NOT NULL,
    `comment_text` TEXT NOT NULL,
    `commented_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`post_id`) REFERENCES `E_TBS`.`forum_posts`(`post_id`) ON DELETE CASCADE,
    FOREIGN KEY (`professor_id`) REFERENCES `E_TBS`.`professors`(`professor_id`) ON DELETE CASCADE
);


-- Administration
CREATE TABLE `E_TBS`.`admin_questions` (
    `question_id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` VARCHAR(10) NOT NULL,
    `user_type` ENUM('Student', 'Professor') NOT NULL,
    `question_text` TEXT NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE `E_TBS`.`admin_answers` (
    `answer_id` INT AUTO_INCREMENT PRIMARY KEY,
    `question_id` INT NOT NULL UNIQUE,
    `answer_text` TEXT NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`question_id`) REFERENCES `E_TBS`.`admin_questions`(`question_id`) ON DELETE CASCADE
);

CREATE TABLE `E_TBS`.`admin_documents` (
    `document_id` INT AUTO_INCREMENT PRIMARY KEY,
    `title` VARCHAR(255) NOT NULL,
    `document_url` VARCHAR(255) NOT NULL,
    `visibility` ENUM('Students', 'Professors', 'Both') NOT NULL,
    `uploaded_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE `E_TBS`.`admin_announcements` (
    `announcement_id` INT AUTO_INCREMENT PRIMARY KEY,
    `title` VARCHAR(255) NOT NULL,
    `content` TEXT NOT NULL,
    `visibility` ENUM('Students', 'Professors', 'Both') NOT NULL,
    `posted_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Library
CREATE TABLE `E_TBS`.`reading_room1_tables` (
    `table_id` INT AUTO_INCREMENT PRIMARY KEY,
    `table_number` INT NOT NULL,
    `current_people` INT DEFAULT 0
);

CREATE TABLE `E_TBS`.`reading_room2_tables` (
    `table_id` INT AUTO_INCREMENT PRIMARY KEY,
    `table_number` INT NOT NULL,
    `current_people` INT DEFAULT 0
);

CREATE TABLE `E_TBS`.`library_usage` (
    `usage_id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` VARCHAR(10) NOT NULL,
    `room_number` INT NOT NULL CHECK (room_number IN (1, 2)),
    `table_id` INT NOT NULL,
    `sit_time` TIMESTAMP,
    `leave_time` TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `E_TBS`.`students`(`student_id`)
);

CREATE TABLE `E_TBS`.`daily_library_archive` (
    `archive_id` INT AUTO_INCREMENT PRIMARY KEY,
    `archive_date` DATE UNIQUE,
    `csv_file_path` VARCHAR(255) NOT NULL
);

CREATE TABLE `E_TBS`.`rr1_discussions` (
    `message_id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` VARCHAR(10) NOT NULL,
    `message` TEXT NOT NULL,
    `sent_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `E_TBS`.`students`(`student_id`) ON DELETE CASCADE
);

CREATE TABLE `E_TBS`.`rr2_discussions` (
    `message_id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` VARCHAR(10) NOT NULL,
    `message` TEXT NOT NULL,
    `sent_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `E_TBS`.`students`(`student_id`) ON DELETE CASCADE
);


-- Restaurant
CREATE TABLE `E_TBS`.`restaurant_registrations` (
    `registration_id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` VARCHAR(10) NOT NULL UNIQUE,
    `registration_date` DATE ,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `E_TBS`.`students`(`student_id`) ON DELETE CASCADE
);

CREATE TABLE `E_TBS`.`restaurant_registration_count` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `registration_date` DATE UNIQUE,
    `total_registered` INT DEFAULT 0
);

CREATE TABLE `E_TBS`.`restaurant_announcements` (
    `announcement_id` INT AUTO_INCREMENT PRIMARY KEY,
    `title` VARCHAR(255) NOT NULL,
    `content` TEXT NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Transcripts and grades
CREATE TABLE `E_TBS`.`student_transcripts` (
    `student_id` VARCHAR(10) PRIMARY KEY,
    `pdf_url` VARCHAR(255) NOT NULL,
    `uploaded_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `E_TBS`.`students`(`student_id`) ON DELETE CASCADE
);

CREATE TABLE `E_TBS`.`student_grades` (
    `grade_id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` VARCHAR(10) NOT NULL,
    `course_code` VARCHAR(10) NOT NULL,
    `course_name` VARCHAR(255) NOT NULL,
    `grade_type` ENUM('Midterm', 'Final', 'Total') NOT NULL,
    `grade` DECIMAL(5,2) NOT NULL,
    `letter_grade` VARCHAR(2) NOT NULL,
    `date_added` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `E_TBS`.`students`(`student_id`) ON DELETE CASCADE
);


-- SIMULATION DATA
INSERT INTO `E_TBS`.`students` (
    `student_id`, `national_id`, `first_name`, `last_name`, `email`, `phone_number`, 
    `date_of_birth`, `student_level`, `major`, `minor`, `student_status`
) VALUES
    ('BA27/045', '12385679', 'Asma', 'Boubaker', 'asma.boubaker@tbs.u-tunis.tn', '50394526', '2002-06-22', 'Senior', 'BA', 'IT', 'Active'),
    ('BA89/044', '10668679', 'Kenza', 'Bacha', 'kenza.bacha@tbs.u-tunis.tn', '98452763', '2005-07-22', 'Freshman', NULL, NULL, 'Active'),
    ('IT45/032', '14569832', 'Omar', 'Ben Salah', 'omar.bensalah@tbs.u-tunis.tn', '51236789', '2003-02-15', 'Junior', 'IT', 'BA', 'Active'),
    ('ACCT32/051', '19857432', 'Lina', 'Mansouri', 'lina.mansouri@tbs.u-tunis.tn', '53784920', '2001-11-30', 'Senior', 'ACCT', 'MRK', 'Active'),
    ('MRK67/019', '16893245', 'Sami', 'Gharbi', 'sami.gharbi@tbs.u-tunis.tn', '56983241', '2004-08-10', 'Sophomore', NULL, NULL, 'Active'),
    ('FIN78/065', '17896532', 'Hana', 'Trabelsi', 'hana.trabelsi@tbs.u-tunis.tn', '54123698', '2005-05-05', 'Freshman', NULL, NULL, 'Active'),
    ('BA55/087', '13248765', 'Mohamed', 'Dridi', 'mohamed.dridi@tbs.u-tunis.tn', '52874631', '2003-09-25', 'Junior', 'BA', 'FIN', 'Active'),
    ('IT98/033', '18957463', 'Sarah', 'Kacem', 'sarah.kacem@tbs.u-tunis.tn', '53987241', '2001-12-12', 'Senior', 'IT', 'IBE', 'Active'),
    ('ACCT88/021', '13456987', 'Youssef', 'Belhaj', 'youssef.belhaj@tbs.u-tunis.tn', '59874123', '2004-03-20', 'Sophomore', NULL, NULL, 'Active'),
    ('MRK23/056', '19876345', 'Ines', 'Jaziri', 'ines.jaziri@tbs.u-tunis.tn', '54781236', '2003-07-18', 'Junior', 'MRK', 'ACCT', 'Active'),
    ('FIN44/078', '14236598', 'Nour', 'Haddad', 'nour.haddad@tbs.u-tunis.tn', '52147839', '2002-01-14', 'Senior', 'FIN', 'IT', 'Graduated'),
    ('BA67/099', '19854237', 'Firas', 'Mekki', 'firas.mekki@tbs.u-tunis.tn', '58974125', '2005-10-05', 'Freshman', NULL, NULL, 'Active'),
    ('IT12/045', '15987423', 'Salma', 'Chakroun', 'salma.chakroun@tbs.u-tunis.tn', '57412398', '2002-04-09', 'Senior', 'IT', 'MRK', 'Suspended');

INSERT INTO `E_TBS`.`professors` (
    `professor_id`, `national_id`, `first_name`, `last_name`, `email`, `phone_number`, 
    `date_of_birth`, `department`, `office_location`
) VALUES
    ('BA57/025', '12365479', 'Karim', 'Boubaker', 'karim.boubaker@tbs.u-tunis.tn', '23798419', '1988-09-12', 'Business Administration', 'Office 17'),
    ('EC34/012', '13578942', 'Nadia', 'Triki', 'nadia.triki@tbs.u-tunis.tn', '24567891', '1975-06-28', 'Economics and Business Analytics', 'Office 10'),
    ('IT22/041', '19874532', 'Omar', 'Ben Salem', 'omar.bensalem@tbs.u-tunis.tn', '26547893', '1982-11-15', 'Information Technology', 'Office 22'),
    ('BA89/078', '14567823', 'Salma', 'Ghorbel', 'salma.ghorbel@tbs.u-tunis.tn', '23987451', '1990-04-03', 'Business Administration', 'Office 30'),
    ('EC11/057', '15673489', 'Khaled', 'Jlassi', 'khaled.jlassi@tbs.u-tunis.tn', '21459876', '1981-07-21', 'Economics and Business Analytics', 'Office 05'),
    ('IT67/023', '17893256', 'Faten', 'Chouchene', 'faten.chouchene@tbs.u-tunis.tn', '29834765', '1979-12-09', 'Information Technology', 'Office 19'),
    ('BA43/035', '19852347', 'Youssef', 'Dhaouadi', 'youssef.dhaouadi@tbs.u-tunis.tn', '25367149', '1987-03-14', 'Business Administration', 'Office 08'),
    ('EC29/064', '18674325', 'Amel', 'Haddad', 'amel.haddad@tbs.u-tunis.tn', '23758941', '1992-10-25', 'Economics and Business Analytics', 'Office 16'),
    ('IT98/011', '12987634', 'Mehdi', 'Karoui', 'mehdi.karoui@tbs.u-tunis.tn', '27658943', '1985-05-31', 'Information Technology', 'Office 12'),
    ('BA77/055', '15426789', 'Sonia', 'Ben Ammar', 'sonia.benammar@tbs.u-tunis.tn', '24987135', '1991-08-07', 'Business Administration', 'Office 20'),
    ('EC56/039', '13254798', 'Ahmed', 'Mokhtar', 'ahmed.mokhtar@tbs.u-tunis.tn', '24536798', '1978-02-18', 'Economics and Business Analytics', 'Office 14');

INSERT INTO `E_TBS`.`courses` (
    `course_code`, `course_name`, `semester`, `level`, `credits`, `has_tutorial`
) VALUES
    ('BCOR110', 'Calculus for Business', 'Spring', 'Freshman', 3, TRUE),
    ('BCOR111', 'Linear Algebra for Business', 'Spring', 'Freshman', 3, TRUE),
    ('BCOR150', 'Probability & Statistics for Business I', 'Spring', 'Freshman', 3, TRUE),
    ('BCOR200', 'Introduction to Management of Information Systems', 'Spring', 'Sophomore', 3, FALSE),
    ('BCOR210', 'Fundamentals of Marketing', 'Spring', 'Sophomore', 3, TRUE),
    ('BCOR270', 'Business Law', 'Spring', 'Sophomore', 3, FALSE),
    ('NBC100', 'Intensive General English', 'Spring', 'Freshman', 3, FALSE),
    ('NBC101', 'Debating Skills', 'Spring', 'Freshman', 1, FALSE),
    ('CS100', 'Algorithms and Initiation to Programming', 'Spring', 'Freshman', 3, FALSE),
    ('CS220', 'Object Oriented Programming (OOP with Java)', 'Spring', 'Sophomore', 3, FALSE),
    ('ACCT300', 'Advanced Managerial Accounting', 'Spring', 'Junior', 3, TRUE),
    ('ACCT400', 'Advanced Accounting', 'Spring', 'Senior', 3, TRUE),
    ('BA300', 'Decision and Game Theory', 'Spring', 'Junior', 3, TRUE),
    ('BA305', 'Production and Operation Management', 'Spring', 'Junior', 3, FALSE),
    ('BA450', 'Decision Support Systems', 'Spring', 'Senior', 3, FALSE),
    ('BA460', 'Risk Analysis', 'Spring', 'Senior', 3, TRUE),
    ('FIN330', 'Derivative Securities', 'Spring', 'Junior', 3, TRUE),
    ('FIN350', 'Financial Markets', 'Spring', 'Junior', 3, TRUE),
    ('FIN420', 'Computer Applications in Finance', 'Spring', 'Senior', 3, FALSE),
    ('FIN440', 'Advanced Corporate Finance', 'Spring', 'Senior', 3, TRUE),
    ('IT300', 'Database Management', 'Spring', 'Junior', 3, FALSE),
    ('IT310', 'Computer Networking Basics', 'Spring', 'Junior', 3, FALSE),
    ('IT460', 'Cloud Computing Technologies and Economic Models', 'Spring', 'Senior', 3, FALSE),
    ('IT480', 'Data Warehousing and Data Mining', 'Spring', 'Senior', 3, FALSE),
    ('IBE300', 'International Trade', 'Spring', 'Junior', 3, FALSE),
    ('IPE320', 'International Macroeconomics', 'Spring', 'Junior', 3, FALSE),
    ('MRK320', 'International Marketing', 'Spring', 'Junior', 3, FALSE),
    ('MRK330', 'Marketing Channel', 'Spring', 'Junior', 3, TRUE),
    ('MRK430', 'Brand Management', 'Spring', 'Senior', 3, FALSE),
    ('MRK440', 'Strategic Marketing Management', 'Fall', 'Senior', 3, FALSE);


INSERT INTO `E_TBS`.`student_courses` (`student_id`, `course_code`, `group_id`) VALUES
    ('BA27/045', 'BA450', 'S.BA.IT'),
    ('BA27/045', 'BA300', 'Ju.BA.FIN'),
    ('BA27/045', 'CS220', 'So.3'),
    ('BA27/045', 'BCOR210', 'So.4'),
    ('BA27/045', 'BCOR111', 'F.1'),
    ('BA89/044', 'CS220', 'So.3'),
    ('BA89/044', 'BCOR210', 'So.3'),
    ('BA89/044', 'BCOR200', 'So.1'),
    ('BA89/044', 'BCOR111', 'F.2'),
	('BA89/044', 'BA300', 'Ju.BA.IBE');


INSERT INTO `E_TBS`.`course_professors` (`course_code`, `professor_id`, `session_type`) VALUES
    ('BA450', 'BA57/025', 'Lecture'),
    ('CS220', 'BA57/025', 'Lecture'),
    ('BCOR210', 'BA57/025', 'Lecture'),
    ('BA300', 'BA57/025', 'Tutorial'),
    ('BCOR210', 'EC34/012', 'Tutorial'),
    ('BCOR111', 'EC34/012', 'Lecture'),
    ('BA300', 'EC34/012', 'Lecture'),
    ('BCOR210', 'IT22/041', 'Tutorial'),
    ('BCOR111', 'IT22/041', 'Tutorial'),
    ('BCOR200', 'IT22/041', 'Lecture');
  
INSERT INTO `E_TBS`.`course_professors` (`course_code`, `professor_id`, `session_type`) VALUES
    ('BA300', 'IT22/041', 'Lecture');
  
INSERT INTO `E_TBS`.`classrooms` (`room_id`, `room_name`, `room_type`, `capacity`, `has_AC`, `has_projector`, `has_lights`) VALUES
-- Amphitheaters
('A1', 'Amphitheater 1', 'Amphitheater', 200, 1, 0, 1),
('A2', 'Amphitheater 2', 'Amphitheater', 200, 1, 0, 1),
('A3', 'Amphitheater 3', 'Amphitheater', 100, 1, 1, 1),
('A4', 'Amphitheater 4', 'Amphitheater', 100, 1, 1, 1),
('A5', 'Amphitheater 5', 'Amphitheater', 100, 1, 1, 0),
('A6', 'Amphitheater 6', 'Amphitheater', 200, 1, 1, 0),
('A7', 'Amphitheater 7', 'Amphitheater', 200, 1, 1, 0),
('A8', 'Amphitheater 8', 'Amphitheater', 100, 1, 1, 1),
('A9', 'Amphitheater 9', 'Amphitheater', 100, 1, 1, 1),
('A10', 'Amphitheater 10', 'Amphitheater', 100, 1, 1, 1),
('A11', 'Amphitheater 11', 'Amphitheater', 400, 1, 0, 1),
('A12', 'Amphitheater 12', 'Amphitheater', 400, 1, 1, 1),

-- Classrooms 1-20 (Capacity 25, No AC, No Projector, All have lights except 11)
('C1', 'Classroom 1', 'Classroom', 25, 0, 0, 1),
('C2', 'Classroom 2', 'Classroom', 25, 0, 0, 1),
('C3', 'Classroom 3', 'Classroom', 25, 0, 0, 1),
('C4', 'Classroom 4', 'Classroom', 25, 0, 0, 1),
('C5', 'Classroom 5', 'Classroom', 25, 0, 0, 1),
('C6', 'Classroom 6', 'Classroom', 25, 0, 0, 1),
('C7', 'Classroom 7', 'Classroom', 25, 0, 0, 1),
('C8', 'Classroom 8', 'Classroom', 25, 0, 0, 1),
('C9', 'Classroom 9', 'Classroom', 25, 0, 0, 1),
('C10', 'Classroom 10', 'Classroom', 25, 0, 0, 1),
('C11', 'Classroom 11', 'Classroom', 25, 0, 0, 0),
('C12', 'Classroom 12', 'Classroom', 25, 0, 0, 1),
('C13', 'Classroom 13', 'Classroom', 25, 0, 0, 1),
('C14', 'Classroom 14', 'Classroom', 25, 0, 0, 1),
('C15', 'Classroom 15', 'Classroom', 25, 0, 0, 1),
('C16', 'Classroom 16', 'Classroom', 25, 0, 0, 1),
('C17', 'Classroom 17', 'Classroom', 25, 0, 0, 1),
('C18', 'Classroom 18', 'Classroom', 25, 0, 0, 1),
('C19', 'Classroom 19', 'Classroom', 25, 0, 0, 1),
('C20', 'Classroom 20', 'Classroom', 25, 0, 0, 1),

-- Classrooms 21-32 (Capacity 40, No AC, No Projector, All have lights except 30)
('C21', 'Classroom 21', 'Classroom', 40, 0, 0, 1),
('C22', 'Classroom 22', 'Classroom', 40, 0, 0, 1),
('C23', 'Classroom 23', 'Classroom', 40, 0, 0, 1),
('C24', 'Classroom 24', 'Classroom', 40, 0, 0, 1),
('C25', 'Classroom 25', 'Classroom', 40, 0, 0, 1),
('C26', 'Classroom 26', 'Classroom', 40, 0, 0, 1),
('C27', 'Classroom 27', 'Classroom', 40, 0, 0, 1),
('C28', 'Classroom 28', 'Classroom', 40, 0, 0, 1),
('C29', 'Classroom 29', 'Classroom', 40, 0, 0, 1),
('C30', 'Classroom 30', 'Classroom', 40, 0, 0, 0),
('C31', 'Classroom 31', 'Classroom', 40, 0, 0, 1),
('C32', 'Classroom 32', 'Classroom', 40, 0, 0, 1),

-- Labs 1-9 (Capacity 25, All have lights, All have AC except for Lab 5 and 2, All have projectors except Lab 1 and 2)
('L1', 'Lab 1', 'Lab', 25, 1, 0, 1),
('L2', 'Lab 2', 'Lab', 25, 0, 0, 1),
('L3', 'Lab 3', 'Lab', 25, 1, 1, 1),
('L4', 'Lab 4', 'Lab', 25, 1, 1, 1),
('L5', 'Lab 5', 'Lab', 25, 0, 1, 1),
('L6', 'Lab 6', 'Lab', 25, 1, 1, 1),
('L7', 'Lab 7', 'Lab', 25, 1, 1, 1),
('L8', 'Lab 8', 'Lab', 25, 1, 1, 1),
('L9', 'Lab 9', 'Lab', 25, 1, 1, 1);



INSERT INTO `E_TBS`.`classrooms` (`room_id`, `room_name`, `room_type`, `capacity`, `has_AC`, `has_projector`, `has_lights`) VALUES
('C33', 'Classroom 33', 'Classroom', 40, 0, 0, 1),
('C34', 'Classroom 34', 'Classroom', 40, 0, 0, 1);

INSERT INTO `E_TBS`.`sessions` (`course_professor_id`, `classroom_id`, `day_of_week`, `start_time`, `end_time`, `duration`, `group_id`, `status`) VALUES
-- BA450 Lecture for S.BA.IT
(61, 'A3', 'Monday', '08:30', '11:30', 180, 'S.BA.IT', 'empty'),

-- CS220 Lecture for So.3 and So.2 together
(62, 'L3', 'Monday', '13:30', '16:30', 180, 'So.3', 'empty'),
(62, 'L3', 'Monday', '13:30', '16:30', 180, 'So.2', 'empty'),
-- CS220 Lecture for So.1
(62, 'L4', 'Tuesday', '08:30', '11:30', 180, 'So.1', 'empty'),

-- BCOR210 Lecture for So.4 and So.3 together
(63, 'A6', 'Wednesday', '08:30', '11:30', 180, 'So.4', 'empty'),
(63, 'A6', 'Wednesday', '08:30', '11:30', 180, 'So.3', 'empty'),

-- BA300 Tutorial for Ju.BA.IT and Ju.BA.FIN
(64, 'C5', 'Tuesday', '11:30', '13:00', 90, 'Ju.BA.IT', 'empty'),
(64, 'C15', 'Friday', '08:30', '10:00', 90, 'Ju.BA.FIN', 'empty'),

-- BCOR210 Tutorial for So.4
(65, 'C8', 'Thursday', '13:30', '15:00', 90, 'So.4', 'empty'),

-- BCOR111 Lecture for F.1 and F.2
(66, 'A5', 'Friday', '08:30', '11:30', 180, 'F.1', 'empty'),
(66, 'A3', 'Wednesday', '08:30', '11:30', 180, 'F.2', 'empty'),

-- BA300 Lecture for Ju.BA.IT and Ju.BA.FIN together
(67, 'A11', 'Thursday', '10:00', '13:00', 180, 'Ju.BA.IT', 'empty'),
(67, 'A11', 'Thursday', '10:00', '13:00', 180, 'Ju.BA.FIN', 'empty'),

-- BCOR210 Tutorial for So.3
(68, 'C10', 'Monday', '10:00', '11:30', 90, 'So.3', 'empty'),

-- BCOR111 Tutorial for F.1 and F.2
(69, 'C12', 'Wednesday', '10:00', '11:30', 90, 'F.1', 'empty'),
(69, 'C1', 'Thursday', '11:30', '13:00', 90, 'F.2', 'empty'),

-- BCOR200 Lecture for So.1 and So.3 together
(70, 'A7', 'Friday', '08:30', '11:30', 180, 'So.1', 'empty'),
(70, 'A7', 'Friday', '08:30', '11:30', 180, 'So.3', 'empty'),

-- BA300 Lecture for Ju.BA.IBE
(71, 'A8', 'Wednesday', '13:30', '16:30', 180, 'Ju.BA.IBE', 'empty');

INSERT INTO `E_TBS`.`sessions` (`course_professor_id`, `classroom_id`, `day_of_week`, `start_time`, `end_time`, `duration`, `group_id`) VALUES
-- BA450 Lecture for S.BA.IT
(61, 'A11', 'Monday', '01:30', '02:30', 60, 'S.BA.IT');



SELECT * 
FROM `E_TBS`.`sessions` AS s
JOIN `E_TBS`.`course_professors` AS cp 
ON s.`course_professor_id` = cp.`id`
WHERE cp.`professor_id` = 'IT22/041';


ALTER TABLE `E_TBS`.`sessions` 
DROP COLUMN `status`;


ALTER TABLE `E_TBS`.`classrooms`
ADD COLUMN `status` ENUM('empty', 'waiting', 'full','unavailable') NOT NULL DEFAULT 'empty';

INSERT INTO `E_TBS`.`classrooms` (`room_id`, `room_name`, `room_type`, `capacity`, `has_AC`, `has_projector`, `has_lights`,`status`) VALUES
('L10', 'Lab 10', 'Lab', 25, 1, 1, 1,'empty'),
('LLINUX', 'Lab Linux', 'Lab', 25, 1, 1, 1,'empty'),
('LLINUX2', 'Lab Linux 2', 'Lab', 25, 1, 1, 1,'empty');


ALTER TABLE `E_TBS`.`attendance_sessions`
ADD COLUMN `closed` BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE `E_TBS`.`attendance_tracking` 
DROP COLUMN `status`;

ALTER TABLE `E_TBS`.`attendance_tracking`
ADD COLUMN `latitude` DECIMAL(9,6),
ADD COLUMN `longitude` DECIMAL(9,6);

ALTER TABLE `E_TBS`.`attendance_tracking`
ADD COLUMN `comment` text;



-- From here i will try to put real data (but with some fake details for confidentiality)

INSERT INTO `E_TBS`.`professors` (
    `professor_id`, `national_id`, `first_name`, `last_name`, `email`, `phone_number`, 
    `date_of_birth`, `department`, `office_location`
) VALUES
    ('IT45/019', '19876501', 'Mehdi', 'Khouja', 'mehdi.khouja@tbs.u-tunis.tn', '21564321', '1984-03-21', 'Information Technology', 'Office 31'),
    ('EC23/077', '19873402', 'Hichem', 'Hasnaoui', 'hichem.hasnaoui@tbs.u-tunis.tn', '21459870', '1980-10-15', 'Economics and Business Analytics', 'Office 27'),
    ('BA54/088', '18976320', 'Maher', 'Khadhraoui', 'maher.khadhraoui@tbs.u-tunis.tn', '22549871', '1987-12-04', 'Business Administration', 'Office 21'),
    ('IT39/016', '17654321', 'Sondos', 'Bannouri', 'sondos.bannouri@tbs.u-tunis.tn', '21678432', '1990-06-09', 'Information Technology', 'Office 32'),
    ('EC65/022', '14327895', 'Zied', 'Nouira', 'zied.nouira@tbs.u-tunis.tn', '21456678', '1985-11-23', 'Economics and Business Analytics', 'Office 33'),
    ('IT71/024', '15678934', 'Imen', 'Chakroun', 'imen.chakroun@tbs.u-tunis.tn', '21875433', '1988-08-14', 'Information Technology', 'Office 26'),
    ('BA29/046', '15437682', 'Sami', 'Loukil', 'sami.loukil@tbs.u-tunis.tn', '21984675', '1986-04-11', 'Business Administration', 'Office 24'),
    ('IT88/027', '18976543', 'Thouraya', 'Laabidi', 'thouraya.laabidi@tbs.u-tunis.tn', '21345765', '1983-09-30', 'Information Technology', 'Office 28'),
    ('BA91/033', '12345678', 'Kholoud', 'Farza', 'kholoud.farza@tbs.u-tunis.tn', '22234567', '1989-02-25', 'Business Administration', 'Office 36'),
    ('BA61/070', '19976352', 'Asma', 'Ben Yaghlene', 'asma.benyaghlene@tbs.u-tunis.tn', '21876345', '1991-01-13', 'Business Administration', 'Office 29'),
    ('EC42/031', '13246789', 'Bassem', 'Elkaw', 'bassem.elkaw@tbs.u-tunis.tn', '21896743', '1979-03-03', 'Economics and Business Analytics', 'Office 13'),
    ('BA38/047', '14827365', 'Salah', 'Ben Abdallah', 'salah.benabdallah@tbs.u-tunis.tn', '21356789', '1977-07-07', 'Business Administration', 'Office 11'),
    ('EC84/014', '16748392', 'Ridha', 'Esghaier', 'ridha.esghaier@tbs.u-tunis.tn', '21678934', '1976-05-19', 'Economics and Business Analytics', 'Office 06'),
    ('IT32/055', '16547892', 'Lamia', 'Rezgui', 'lamia.rezgui@tbs.u-tunis.tn', '21234569', '1984-06-29', 'Information Technology', 'Office 23'),
    ('EC87/066', '17894567', 'Zohra', 'Maalej', 'zohra.maalej@tbs.u-tunis.tn', '21783456', '1985-01-22', 'Economics and Business Analytics', 'Office 09'),
    ('BA80/068', '15893247', 'Bouthaina', 'Msaad', 'bouthaina.msaad@tbs.u-tunis.tn', '21438965', '1983-10-16', 'Business Administration', 'Office 34'),
    ('BA90/079', '12457896', 'Mohamed', 'Ben Nouri', 'mohamed.bennouri@tbs.u-tunis.tn', '21679834', '1982-01-27', 'Business Administration', 'Office 35'),
    ('EC61/044', '13876543', 'Rania', 'Bousslema', 'rania.bousslema@tbs.u-tunis.tn', '21738456', '1989-04-15', 'Economics and Business Analytics', 'Office 18'),
    ('BA55/065', '11234567', 'Aymen', 'Mohamed', 'aymen.mohamed@tbs.u-tunis.tn', '21457634', '1986-02-12', 'Business Administration', 'Office 37'),
    ('IT83/031', '13456789', 'Rim', 'Kefela', 'rim.kefela@tbs.u-tunis.tn', '21384920', '1992-07-03', 'Information Technology', 'Office 38'),
    ('IT47/029', '16587432', 'Ghassen', 'Aydi', 'ghassen.aydi@tbs.u-tunis.tn', '21584920', '1980-10-10', 'Information Technology', 'Office 39'),
    ('EC33/077', '15437826', 'Mariem', 'Thaalbi', 'mariem.thaalbi@tbs.u-tunis.tn', '21739854', '1990-11-04', 'Economics and Business Analytics', 'Office 15'),
    ('BA99/022', '15432678', 'Tarek', 'Ben Noamen', 'tarek.bennoamen@tbs.u-tunis.tn', '21789432', '1981-08-24', 'Business Administration', 'Office 40'),
    ('EC72/062', '13428765', 'Fedia', 'Daami', 'fedia.daami@tbs.u-tunis.tn', '21375849', '1987-12-18', 'Economics and Business Analytics', 'Office 41'),
    ('IT28/059', '13348726', 'Cyrine', 'Chaieb', 'cyrine.chaieb@tbs.u-tunis.tn', '21584976', '1989-09-29', 'Information Technology', 'Office 42'),
    ('EC93/018', '13487659', 'Nour', 'Boughanmi', 'nour.boughanmi@tbs.u-tunis.tn', '21246789', '1993-05-01', 'Economics and Business Analytics', 'Office 43'),
    ('IT49/037', '15734928', 'Ferdaws', 'Ezzi', 'ferdaws.ezzi@tbs.u-tunis.tn', '21609834', '1991-03-31', 'Information Technology', 'Office 44'),
    ('BA63/089', '18726354', 'Montassar', 'Ben Massoud', 'montassar.benmassoud@tbs.u-tunis.tn', '21569347', '1984-04-07', 'Business Administration', 'Office 45'),
    ('EC48/073', '17834527', 'Manel', 'Abdelkader', 'manel.abdelkader@tbs.u-tunis.tn', '21638945', '1992-10-11', 'Economics and Business Analytics', 'Office 46'),
    ('IT36/015', '14285796', 'Eya', 'Bedhiafi', 'eya.bedhiafi@tbs.u-tunis.tn', '21398452', '1990-12-08', 'Information Technology', 'Office 47'),
    ('EC51/071', '13257849', 'Nesrine', 'Zouaoui', 'nesrine.zouaoui@tbs.u-tunis.tn', '21984756', '1988-07-02', 'Economics and Business Analytics', 'Office 48'),
    ('BA74/028', '15897364', 'Amine', 'Ben Said', 'amine.bensaid@tbs.u-tunis.tn', '21837495', '1986-01-06', 'Business Administration', 'Office 49'),
    ('IT55/067', '14893276', 'Montasar', 'Agrebi', 'montasar.agrebi@tbs.u-tunis.tn', '21709845', '1991-06-21', 'Information Technology', 'Office 50'),
    ('EC69/024', '13749852', 'Hedi', 'Essid', 'hedi.essid@tbs.u-tunis.tn', '21384976', '1982-09-13', 'Economics and Business Analytics', 'Office 51'),
    ('IT30/030', '13658974', 'Ibtissem', 'Issaoui', 'ibtissem.issaoui@tbs.u-tunis.tn', '21758934', '1987-08-10', 'Information Technology', 'Office 52'),
    ('BA87/021', '17892356', 'Mondher', 'Hassen', 'mondher.hassen@tbs.u-tunis.tn', '21589743', '1985-03-08', 'Business Administration', 'Office 53'),
    ('EC55/088', '14563287', 'Laassed', 'Elmoubarki', 'laassed.elmoubarki@tbs.u-tunis.tn', '21908734', '1979-10-19', 'Economics and Business Analytics', 'Office 54'),
    ('IT90/033', '17856329', 'Mongia', 'Besbes', 'mongia.besbes@tbs.u-tunis.tn', '21589321', '1981-11-26', 'Information Technology', 'Office 55'),
    ('EC40/057', '13568974', 'Eymen', 'Erraies', 'eymen.erraies@tbs.u-tunis.tn', '21743985', '1986-06-17', 'Economics and Business Analytics', 'Office 56'),
    ('BA85/077', '13984726', 'Pedro', 'Telleria', 'pedro.telleria@tbs.u-tunis.tn', '21586934', '1978-04-14', 'Business Administration', 'Office 57'),
    ('EC70/017', '13345786', 'Naceur', 'Azaiez', 'naceur.azaiez@tbs.u-tunis.tn', '21487563', '1980-12-22', 'Economics and Business Analytics', 'Office 58'),
    ('EC91/079', '13467589', 'Naceur', 'Khraief', 'naceur.khraief@tbs.u-tunis.tn', '21573849', '1983-07-20', 'Economics and Business Analytics', 'Office 59'),
    ('BA78/083', '12876543', 'Sonia', 'Rebai', 'sonia.rebai@tbs.u-tunis.tn', '21583947', '1989-09-05', 'Business Administration', 'Office 60'),
    ('EC92/021', '12347896', 'Nidhal', 'Moumen', 'nidhal.moumen@tbs.u-tunis.tn', '21374985', '1985-10-01', 'Economics and Business Analytics', 'Office 61'),
    ('EC60/050', '14358967', 'Faten', 'Kateb', 'faten.kateb@tbs.u-tunis.tn', '21674892', '1988-11-18', 'Economics and Business Analytics', 'Office 62'),
    ('IT84/066', '19847623', 'Olfa', 'Tebini', 'olfa.tebini@tbs.u-tunis.tn', '21485976', '1986-02-27', 'Information Technology', 'Office 63'),
    ('IT31/026', '18645239', 'Anas', 'Ksontini', 'anas.ksontini@tbs.u-tunis.tn', '21789632', '1991-03-20', 'Information Technology', 'Office 64'),
    ('EC85/045', '12987346', 'Amira', 'Zribi', 'amira.zribi@tbs.u-tunis.tn', '21693485', '1990-09-25', 'Economics and Business Analytics', 'Office 65'),
    ('BA53/048', '14573289', 'Riadh', 'Aloui', 'riadh.aloui@tbs.u-tunis.tn', '21493857', '1982-12-14', 'Business Administration', 'Office 66'),
    ('IT58/041', '13458967', 'Mohamed', 'Hamdoun', 'mohamed.hamdoun@tbs.u-tunis.tn', '21584326', '1987-05-16', 'Information Technology', 'Office 67'),
    ('IT50/038', '13276945', 'Ilyes', 'Ben Rejeb', 'ilyes.benrejeb@tbs.u-tunis.tn', '21749385', '1993-01-09', 'Information Technology', 'Office 68'),
    ('EC46/080', '13846927', 'Hedia', 'Guidara', 'hedia.guidara@tbs.u-tunis.tn', '21834765', '1977-06-06', 'Economics and Business Analytics', 'Office 69');


INSERT INTO `E_TBS`.`professors` (
    `professor_id`, `national_id`, `first_name`, `last_name`, `email`, `phone_number`, 
    `date_of_birth`, `department`, `office_location`
) VALUES
    ('IT45/061', '16892475', 'Ghassen', 'Ben Belgacem', 'ghassen.benbelgacem@tbs.u-tunis.tn', '23476591', '1983-01-19', 'Information Technology', 'Office 25'),
    ('EC24/048', '12349872', 'Fadoua', 'Nasri', 'fadoua.nasri@tbs.u-tunis.tn', '26789123', '1980-03-27', 'Economics and Business Analytics', 'Office 13'),
    ('BA69/031', '13478529', 'Khalil', 'Matar', 'khalil.matar@tbs.u-tunis.tn', '23984672', '1987-10-04', 'Business Administration', 'Office 06'),
    ('BA50/044', '17983426', 'Amira', 'Dridi', 'amira.dridi@tbs.u-tunis.tn', '27483915', '1993-06-12', 'Business Administration', 'Office 26'),
    ('IT88/036', '19874529', 'Ameni', 'Azouz', 'ameni.azouz@tbs.u-tunis.tn', '27891453', '1991-11-29', 'Information Technology', 'Office 24'),
    ('EC13/059', '15432768', 'Sami', 'Sfaxi', 'sami.sfaxi@tbs.u-tunis.tn', '24578912', '1985-08-06', 'Economics and Business Analytics', 'Office 09'),
    ('EC66/021', '14798235', 'Raouf', 'Madelgi', 'raouf.madelgi@tbs.u-tunis.tn', '24873459', '1976-04-15', 'Economics and Business Analytics', 'Office 04'),
    ('EC81/046', '13986527', 'Nidhal', 'Merzgui', 'nidhal.merzgui@tbs.u-tunis.tn', '25784613', '1982-07-03', 'Economics and Business Analytics', 'Office 28'),
    ('BA61/057', '16543789', 'Bassem', 'Guizani', 'bassem.guizani@tbs.u-tunis.tn', '21457689', '1988-09-09', 'Business Administration', 'Office 15'),
    ('BA74/049', '15439872', 'Yosra', 'Soussi', 'yosra.soussi@tbs.u-tunis.tn', '24563879', '1992-02-26', 'Business Administration', 'Office 23'),
    ('EC29/076', '17654382', 'Hend', 'Kharroubi', 'hend.kharroubi@tbs.u-tunis.tn', '23985741', '1984-05-18', 'Economics and Business Analytics', 'Office 27'),
    ('IT71/018', '16823579', 'Maher', 'Labidi', 'maher.labidi@tbs.u-tunis.tn', '23487951', '1986-12-07', 'Information Technology', 'Office 18'),
    ('EC20/058', '19745328', 'Houssem', 'Ben Mrad', 'houssem.benmrad@tbs.u-tunis.tn', '21784563', '1981-01-23', 'Economics and Business Analytics', 'Office 07'),
    ('BA58/062', '14573926', 'Dorra', 'Aloui', 'dorra.aloui@tbs.u-tunis.tn', '24587913', '1990-09-15', 'Business Administration', 'Office 21'),
    ('BA73/045', '16489375', 'Sarra', 'Jouini', 'sarra.jouini@tbs.u-tunis.tn', '24678954', '1989-10-10', 'Business Administration', 'Office 32'),
    ('IT93/030', '18374956', 'Aymen', 'Hedhili', 'aymen.hedhili@tbs.u-tunis.tn', '23984561', '1985-06-01', 'Information Technology', 'Office 31'),
    ('IT59/050', '19874587', 'Ines', 'Khmir', 'ines.khmir@tbs.u-tunis.tn', '27894513', '1993-08-30', 'Information Technology', 'Office 29'),
    ('IT90/043', '17894356', 'Ikram', 'Azzouz', 'ikram.azzouz@tbs.u-tunis.tn', '26354789', '1987-03-22', 'Information Technology', 'Office 11'),
    ('IT32/071', '19384756', 'Imen', 'Dhen', 'imen.dhen@tbs.u-tunis.tn', '25436789', '1994-12-14', 'Information Technology', 'Office 33'),
    ('EC75/026', '14923875', 'Hatem', 'Sghaier', 'hatem.sghaier@tbs.u-tunis.tn', '24891467', '1979-07-11', 'Economics and Business Analytics', 'Office 02'),
    ('BA52/034', '19823745', 'Asma', 'Chaabani', 'asma.chaabani@tbs.u-tunis.tn', '23784619', '1991-05-08', 'Business Administration', 'Office 34'),
    ('EC47/037', '15894376', 'Kais', 'Alimi', 'kais.alimi@tbs.u-tunis.tn', '23945781', '1983-11-17', 'Economics and Business Analytics', 'Office 03'),
    ('EC19/042', '16789345', 'Sana', 'Arfaoui', 'sana.arfaoui@tbs.u-tunis.tn', '27894312', '1990-01-05', 'Economics and Business Analytics', 'Office 35'),
    ('IT36/056', '18679235', 'Fedia', 'Telmoudi', 'fedia.telmoudi@tbs.u-tunis.tn', '26374981', '1986-03-30', 'Information Technology', 'Office 36'),
    ('BA39/041', '14382975', 'Kaouther', 'Soudani', 'kaouther.soudani@tbs.u-tunis.tn', '27483956', '1982-10-28', 'Business Administration', 'Office 37'),
    ('IT84/054', '19823756', 'Cyrine', 'Boukari', 'cyrine.boukari@tbs.u-tunis.tn', '27384910', '1992-06-06', 'Information Technology', 'Office 38'),
    ('BA85/065', '15326748', 'Selma', 'El Hadj', 'selma.elhadj@tbs.u-tunis.tn', '24879463', '1989-11-11', 'Business Administration', 'Office 39'),
    ('IT55/033', '17493568', 'Aymen', 'Chihi', 'aymen.chihi@tbs.u-tunis.tn', '23958741', '1988-04-19', 'Information Technology', 'Office 40'),
    ('EC53/051', '16384279', 'Farah', 'Daami', 'farah.daami@tbs.u-tunis.tn', '27389416', '1980-09-12', 'Economics and Business Analytics', 'Office 41');


INSERT INTO `E_TBS`.`professors` (
    `professor_id`, `national_id`, `first_name`, `last_name`, `email`, `phone_number`, 
    `date_of_birth`, `department`, `office_location`
) VALUES
    ('EC62/066', '18794328', 'Lamia', 'Mezghani', 'lamia.mezghani@tbs.u-tunis.tn', '25784931', '1984-03-22', 'Economics and Business Analytics', 'Office 42'),
    ('BA92/060', '19238475', 'Roua', 'Ben Ammar', 'roua.benammar@tbs.u-tunis.tn', '27483952', '1991-07-08', 'Business Administration', 'Office 43'),
    ('IT40/073', '16574829', 'Kenz', 'Ben Alaya', 'kenz.benalaya@tbs.u-tunis.tn', '26893471', '1992-05-14', 'Information Technology', 'Office 44');

ALTER TABLE `E_TBS`.`attendance_sessions`
ADD COLUMN `group_codes` TEXT ;


CREATE TABLE `E_TBS`.`semesters` (
  `id` INT NOT NULL,                 
  `name` VARCHAR(50) NOT NULL,         
  `start_date` DATE NOT NULL,
  `end_date` DATE NOT NULL,
  PRIMARY KEY (`id`)                  
);

CREATE TABLE `E_TBS`.`study_weeks` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `semester_id` INT NOT NULL,        
  `name` VARCHAR(100) NOT NULL,
  `start_date` DATE NOT NULL,
  `end_date` DATE NOT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`semester_id`) REFERENCES `semesters`(`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE `E_TBS`.`holidays` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `semester_id` INT NOT NULL,
  `name` VARCHAR(100) NOT NULL,
  `holiday_date` DATE NOT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`semester_id`) REFERENCES `semesters`(`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);


INSERT INTO `E_TBS`.`students` (
    `student_id`, `national_id`, `first_name`, `last_name`, `email`, `phone_number`,
    `date_of_birth`, `student_level`, `major`, `minor`, `student_status`
) VALUES
    ('MRK63/001', '87315920', 'Habib', 'Chahed', 'habib.chahed@tbs.u-tunis.tn', '59110115', '2005-07-13', 'Junior', 'BA', 'MRK', 'Active'),
    ('BA65/002', '11209557', 'Rania', 'Zouari', 'rania.zouari@tbs.u-tunis.tn', '56461511', '1999-11-08', 'Freshman', 'IT', 'BA', 'Active'),
    ('IT71/003', '60129162', 'Maha', 'Chahed', 'maha.chahed@tbs.u-tunis.tn', '50011106', '2002-07-26', 'Sophomore', 'BA', 'ACCT', 'Active'),
    ('ACCT54/004', '84425799', 'Hichem', 'Gharbi', 'hichem.gharbi@tbs.u-tunis.tn', '52630333', '2003-02-02', 'Senior', 'MRK', 'ACCT', 'Active'),
    ('BA61/005', '71620891', 'Sarra', 'Sassi', 'sarra.sassi@tbs.u-tunis.tn', '59482404', '2003-06-13', 'Freshman', 'MRK', NULL, 'Active'),
    ('MRK78/006', '79537868', 'Youssef', 'Slimi', 'youssef.slimi@tbs.u-tunis.tn', '50704990', '2005-10-08', 'Junior', 'MRK', 'IT', 'Active'),
    ('ACCT22/007', '81977542', 'Salma', 'Khaldi', 'salma.khaldi@tbs.u-tunis.tn', '59074298', '2000-04-01', 'Senior', 'ACCT', 'MRK', 'Active'),
    ('BA93/008', '64491984', 'Karim', 'Nouri', 'karim.nouri@tbs.u-tunis.tn', '53772782', '2001-11-13', 'Sophomore', 'BA', NULL, 'Active'),
    ('IT28/009', '10525946', 'Hiba', 'Zidi', 'hiba.zidi@tbs.u-tunis.tn', '54485988', '2002-09-07', 'Freshman', 'IT', 'ACCT', 'Active'),
    ('ACCT57/010', '19679014', 'Alaa', 'Zghal', 'alaa.zghal@tbs.u-tunis.tn', '55672806', '2003-05-23', 'Senior', 'MRK', 'BA', 'Active'),
    ('MRK45/011', '87721651', 'Chiraz', 'Mejri', 'chiraz.mejri@tbs.u-tunis.tn', '53870865', '2001-08-18', 'Junior', 'ACCT', NULL, 'Active'),
    ('IT66/012', '92742284', 'Nour', 'Trabelsi', 'nour.trabelsi@tbs.u-tunis.tn', '51368146', '2004-03-15', 'Sophomore', 'IT', 'MRK', 'Active'),
    ('BA79/013', '72580492', 'Anis', 'Hammami', 'anis.hammami@tbs.u-tunis.tn', '52117699', '2000-06-30', 'Senior', 'BA', 'IT', 'Active'),
    ('ACCT50/014', '82062096', 'Ameni', 'Ferchichi', 'ameni.ferchichi@tbs.u-tunis.tn', '59399110', '2002-12-22', 'Junior', 'MRK', 'ACCT', 'Active'),
    ('MRK99/015', '64305579', 'Ahmed', 'Ben Othman', 'ahmed.benothman@tbs.u-tunis.tn', '50971933', '2003-01-19', 'Freshman', 'MRK', 'IT', 'Active'),
    ('IT44/016', '19352979', 'Leila', 'Guedria', 'leila.guedria@tbs.u-tunis.tn', '57412645', '2004-11-04', 'Sophomore', 'IT', 'BA', 'Active'),
    ('BA41/017', '16499927', 'Yasmine', 'Kefi', 'yasmine.kefi@tbs.u-tunis.tn', '59622572', '2001-03-03', 'Senior', 'BA', 'MRK', 'Active'),
    ('ACCT23/018', '90551166', 'Nader', 'Ghribi', 'nader.ghribi@tbs.u-tunis.tn', '50060821', '1999-12-27', 'Junior', 'ACCT', NULL, 'Active'),
    ('MRK88/019', '70320027', 'Ikram', 'Zghidi', 'ikram.zghidi@tbs.u-tunis.tn', '55039220', '2000-05-25', 'Sophomore', 'MRK', 'BA', 'Active'),
    ('IT13/020', '19967877', 'Walid', 'Omrani', 'walid.omrani@tbs.u-tunis.tn', '50773258', '2005-01-06', 'Freshman', 'IT', 'MRK', 'Active'),
    ('BA55/021', '69601271', 'Sami', 'Dhaouadi', 'sami.dhaouadi@tbs.u-tunis.tn', '58044883', '2002-10-17', 'Senior', 'BA', NULL, 'Active'),
    ('ACCT77/022', '19440350', 'Sana', 'Guesmi', 'sana.guesmi@tbs.u-tunis.tn', '54810550', '2003-03-12', 'Junior', 'ACCT', 'IT', 'Active'),
    ('MRK74/023', '63825892', 'Nidhal', 'Chaari', 'nidhal.chaari@tbs.u-tunis.tn', '56216088', '2004-08-11', 'Freshman', 'MRK', 'ACCT', 'Active'),
    ('IT27/024', '11336294', 'Aicha', 'Ben Rejeb', 'aicha.benrejeb@tbs.u-tunis.tn', '59188774', '2002-01-25', 'Sophomore', 'IT', 'BA', 'Active'),
    ('BA60/025', '93977561', 'Lotfi', 'Baccar', 'lotfi.baccar@tbs.u-tunis.tn', '58581093', '2001-06-06', 'Senior', 'BA', 'MRK', 'Active'),
    ('ACCT30/026', '76431167', 'Rahma', 'Jemai', 'rahma.jemai@tbs.u-tunis.tn', '54423621', '2000-09-03', 'Junior', 'ACCT', 'MRK', 'Active'),
    ('MRK58/027', '87567484', 'Marwa', 'Bouazizi', 'marwa.bouazizi@tbs.u-tunis.tn', '59544136', '2003-04-28', 'Freshman', 'MRK', 'BA', 'Active'),
    ('IT17/028', '74319678', 'Zied', 'Jaziri', 'zied.jaziri@tbs.u-tunis.tn', '50172948', '2004-07-02', 'Sophomore', 'IT', NULL, 'Active'),
    ('BA75/029', '84108290', 'Hana', 'Belhaj', 'hana.belhaj@tbs.u-tunis.tn', '57472877', '2002-08-14', 'Senior', 'BA', 'IT', 'Active'),
    ('ACCT91/030', '92467092', 'Malek', 'Debbabi', 'malek.debbabi@tbs.u-tunis.tn', '59406750', '1999-10-23', 'Junior', 'ACCT', 'MRK', 'Active'),
    ('MRK19/031', '77680401', 'Wafa', 'Ghodhbane', 'wafa.ghodhbane@tbs.u-tunis.tn', '51239175', '2005-06-09', 'Freshman', 'MRK', 'IT', 'Active'),
    ('IT94/032', '71097822', 'Sofien', 'Mezghanni', 'sofien.mezghanni@tbs.u-tunis.tn', '55812960', '2003-02-11', 'Sophomore', 'IT', 'BA', 'Active'),
    ('BA85/033', '83324386', 'Sahar', 'Chakroun', 'sahar.chakroun@tbs.u-tunis.tn', '57461310', '2000-12-15', 'Senior', 'BA', NULL, 'Active'),
    ('ACCT70/034', '18750410', 'Jihen', 'Marzouki', 'jihen.marzouki@tbs.u-tunis.tn', '53628592', '2001-09-21', 'Junior', 'ACCT', 'IT', 'Active'),
    ('MRK90/035', '68704236', 'Islem', 'Chebbi', 'islem.chebbi@tbs.u-tunis.tn', '51440629', '2002-04-20', 'Freshman', 'MRK', 'ACCT', 'Active'),
    ('IT52/036', '97260832', 'Hatem', 'Rzig', 'hatem.rzig@tbs.u-tunis.tn', '58608462', '2004-02-05', 'Sophomore', 'IT', 'MRK', 'Active'),
    ('BA40/037', '16552092', 'Najla', 'Taktak', 'najla.taktak@tbs.u-tunis.tn', '55371892', '2001-01-11', 'Senior', 'BA', 'IT', 'Active');



INSERT INTO `E_TBS`.`student_courses` (`student_id`, `course_code`, `group_id`) VALUES
-- F.17
('ACCT22/007', 'BCOR111', 'F.17'),
('ACCT23/018', 'BCOR111', 'F.17'),
('ACCT30/026', 'BCOR111', 'F.17'),
('ACCT32/051', 'BCOR111', 'F.17'),
('ACCT50/014', 'BCOR111', 'F.17'),
('ACCT54/004', 'BCOR111', 'F.17'),
('ACCT57/010', 'BCOR111', 'F.17'),
('ACCT70/034', 'BCOR111', 'F.17'),
('ACCT77/022', 'BCOR111', 'F.17'),
('ACCT88/021', 'BCOR111', 'F.17'),
('ACCT91/030', 'BCOR111', 'F.17'),
('BA27/045', 'BCOR111', 'F.17'),
('BA40/037', 'BCOR111', 'F.17'),
('BA41/017', 'BCOR111', 'F.17'),
('BA55/021', 'BCOR111', 'F.17'),
('BA55/087', 'BCOR111', 'F.17'),
('BA60/025', 'BCOR111', 'F.17'),
('BA61/005', 'BCOR111', 'F.17'),
('BA65/002', 'BCOR111', 'F.17'),
('BA67/099', 'BCOR111', 'F.17'),

-- F.18
('BA75/029', 'BCOR111', 'F.18'),
('BA79/013', 'BCOR111', 'F.18'),
('BA85/033', 'BCOR111', 'F.18'),
('BA89/044', 'BCOR111', 'F.18'),
('BA93/008', 'BCOR111', 'F.18'),
('FIN44/078', 'BCOR111', 'F.18'),
('FIN78/065', 'BCOR111', 'F.18'),
('IT12/045', 'BCOR111', 'F.18'),
('IT13/020', 'BCOR111', 'F.18'),
('IT17/028', 'BCOR111', 'F.18'),
('IT27/024', 'BCOR111', 'F.18'),
('IT28/009', 'BCOR111', 'F.18'),
('IT44/016', 'BCOR111', 'F.18'),
('IT45/032', 'BCOR111', 'F.18'),
('IT52/036', 'BCOR111', 'F.18'),
('IT66/012', 'BCOR111', 'F.18'),
('IT71/003', 'BCOR111', 'F.18'),
('IT94/032', 'BCOR111', 'F.18'),
('IT98/033', 'BCOR111', 'F.18'),
('MRK19/031', 'BCOR111', 'F.18'),
('MRK23/056', 'BCOR111', 'F.18'),
('MRK45/011', 'BCOR111', 'F.18');

INSERT INTO `e_tbs`.`student_courses` (`student_id`, `course_code`, `group_id`) VALUES
-- Ju.BA2.1
('ACCT22/007', 'BA310', 'Ju.BA2.1'),
('ACCT23/018', 'BA310', 'Ju.BA2.1'),
('ACCT30/026', 'BA310', 'Ju.BA2.1'),
('ACCT32/051', 'BA310', 'Ju.BA2.1'),
('ACCT50/014', 'BA310', 'Ju.BA2.1'),
('ACCT54/004', 'BA310', 'Ju.BA2.1'),
('ACCT57/010', 'BA310', 'Ju.BA2.1'),
('ACCT70/034', 'BA310', 'Ju.BA2.1'),
('ACCT77/022', 'BA310', 'Ju.BA2.1'),
('ACCT88/021', 'BA310', 'Ju.BA2.1'),
('ACCT91/030', 'BA310', 'Ju.BA2.1'),
('BA27/045', 'BA310', 'Ju.BA2.1'),
('BA40/037', 'BA310', 'Ju.BA2.1'),
('BA41/017', 'BA310', 'Ju.BA2.1'),
('BA55/021', 'BA310', 'Ju.BA2.1'),
('BA55/087', 'BA310', 'Ju.BA2.1'),
('BA60/025', 'BA310', 'Ju.BA2.1'),
('BA61/005', 'BA310', 'Ju.BA2.1'),

-- Ju.BA3
('BA65/002', 'BA310', 'Ju.BA3'),
('BA67/099', 'BA310', 'Ju.BA3'),
('BA75/029', 'BA310', 'Ju.BA3'),
('BA79/013', 'BA310', 'Ju.BA3'),
('BA85/033', 'BA310', 'Ju.BA3'),
('BA89/044', 'BA310', 'Ju.BA3'),
('BA93/008', 'BA310', 'Ju.BA3'),
('FIN44/078', 'BA310', 'Ju.BA3'),
('FIN78/065', 'BA310', 'Ju.BA3'),
('IT12/045', 'BA310', 'Ju.BA3'),
('IT13/020', 'BA310', 'Ju.BA3'),
('IT17/028', 'BA310', 'Ju.BA3'),
('IT27/024', 'BA310', 'Ju.BA3'),
('IT28/009', 'BA310', 'Ju.BA3'),
('IT44/016', 'BA310', 'Ju.BA3'),

-- Ju.BA4
('IT45/032', 'BA310', 'Ju.BA4'),
('IT52/036', 'BA310', 'Ju.BA4'),
('IT66/012', 'BA310', 'Ju.BA4'),
('IT71/003', 'BA310', 'Ju.BA4'),
('IT94/032', 'BA310', 'Ju.BA4'),
('IT98/033', 'BA310', 'Ju.BA4'),
('MRK19/031', 'BA310', 'Ju.BA4'),
('MRK23/056', 'BA310', 'Ju.BA4'),
('MRK45/011', 'BA310', 'Ju.BA4'),
('MRK58/027', 'BA310', 'Ju.BA4'),
('MRK63/001', 'BA310', 'Ju.BA4'),
('MRK67/019', 'BA310', 'Ju.BA4'),
('MRK74/023', 'BA310', 'Ju.BA4'),
('MRK78/006', 'BA310', 'Ju.BA4'),
('MRK88/019', 'BA310', 'Ju.BA4'),
('MRK90/035', 'BA310', 'Ju.BA4'),
('MRK99/015', 'BA310', 'Ju.BA4');


CREATE TABLE `E_TBS`.`student_gpa` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `student_id` VARCHAR(20) NOT NULL,
  `cum_gpa` DECIMAL(3,2) NOT NULL CHECK (`cum_gpa` >= 0.00 AND `cum_gpa` <= 4.00),
  PRIMARY KEY (`id`),
  FOREIGN KEY (`student_id`) REFERENCES `students`(`student_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

INSERT INTO `E_TBS`.`student_gpa` (`student_id`, `cum_gpa`) VALUES
('ACCT22/007', 3.91),
('ACCT23/018', 2.34),
('ACCT30/026', 1.75),
('ACCT32/051', 3.66),
('ACCT50/014', 1.89),
('ACCT54/004', 3.12),
('ACCT57/010', 2.01),
('ACCT70/034', 3.83),
('ACCT77/022', 2.58),
('ACCT88/021', 3.27),
('ACCT91/030', 1.96),
('BA27/045', 2.67),
('BA40/037', 3.04),
('BA41/017', 1.59),
('BA55/021', 3.88),
('BA55/087', 2.23),
('BA60/025', 2.72),
('BA61/005', 3.35),
('BA65/002', 1.61),
('BA67/099', 3.06),
('BA75/029', 2.44),
('BA79/013', 1.87),
('BA85/033', 3.98),
('BA89/044', 2.17),
('BA93/008', 3.49),
('FIN44/078', 1.73),
('FIN78/065', 2.96),
('IT12/045', 3.39),
('IT13/020', 1.90),
('IT17/028', 3.81),
('IT27/024', 2.19),
('IT28/009', 3.53),
('IT44/016', 2.61),
('IT45/032', 1.78),
('IT52/036', 3.69),
('IT66/012', 1.50),
('IT71/003', 2.86),
('IT94/032', 2.41),
('IT98/033', 3.22),
('MRK19/031', 1.92),
('MRK23/056', 3.91),
('MRK45/011', 2.48),
('MRK58/027', 3.13),
('MRK63/001', 2.08),
('MRK67/019', 3.76),
('MRK74/023', 2.56),
('MRK78/006', 3.62),
('MRK88/019', 1.97),
('MRK90/035', 3.02),
('MRK99/015', 3.99);


CREATE TABLE `E_TBS`.`course_difficulty` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `course_code` VARCHAR(10) NOT NULL,
  `avg_last_year_grade` DECIMAL(4,2) NOT NULL, 
  `fail_rate_last_year` DECIMAL(5,2) NOT NULL,  
  PRIMARY KEY (`id`),
  FOREIGN KEY (`course_code`) REFERENCES `courses`(`course_code`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

INSERT INTO `E_TBS`.`course_difficulty` (`course_code`, `avg_last_year_grade`, `fail_rate_last_year`) VALUES
('BA310', 66.0, 28.00),   
('BA300', 69.5, 22.00),  
('BCOR111', 71.0, 12.00); 



ALTER TABLE `E_TBS`.`quiz_questions`
ADD COLUMN `question_weight`  DECIMAL(4,2) NOT NULL;

ALTER TABLE `E_TBS`.`quizzes` 
DROP COLUMN `question_weight`;

ALTER TABLE `E_TBS`.`quizzes` 
DROP COLUMN `number_of_questions`;

ALTER TABLE `E_TBS`.`quizzes`
ADD COLUMN `number_of_questions`  INT;

ALTER TABLE `E_TBS`.`quizzes` 
DROP COLUMN `quiz_type`;

ALTER TABLE `E_TBS`.`quizzes` 
DROP COLUMN `pdf_url`;

ALTER TABLE `E_TBS`.`quizzes`
ADD COLUMN `is_published`  boolean ;

ALTER TABLE `E_TBS`.`student_quiz_submissions`
DROP COLUMN `grade` ;

ALTER TABLE `E_TBS`.`student_quiz_submissions`
ADD COLUMN `grade` DECIMAL(5,2) default NULL ;