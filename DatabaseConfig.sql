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

CREATE TABLE `E_Tcourse_materialsBS`.`quiz_choices` (
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
