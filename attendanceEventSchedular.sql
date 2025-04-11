SHOW VARIABLES LIKE 'event_scheduler';
SHOW EVENTS FROM E_TBS;
DELIMITER $$

CREATE EVENT IF NOT EXISTS `E_TBS`.auto_close_attendance
ON SCHEDULE EVERY 1 MINUTE
COMMENT 'Automatically closes past attendance sessions'
DO
BEGIN
    -- Update sessions from previous days
    UPDATE `E_TBS`.`attendance_sessions` a
    SET a.closed = TRUE
    WHERE a.session_date < CURDATE()
    AND a.closed = FALSE
    AND a.attendance_session_id > 0;
    
    -- Update sessions from today that have ended
    UPDATE `E_TBS`.`attendance_sessions` a
    SET a.closed = TRUE
    WHERE a.session_date = CURDATE()
    AND TIME(NOW()) > a.end_time
    AND a.closed = FALSE
    AND a.attendance_session_id > 0;
    
    -- Optional: Log the operation (ensure system_logs table exists)
    INSERT INTO `E_TBS`.`system_logs` (event, description) 
    VALUES ('auto_close_attendance', CONCAT('Closed sessions at ', NOW()));
END$$

DELIMITER ;

