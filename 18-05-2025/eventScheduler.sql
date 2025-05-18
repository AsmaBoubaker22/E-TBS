SHOW VARIABLES LIKE 'event_scheduler';
SHOW EVENTS FROM E_TBS;

DELIMITER $$

CREATE EVENT update_classroom_status
ON SCHEDULE EVERY 1 MINUTE
DO
BEGIN
    UPDATE `E_TBS`.`classrooms` c
    JOIN `E_TBS`.`sessions` s ON c.room_id = s.classroom_id
    SET c.status = 
        CASE 
            WHEN TIME(NOW()) BETWEEN s.start_time AND ADDTIME(s.start_time, '00:30:00') THEN 'waiting'
            WHEN TIME(NOW()) > ADDTIME(s.start_time, '00:30:00') AND TIME(NOW()) < s.end_time THEN 'full'
            ELSE 'empty'
        END
    WHERE s.day_of_week = DAYNAME(NOW());
END $$

DELIMITER ;

ALTER EVENT `E_TBS`.`update_classroom_status`
DO
UPDATE `E_TBS`.`classrooms` c
LEFT JOIN `E_TBS`.`sessions` s 
ON c.room_id = s.classroom_id AND s.day_of_week = DAYNAME(NOW())
SET c.status = 
    CASE 
        WHEN c.status = 'unavailable' THEN 'unavailable'  
        WHEN s.classroom_id IS NULL THEN 'empty'  
        WHEN TIME(NOW()) BETWEEN s.start_time AND ADDTIME(s.start_time, '00:30:00') THEN 'waiting'
        WHEN TIME(NOW()) > ADDTIME(s.start_time, '00:30:00') AND TIME(NOW()) < s.end_time THEN 'full'
        ELSE 'empty'
    END;


-- this is to correct the ordering by id
ALTER EVENT `E_TBS`.`update_classroom_status`
DO
UPDATE `E_TBS`.`classrooms` c
LEFT JOIN (
    SELECT 
        classroom_id,
        start_time,
        end_time,
        -- Add other fields you might need
        ROW_NUMBER() OVER (
            PARTITION BY classroom_id 
            ORDER BY 
                CASE 
                    WHEN TIME(NOW()) BETWEEN start_time AND end_time THEN 0
                    WHEN TIME(NOW()) < start_time THEN 1
                    ELSE 2
                END,
                start_time DESC
        ) as session_priority
    FROM `E_TBS`.`sessions`
    WHERE day_of_week = DAYNAME(NOW())
) s ON c.room_id = s.classroom_id AND s.session_priority = 1
SET c.status = 
    CASE 
        WHEN c.status = 'unavailable' THEN 'unavailable'  
        WHEN s.classroom_id IS NULL THEN 'empty'  
        WHEN c.status = 'full' AND TIME(NOW()) < s.end_time THEN 'full'  -- 🔒 don't override full
        WHEN TIME(NOW()) BETWEEN s.start_time AND ADDTIME(s.start_time, '01:00:00') THEN 'waiting'
        WHEN TIME(NOW()) > ADDTIME(s.start_time, '01:00:00') AND TIME(NOW()) < s.end_time THEN 'full'
        ELSE 'empty'
    END;

    
  DELIMITER //

CREATE PROCEDURE `E_TBS`.update_classroom_status_proc()
BEGIN
    UPDATE `E_TBS`.`classrooms` c
    LEFT JOIN (
        SELECT 
            classroom_id,
            start_time,
            end_time,
            ROW_NUMBER() OVER (
                PARTITION BY classroom_id 
                ORDER BY 
                    CASE 
                        WHEN TIME(NOW()) BETWEEN start_time AND end_time THEN 0
                        WHEN TIME(NOW()) < start_time THEN 1
                        ELSE 2
                    END,
                    start_time DESC
            ) AS session_priority
        FROM `E_TBS`.`sessions`
        WHERE day_of_week = DAYNAME(NOW())
    ) s ON c.room_id = s.classroom_id AND s.session_priority = 1
    SET c.status = 
        CASE 
            WHEN c.status = 'unavailable' THEN 'unavailable'
            WHEN s.classroom_id IS NULL THEN 'empty'
            WHEN c.status = 'full' AND TIME(NOW()) < s.end_time THEN 'full'
            WHEN TIME(NOW()) BETWEEN s.start_time AND ADDTIME(s.start_time, '01:00:00') THEN 'waiting'
            WHEN TIME(NOW()) > ADDTIME(s.start_time, '01:00:00') AND TIME(NOW()) < s.end_time THEN 'full'
            ELSE 'empty'
        END;
END //

DELIMITER ;

ALTER EVENT `E_TBS`.`update_classroom_status`
DO
CALL update_classroom_status_proc();
