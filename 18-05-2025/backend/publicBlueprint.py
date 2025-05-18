from flask import Blueprint, request, jsonify, flash, render_template, current_app, redirect, url_for, session, abort, json
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL
import re
from datetime import time, timedelta, datetime
from .auth import login_required
import random


publicBLP = Blueprint('public', __name__)


# this is just to test the connection to the database , gonna delete it later
@publicBLP.route('/test-db', methods=['GET'])
def test_db_connection():
    try:
        # Access the mysql object from the app
        mysql = current_app.mysql

        # Create a cursor
        cursor = mysql.connection.cursor()

        # Execute a query to fetch data from the classrooms table
        cursor.execute("SELECT status FROM classrooms")

        # Fetch all rows
        classrooms = cursor.fetchall()

        # Close the cursor
        cursor.close()

        # Return the data as JSON
        return jsonify({
            "message": "Database connection successful!",
            "classrooms": classrooms
        }), 200

    except Exception as e:
        return jsonify({
            "message": "Failed to connect to the database.",
            "error": str(e)
        }), 500


@publicBLP.route('/')
def home():
    return render_template("home.html")


@publicBLP.route('/publicMap')
def publicMap():
    # Access the mysql object from the app
    mysql = current_app.mysql
    # Create a cursor
    cur = mysql.connection.cursor()
    # SQL query to get all rooms and their statuses
    cur.execute("SELECT room_id, status FROM classrooms")  # Replace 'rooms' with your actual table name
    # Fetch all results from the query
    rooms = cur.fetchall()  # This will return a list of tuples (room_id, status)

    # Create a dictionary mapping room_id to status
    room_statuses = {room[0]: room[1] for room in rooms}  # room[0] is room_id, room[1] is status

    # Close the cursor
    cur.close()

    # Pass the room statuses to the template
    return render_template("publicMap.html", room_statuses=room_statuses)


#this endpoint is to dynamicall update the room status 
@publicBLP.route('/get-room-statuses', methods=['GET'])
def get_room_statuses():
    try:
        mysql = current_app.mysql
        cur = mysql.connection.cursor()

        # SQL query to get all rooms and their statuses
        cur.execute("SELECT room_id, status FROM classrooms")

        # Fetch all results from the query
        rooms = cur.fetchall()  # This will return a list of tuples (room_id, status)

        # Create a dictionary mapping room_id to status
        room_statuses = {room[0]: room[1] for room in rooms}  # room[0] is room_id, room[1] is status

        # Close the cursor
        cur.close()

        # Return the room statuses as JSON
        return jsonify(room_statuses), 200

    except Exception as e:
        return jsonify({
            "message": "Failed to fetch room statuses.",
            "error": str(e)
        }), 500


#AUTHENTICATION ---------------------------------------------------------------------------------------------
@publicBLP.route('/signup', methods=['POST'])
def signup():
    try:
        if request.method == 'POST':
            role = request.form.get('role')
            username = request.form.get('username')
            national_id = request.form.get('national_id')
            university_email = request.form.get('university_email')
            notification_email = request.form.get('notification_email')
            phone_number = request.form.get('phone_number')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')

        if role=="student" : 
            mysql = current_app.mysql
            cur = mysql.connection.cursor()
            # Check if the national_id already has an account
            cur.execute("""
                SELECT * FROM student_users 
                WHERE student_id = (SELECT student_id FROM students WHERE national_id = %s)
            """, (national_id,))

            user = cur.fetchone() 

            if user:  
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({
                            "success": False,
                            "message": "An account with this National ID already exists!",
                            "category": "E"
                        })
                flash('An account with this National ID already exists!', 'E')
                return render_template("signup.html")
            else:
                # Check if the username already has been used
                cur.execute("""
                    SELECT username FROM student_users WHERE username = %s
                    UNION 
                    SELECT username FROM professor_users WHERE username = %s
                """, (username, username))
                existing_user = cur.fetchone()

                # Check if the national_id is enrolled in the university
                cur.execute("SELECT * FROM students WHERE national_id = %s", (national_id,))
                student_data = cur.fetchone()

                if not student_data: 
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({
                            "success": False,
                            "message": "The student with this national ID is not enrolled in TBS",
                            "category": "E"
                        })
                    flash('The student with this national ID is not enrolled in TBS', 'E')
                    return render_template("signup.html")
                elif existing_user : 
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({
                            "success": False,
                            "message": "An account with this username already exists! please choose another one",
                            "category": "E"
                        })
                    flash('An account with this username already exists! please choose another one', 'E')
                    return render_template("signup.html")
                elif len(username) < 5:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({
                            "success": False,
                            "message": "username too short! please use a relevant one using your first and last name.",
                            "category": "E"
                        })
                    flash('username too short! please use a relevant one using your first and last name.', 'E')
                    return render_template("signup.html")
                elif student_data[4] != university_email :
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({
                            "success": False,
                            "message": "University email is not compatible with this national ID! please check with administration if you forgot it.",
                            "category": "E"
                        })
                    flash('University email is not compatible with this national ID! please check with administration if you forgot it.', 'E')
                    return render_template("signup.html")
                elif phone_number and not re.match(r'^\d+$', phone_number):
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({
                            "success": False,
                            "message": "Phone number must contain only digits, or it can be left empty.",
                            "category": "E"
                        })
                    flash("Phone number must contain only digits, or it can be left empty.", 'E')
                    return render_template("signup.html")
                elif password != confirm_password :
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({
                            "success": False,
                            "message": "Passwords don\'t match.",
                            "category": "E"
                        })
                    flash('Passwords don\'t match.', 'E')
                    return render_template("signup.html")
                else:
                    #Successful submission
                    passwordHash = generate_password_hash(password, method='pbkdf2:sha256')               
                    cur.execute("""
                        INSERT INTO student_users (student_id, username,password_hash,email, notification_email, phone_number) 
                        VALUES ((SELECT student_id FROM students WHERE national_id = %s), %s, %s, %s, %s, %s)
                    """, (national_id, username, passwordHash, university_email, notification_email, phone_number))
                    # Store ALL needed data in session
                    session.update({
                        'user_id': student_data[0],       
                        'role': role,           
                        'username': username,        
                        'first_name': student_data[2],    
                        'last_name': student_data[3],     
                        'email': university_email,          
                        'notification_email': notification_email,
                        'student_level':student_data[7],
                        'major':student_data[8],
                        'minor':student_data[9]
                    })         
        else:
            mysql = current_app.mysql
            cur = mysql.connection.cursor()
            # Check if the national_id already has an account
            cur.execute("""
                SELECT * FROM professor_users 
                WHERE professor_id = (SELECT professor_id FROM professors WHERE national_id = %s)
            """, (national_id,))

            user = cur.fetchone() 

            if user:  
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({
                            "success": False,
                            "message": "An account with this National ID already exists!",
                            "category": "E"
                        })
                flash('An account with this National ID already exists!', 'E')
                return render_template("signup.html")
            else:
                # Check if the username already has been used
                cur.execute("""
                    SELECT username FROM student_users WHERE username = %s
                    UNION 
                    SELECT username FROM professor_users WHERE username = %s
                """, (username, username))
                existing_user = cur.fetchone()

                # Check if the national_id is enrolled in the university
                cur.execute("SELECT * FROM professors WHERE national_id = %s", (national_id,))
                professor_data = cur.fetchone()

                if not professor_data: 
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({
                            "success": False,
                            "message": "The professor with this national ID is not enrolled in TBS",
                            "category": "E"
                        })
                    flash('The professor with this national ID is not enrolled in TBS', 'E')
                    return render_template("signup.html")
                elif existing_user : 
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({
                            "success": False,
                            "message": "An account with this username already exists! please choose another one",
                            "category": "E"
                        })
                    flash('An account with this username already exists! please choose another one', 'E')
                    return render_template("signup.html")
                elif len(username) < 5:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({
                            "success": False,
                            "message": "username too short! please use a relevant one using your first and last name.",
                            "category": "E"
                        })
                    flash('username too short! please use a relevant one using your first and last name.', 'E')
                    return render_template("signup.html")
                elif professor_data[4] != university_email :
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({
                            "success": False,
                            "message": "University email is not compatible with this national ID! please check with administration if you forgot it.",
                            "category": "E"
                        })
                    flash('University email is not compatible with this national ID! please check with administration if you forgot it.', 'E')
                    return render_template("signup.html")
                elif phone_number and not re.match(r'^\d+$', phone_number):
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({
                            "success": False,
                            "message": "Phone number must contain only digits, or it can be left empty.",
                            "category": "E"
                        })
                    flash("Phone number must contain only digits, or it can be left empty.", 'E')
                    return render_template("signup.html")
                elif password != confirm_password :
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({
                            "success": False,
                            "message": "Passwords don\'t match.",
                            "category": "E"
                        })
                    flash('Passwords don\'t match.', 'E')
                    return render_template("signup.html")
                else:
                    #Successful submission
                    passwordHash = generate_password_hash(password, method='pbkdf2:sha256')               
                    cur.execute("""
                        INSERT INTO professor_users (professor_id, username,password_hash,email, notification_email, phone_number) 
                        VALUES ((SELECT professor_id FROM professors WHERE national_id = %s), %s, %s, %s, %s, %s)
                    """, (national_id, username, passwordHash, university_email, notification_email, phone_number))
                    # Store ALL needed data in session
                    session.update({
                        'user_id': professor_data[0],       
                        'role': role,           
                        'username': username,        
                        'first_name': professor_data[2],    
                        'last_name': professor_data[3],     
                        'email': university_email,          
                        'notification_email': notification_email,
                        'department':professor_data[7],
                        'office':professor_data[8],
                        'phone_number': phone_number
                    })  

        mysql.connection.commit()  # Save changes
        cur.close()
        if role == 'student':
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    "success": True,
                    "redirect": True,
                    "url": url_for('public.studentCourses')
                })
            flash('Your account was successfully created!', 'success')
            return redirect(url_for('public.studentCourses'))
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    "success": True,
                    "redirect": True,
                    "url": url_for('public.professorCourses')
                })
            flash('Your account was successfully created!', 'success')
            return redirect(url_for('public.professorCourses'))
        
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                "success": False,
                "message": str(e),
                "category": "E"
            }), 500
        flash(f'An error occurred: {str(e)}', 'E')
        return render_template("signup.html")


@publicBLP.route('/login', methods=['POST'])
def login():
    try:
        username = request.form.get('username')
        password = request.form.get('password')

        mysql = current_app.mysql
        cur = mysql.connection.cursor()

        # Check both student and professor tables
        cur.execute("""
            SELECT 
                'student' as role,
                su.student_id as id,
                su.username,
                su.password_hash,
                s.first_name,
                s.last_name,
                su.email as university_email,
                su.notification_email,
                s.student_level,
                s.major,
                s.minor
            FROM student_users su
            JOIN students s ON su.student_id = s.student_id
            WHERE su.username = %s
            
            UNION ALL
            
            SELECT 
                'professor' as role,
                pu.professor_id as id,
                pu.username,
                pu.password_hash,
                p.first_name,
                p.last_name,
                pu.email as university_email,
                pu.notification_email,
                p.department,
                p.office_location,
                p.phone_number
            FROM professor_users pu
            JOIN professors p ON pu.professor_id = p.professor_id
            WHERE pu.username = %s
            
            LIMIT 1
        """, (username, username))
        user = cur.fetchone()
        cur.close()

        if not user :
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    "success": False,
                    "message": "Account does not exist!",
                    "category": "E"
                })
            flash('Account does not exist!', 'E')
            return render_template("login.html")
        elif not check_password_hash(user[3], password): 
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    "success": False,
                    "message": "Wrong Password !",
                    "category": "E"
                })
            flash('Wrong Password !', 'E')
            return render_template("login.html")
        
        # Store ALL needed data in session
        if user[0] == 'professor':
            session.update({
                'user_id': user[1],          # id
                'role': user[0],             # role
                'username': user[2],         # username
                'first_name': user[4],      # first_name
                'last_name': user[5],        # last_name
                'email': user[6],           # university_email
                'notification_email': user[7],
                'department':user[8],
                'office_location':user[9],
                'phone_number':user[10]
            })
        else:
            session.update({
                'user_id': user[1],          # id
                'role': user[0],             # role
                'username': user[2],         # username
                'first_name': user[4],      # first_name
                'last_name': user[5],        # last_name
                'email': user[6],           # university_email
                'notification_email': user[7],
                'student_level':user[8],
                'major':user[9],
                'minor':user[10]
            })
        
        if session['role'] == 'student':
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    "success": True,
                    "redirect": True,
                    "url": url_for('public.studentCourses')
                })
            flash('Login successful !', 'success')
            return redirect(url_for('public.studentCourses'))
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    "success": True,
                    "redirect": True,
                    "url": url_for('public.professorCourses')
                })
            flash('Login successful !', 'success')
            return redirect(url_for('public.professorCourses'))
    
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                "success": False,
                "message": str(e),
                "category": "E"
            }), 500
        flash(f'An error occurred: {str(e)}', 'E')
        return render_template("login.html")


@publicBLP.route('/logout', methods=['POST'])  
def logout():
    session.clear()
    flash('Logged out successfully!', 'S')
    return redirect(url_for('public.home'))


#COMMON FEATURES------------------------------------------------------------------------------------------------------
@publicBLP.route('/privateMap')
@login_required
def privateMap():
    mysql = current_app.mysql
    cur = mysql.connection.cursor()

    # Get ALL classroom details (not just status)
    cur.execute("""
        SELECT 
            room_id, 
            room_name, 
            room_type, 
            capacity, 
            has_AC, 
            has_projector, 
            has_lights, 
            status
        FROM classrooms
    """)
    rooms = cur.fetchall()
    
    # Create complete room data dictionary
    room_statuses = {
        room[0]: {
            'name': room[1],
            'type': room[2],
            'capacity': room[3],
            'has_AC': str(room[4]),  # Convert to string for easy JS comparison
            'has_projector': str(room[5]),
            'has_lights': str(room[6]),
            'status': room[7]
        } for room in rooms
    }

    # [Keep your existing sessions query and processing]
    current_day = datetime.now().strftime('%A')

    cur.execute("""
        SELECT 
            s.classroom_id,
            CONCAT(p.first_name, ' ', p.last_name) as professor_name,
            c.course_name,
            cp.session_type,
            TIME(s.start_time) as start_time,
            TIME(s.end_time) as end_time,
            s.day_of_week,
            GROUP_CONCAT(DISTINCT s.group_id ORDER BY s.group_id SEPARATOR ', ') as group_list
        FROM sessions s
        JOIN course_professors cp ON s.course_professor_id = cp.id
        JOIN professors p ON cp.professor_id = p.professor_id
        JOIN courses c ON cp.course_code = c.course_code
        WHERE 
            s.day_of_week = %s  # Filter for today's day only
            AND TIME(NOW()) BETWEEN TIME(s.start_time) AND TIME(s.end_time)
        GROUP BY s.classroom_id, s.course_professor_id, s.start_time, s.end_time,
                p.first_name, p.last_name, c.course_name, cp.session_type, s.day_of_week
        ORDER BY s.start_time
    """, (current_day,)) 

    current_sessions = {}
    for session in cur.fetchall():
        classroom_id = session[0]
        if classroom_id in current_sessions:
            existing_groups = current_sessions[classroom_id]['groups']
            new_groups = session[6]
            combined_groups = f"{existing_groups}, {new_groups}" if existing_groups else new_groups
            current_sessions[classroom_id]['groups'] = combined_groups
        else:
            current_sessions[classroom_id] = {
                    'professor': session[1],
                    'course': session[2],
                    'session_type': session[3],
                    'time': f"{session[4]} to {session[5]}",
                    'day_of_week': session[6],
                    'groups': session[7],
                    'classroom_id': classroom_id  # Added for easier filtering
                }

    cur.execute("""
    SELECT 
        s.classroom_id,
        CONCAT(p.first_name, ' ', p.last_name) as professor_name,
        c.course_name,
        cp.session_type,
        s.start_time,
        s.end_time,
        s.day_of_week,
        GROUP_CONCAT(DISTINCT s.group_id ORDER BY s.group_id SEPARATOR ', ') as group_list,
        s.course_professor_id  -- Added this to properly identify unique sessions
    FROM sessions s
    JOIN course_professors cp ON s.course_professor_id = cp.id
    JOIN professors p ON cp.professor_id = p.professor_id
    JOIN courses c ON cp.course_code = c.course_code
    WHERE s.day_of_week = DAYNAME(CURDATE())
    GROUP BY s.classroom_id, s.course_professor_id, s.start_time, s.end_time,
            p.first_name, p.last_name, c.course_name, cp.session_type, s.day_of_week
    ORDER BY s.classroom_id, s.start_time
    """)

    todays_sessions = {}
    for session in cur.fetchall():
    # Create a unique session key (classroom + time + professor)
        session_key = (session[0], session[4], session[5], session[8])  # classroom_id, start_time, end_time, course_professor_id
        
        if session_key in todays_sessions:
            # Only combine groups if it's the exact same session
            existing_groups = todays_sessions[session_key]['groups']
            new_groups = session[7]  # group_list at index 7
            combined_groups = f"{existing_groups}, {new_groups}" if existing_groups else new_groups
            todays_sessions[session_key]['groups'] = combined_groups
        else:
            # New unique session
            todays_sessions[session_key] = {
                'professor': session[1],        # professor_name at index 1
                'course': session[2],           # course_name at index 2
                'session_type': session[3],    # session_type at index 3
                'time': f"{session[4]} to {session[5]}",  # formatted time
                'day_of_week': session[6],     # day_of_week at index 6
                'groups': session[7],          # group_list at index 7
                'classroom_id': session[0],    # classroom_id at index 0
                'start_time': session[4],      # start_time at index 4
                'end_time': session[5],        # end_time at index 5
                'course_professor_id': session[8]  # course_professor_id at index 8
            }
    
  
    def prepare_session_data(sessions):
        """Convert timedelta objects to strings and prepare for JSON serialization"""
        serializable_sessions = []
        for session in sessions.values():
            # Convert timedelta to string representation
            start_str = str(session['start_time']) if isinstance(session['start_time'], timedelta) else session['start_time'].strftime('%H:%M:%S')
            end_str = str(session['end_time']) if isinstance(session['end_time'], timedelta) else session['end_time'].strftime('%H:%M:%S')
            
            serializable_sessions.append({
                'classroom_id': session['classroom_id'],
                'professor': session['professor'],
                'course': session['course'],
                'session_type': session['session_type'],
                'time': f"{start_str} to {end_str}",
                'day_of_week': session['day_of_week'],
                'groups': session['groups'],
                'start': start_str,
                'end': end_str
            })
        return serializable_sessions
    cur.close()
    # In your route function:
    serialized_sessions = prepare_session_data(todays_sessions)

    return render_template("privateMap.html",
        room_statuses=room_statuses,
        current_sessions=current_sessions,
        todays_sessions=serialized_sessions
    )



#PROFESSORS FEATURES--------------------------------------------------------------------------------------------------------------
@publicBLP.route('/Pcourses')
@login_required
def professorCourses():
    # Get professor ID from Flask's session
    professor_id = session['user_id']
    
    # Get database connection
    mysql = current_app.mysql
    cur = mysql.connection.cursor()
    
    # Query to group sessions by time and classroom, concatenate group IDs
    query = """
        SELECT 
            cp.id AS course_professor_id,
            c.course_code,
            c.course_name,
            c.level,
            cp.session_type,
            s.day_of_week,
            s.start_time,
            s.end_time,
            s.classroom_id,
            GROUP_CONCAT(DISTINCT s.group_id ORDER BY s.group_id SEPARATOR ', ') AS group_list
        FROM course_professors cp
        JOIN courses c ON cp.course_code = c.course_code
        JOIN sessions s ON cp.id = s.course_professor_id
        WHERE cp.professor_id = %s
        GROUP BY 
            cp.id, c.course_code, c.course_name, c.level, cp.session_type,
            s.day_of_week, s.start_time, s.end_time, s.classroom_id
        ORDER BY c.course_name, s.day_of_week, s.start_time
    """
    
    
    cur.execute(query, (professor_id,))
    fetched_sessions = cur.fetchall()

    # Process the fetched sessions
    processed_courses = {}
    for row in fetched_sessions:
        cp_id = row[0]
        course_key = (cp_id, row[1], row[2], row[3], row[4])  # Add cp_id to course_key
        
        if course_key not in processed_courses:
            processed_courses[course_key] = {
                'course_professor_id': cp_id,
                'course_code': row[1],
                'course_name': row[2],
                'level': row[3],
                'session_type': row[4],
                'course_sessions': []
            }

        # Check if we have an existing session for the same time and classroom
        session_exists = False
        for course_session in processed_courses[course_key]['course_sessions']:
            if (course_session['day'] == row[5] and 
                course_session['start'] == str(row[6]) and 
                course_session['end'] == str(row[7]) and 
                course_session['classroom'] == row[8]):
                
                session_exists = True
                course_session['groups'] += ", " + row[9]

        # If no existing session found, add a new one
        if not session_exists:
            processed_courses[course_key]['course_sessions'].append({
                'day': row[5],
                'start': str(row[6]),
                'end': str(row[7]),
                'classroom': row[8],
                'groups': row[9] 
            })
    # Serialize before storing in session
    session['all_courses_data'] = serialize_course_data(list(processed_courses.values()))
    
    # ✅ Debug print
    print("Processed Courses Data:")
    for course in processed_courses.values():
        print(course)

    # Pass the processed data to the template
    return render_template("professorCourses.html", 
                           courses=list(processed_courses.values()),
                           professor_name=f"{session.get('first_name', '')} {session.get('last_name', '')}")



def serialize_course_data(courses):
    """Convert course data to JSON-serializable format"""
    serialized = []
    for course in courses:
        serialized.append({
            'course_professor_id': str(course['course_professor_id']),  # Add the professor id
            'course_code': str(course['course_code']),
            'course_name': str(course['course_name']),
            'level': str(course['level']),
            'session_type': str(course['session_type']),
            'course_sessions': [{
                'day': str(session['day']),
                'start': str(session['start']),
                'end': str(session['end']),
                'classroom': str(session['classroom']),
                'groups': str(session['groups'])
            } for session in course['course_sessions']]
        })
    return serialized



@publicBLP.route('/Pcourses/<course_code>/<professor_id>')
@login_required
def professorCourseDetails(course_code, professor_id):
    # Get from session storage
    all_courses = session.get('all_courses_data', [])
    
    # Find the specific course by course_code
    course = None
    for c in all_courses:
        if str(c['course_professor_id']) == str(professor_id):  # Ensure both are compared as strings or integers
            course = c
            break
    
    if not course:
        abort(404)
    
    # ✅ Debug print
    print("Selected Course Details:")
    print(course)
    
    return render_template('pCourseDetails.html', course=course)



#attendance feature
@publicBLP.route('/create-attendance', methods=['POST'])
@login_required
def create_attendance():
    try:
        # Get form data
        course_professor_id = request.form.get('course_professor_id')
        session_date = request.form.get('session_date')
        start_time = request.form.get('start_time') or None
        end_time = request.form.get('end_time') or None
        location = request.form.get('location') or None
        details = request.form.get('details', '')
        course_code = request.form.get('course_code')
        groups = request.form.get('groups', 'ALL')  # Get groups with default 'ALL'

        # Log form data for debugging
        current_app.logger.debug(f"Form data received: course_professor_id={course_professor_id}, "
                               f"session_date={session_date}, start_time={start_time}, "
                               f"end_time={end_time}, location={location}, details={details}, "
                               f"course_code={course_code}, groups={groups}")

        if not session_date:
            raise ValueError("Session date is required.")
        
        mysql = current_app.mysql
        cur = mysql.connection.cursor()

        # Insert attendance session with group_codes
        cur.execute(""" 
            INSERT INTO attendance_sessions (
                course_professor_id,
                session_date,
                start_time,
                end_time,
                location,
                details,
                attendance_csv_url,
                finalized_at,
                group_codes
            ) VALUES (%s, %s, %s, %s, %s, %s, NULL, NULL, %s)
        """, (
            course_professor_id,
            session_date,
            start_time,
            end_time,
            location,
            details,
            groups  # This will store either 'ALL' or specific group combinations
        ))

        mysql.connection.commit()
        attendance_session_id = cur.lastrowid

        flash('Attendance session created successfully!', category='S')
        return redirect(url_for('public.professorCourseDetails', course_code=course_code, professor_id=course_professor_id))

    except Exception as e:
        current_app.logger.error(f"Error creating attendance: {str(e)}")
        mysql.connection.rollback()
        flash('Failed to create attendance session. Please try again.', category='E')
        return redirect(request.referrer or url_for('public.professorCourses'))


@publicBLP.route('/get_attendance_sessions/<int:course_professor_id>', methods=['GET'])
@login_required
def get_attendance_sessions(course_professor_id):
    try:
        # Verify ownership
        mysql = current_app.mysql
        cur = mysql.connection.cursor()
        cur.execute("SELECT 1 FROM course_professors WHERE id = %s AND professor_id = %s", 
                   (course_professor_id, session['user_id']))
        
        if not cur.fetchone():
            return jsonify(success=False, message="Unauthorized"), 403

        # Get sessions (now including details and group_codes columns)
        cur.execute("""
            SELECT 
                attendance_session_id,
                DATE_FORMAT(session_date, '%%Y-%%m-%%d') as formatted_date,
                TIME_FORMAT(start_time, '%%H:%%i') as start_time,
                TIME_FORMAT(end_time, '%%H:%%i') as end_time,
                location,
                closed,
                details,
                group_codes  # <-- Added this line to include groups
            FROM attendance_sessions
            WHERE course_professor_id = %s
            ORDER BY session_date DESC, start_time DESC
        """, (course_professor_id,))
        
        sessions = [dict(zip([column[0] for column in cur.description], row)) 
                   for row in cur.fetchall()]
        
        return jsonify(success=True, sessions=sessions)
        
    except Exception as e:
        current_app.logger.error(f"Error: {str(e)}")
        return jsonify(success=False, message="Server error"), 500


@publicBLP.route('/update-attendance-session', methods=['POST'])
@login_required
def update_attendance_session():
    try:
        # Get form data
        attendance_session_id = request.form.get('attendance_session_id')
        session_date = request.form.get('session_date')
        start_time = request.form.get('start_time') or None
        end_time = request.form.get('end_time') or None
        location = request.form.get('location') or None
        details = request.form.get('details', '')
        groups = request.form.get('groups', 'ALL')  # Added groups field
        course_code = request.form.get('course_code')
        course_professor_id = request.form.get('course_professor_id')

        # Log form data for debugging
        current_app.logger.debug(f"Update form data: attendance_session_id={attendance_session_id}, "
                               f"session_date={session_date}, start_time={start_time}, "
                               f"end_time={end_time}, location={location}, details={details}, "
                               f"groups={groups}, course_code={course_code},"
                               f"course_professor_id={course_professor_id}")

        # Validate required fields
        if not attendance_session_id or not session_date:
            raise ValueError("Attendance session ID and date are required")

        # Get database connection
        mysql = current_app.mysql
        cur = mysql.connection.cursor()

        # Verify ownership
        cur.execute("""
            SELECT 1 FROM attendance_sessions AS a
            JOIN course_professors AS cp ON a.course_professor_id = cp.id
            WHERE a.attendance_session_id = %s AND cp.professor_id = %s
        """, (attendance_session_id, session['user_id']))
        
        if not cur.fetchone():
            flash('You are not authorized to update this session', category='E')
            return redirect(request.referrer or url_for('public.professorCourses'))

        # Update the session (now including group_codes)
        cur.execute("""
            UPDATE attendance_sessions
            SET session_date = %s,
                start_time = %s,
                end_time = %s,
                location = %s,
                details = %s,
                group_codes = %s
            WHERE attendance_session_id = %s
        """, (
            session_date,
            start_time,
            end_time,
            location,
            details,
            groups,  # Added groups parameter
            attendance_session_id
        ))

        mysql.connection.commit()

        flash('Attendance session updated successfully!', category='S')
        return redirect(url_for('public.professorCourseDetails', course_code=course_code, professor_id=course_professor_id))

    except Exception as e:
        current_app.logger.error(f"Error updating attendance session: {str(e)}")
        if 'mysql' in locals() and mysql.connection:
            mysql.connection.rollback()
        
        flash('Failed to update attendance session. Please try again.', category='E')
        return redirect(request.referrer or url_for('public.professorCourses'))


@publicBLP.route('/delete_attendance_session/<int:attendance_session_id>', methods=['DELETE'])
@login_required
def delete_attendance_session(attendance_session_id):
    try:
        mysql = current_app.mysql
        cur = mysql.connection.cursor()

        # 1. Verify ownership
        cur.execute("""
            SELECT cp.professor_id 
            FROM attendance_sessions AS a
            JOIN course_professors AS cp ON a.course_professor_id = cp.id
            WHERE a.attendance_session_id = %s
        """, (attendance_session_id,))
        
        result = cur.fetchone()
        
        if not result:
            flash("Session not found", category="E")
            return "", 404
            
        if result[0] != session['user_id']:
            flash("Unauthorized to delete this session", category="E")
            return "", 403

        # 2. Delete the session
        cur.execute("""
            DELETE FROM attendance_sessions 
            WHERE attendance_session_id = %s
        """, (attendance_session_id,))
        
        mysql.connection.commit()
        
        return "", 200
        
    except Exception as e:
        mysql.connection.rollback()
        current_app.logger.error(f"Delete session error: {str(e)}")
        flash("Server error while deleting session", category="E")
        return "", 500


@publicBLP.route('/close_attendance_session/<int:attendance_session_id>', methods=['POST'])
@login_required
def close_attendance_session(attendance_session_id):
    try:
        mysql = current_app.mysql
        cur = mysql.connection.cursor()

        # 1. Verify ownership
        cur.execute("""
            SELECT cp.professor_id 
            FROM attendance_sessions AS a
            JOIN course_professors AS cp ON a.course_professor_id = cp.id
            WHERE a.attendance_session_id = %s
        """, (attendance_session_id,))
        
        result = cur.fetchone()
        
        if not result:
            flash("Session not found", category="E")
            return "", 404
            
        if result[0] != session['user_id']:
            flash("Unauthorized to close this session", category="E")
            return "", 403

        # 2. Delete the session
        cur.execute("""
            UPDATE attendance_sessions
            SET closed = TRUE
            WHERE attendance_session_id = %s
        """, (attendance_session_id,))

        
        mysql.connection.commit()
        
        return "", 200
        
    except Exception as e:
        mysql.connection.rollback()
        current_app.logger.error(f"close session error: {str(e)}")
        flash("Server error while closing session", category="E")
        return "", 500


@publicBLP.route('/attendance_sheet/<int:attendance_session_id>', methods=['GET'])
@login_required
def attendance_sheet(attendance_session_id):
    try:
        mysql = current_app.mysql
        cur = mysql.connection.cursor()

        # Get finalized_at status first
        cur.execute("""
            SELECT finalized_at 
            FROM attendance_sessions 
            WHERE attendance_session_id = %s
        """, (attendance_session_id,))
        finalized_at = cur.fetchone()[0] if cur.rowcount > 0 else None
       
        cur.execute("""
            SELECT 
                s.national_id,
                s.first_name,
                s.last_name,
                a.address_of_attendance,
                a.latitude,
                a.longitude,
                a.attendance_time,
                a.comment,
                a.attendance_id  -- Added at the end to avoid breaking index-based front-end
            FROM attendance_tracking a
            JOIN students s ON a.student_id = s.student_id
            WHERE a.attendance_session_id = %s
        """, (attendance_session_id,))

        students_attendance = cur.fetchall()


        cur.execute("""
            SELECT 
                c.course_code,
                c.course_name,
                CONCAT(p.first_name, ' ', p.last_name) AS professor_name,
                s.session_date,
                s.start_time,
                s.end_time,
                s.location,
                s.details,
                s.group_codes  # <-- Added this line
            FROM attendance_sessions s
            JOIN course_professors cp ON s.course_professor_id = cp.id
            JOIN courses c ON cp.course_code = c.course_code
            JOIN professors p ON cp.professor_id = p.professor_id
            WHERE s.attendance_session_id = %s
        """, (attendance_session_id,))
        session_info = cur.fetchone()

        if not students_attendance:
            flash("No students attended this session.", category="E")


        # Step 1: Get course_professor_id from attendance_sessions
        cur.execute("""
            SELECT course_professor_id
            FROM attendance_sessions
            WHERE attendance_session_id = %s
        """, (attendance_session_id,))
        result = cur.fetchone()
        course_professor_id = result[0] if result else None

        if course_professor_id:
            # Step 2: Get course_code from course_professors
            cur.execute("""
                SELECT course_code
                FROM course_professors
                WHERE id = %s
            """, (course_professor_id,))
            result = cur.fetchone()
            course_code = result[0] if result else None

            # Step 3: Get all group_ids for this course_professor_id
            cur.execute("""
                SELECT DISTINCT group_id
                FROM sessions
                WHERE course_professor_id = %s
            """, (course_professor_id,))
            group_results = cur.fetchall()
            group_ids = [row[0] for row in group_results]

            if course_code and group_ids:
                # Step 4: Get all students in these groups for this course_code
                format_strings = ','.join(['%s'] * len(group_ids))
                query = f"""
                    SELECT st.student_id, st.national_id, st.first_name, st.last_name
                    FROM student_courses sc
                    JOIN students st ON sc.student_id = st.student_id
                    WHERE sc.course_code = %s AND sc.group_id IN ({format_strings})
                """
                cur.execute(query, (course_code, *group_ids))
                all_students_in_groups = cur.fetchall()

                # Step 5: Get list of attended student_ids
                attended_national_ids = [row[0] for row in students_attendance] 

                # Step 6: Get absentees
                students_absent = [student for student in all_students_in_groups if student[1] not in attended_national_ids]

            else:
                students_absent = []
        else:
            students_absent = []

        print("students absent :",students_absent)
        print(attendance_session_id)

        return render_template(
            'attendanceSheet.html',
            attendance_session_id=attendance_session_id, 
            students_attendance=students_attendance,
            session_info=session_info,
            students_absent=students_absent,
            is_finalized=finalized_at is not None
        )

    except Exception as e:
        current_app.logger.error(f"Error retrieving attendance data: {str(e)}")
        flash("Error loading attendance sheet", category="E")
        return redirect('/Pcourses')


@publicBLP.route('/update_attendance_comments', methods=['POST'])
@login_required
def update_attendance_comments():
    try:
        data = request.get_json()
        updates = data.get('updates', [])
        
        if not updates:
            return jsonify({'success': False, 'message': 'No updates provided'}), 400
        
        mysql = current_app.mysql
        cur = mysql.connection.cursor()
        
        # Update each comment
        for update in updates:
            cur.execute("""
                UPDATE attendance_tracking
                SET comment = %s
                WHERE attendance_id = %s
            """, (update['comment'], update['attendance_id']))
        
        mysql.connection.commit()
        return jsonify({'success': True, 'message': 'Comments updated successfully'})
        
    except Exception as e:
        current_app.logger.error(f"Error updating comments: {str(e)}")
        mysql.connection.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@publicBLP.route('/delete_attendance/<int:attendance_id>', methods=['DELETE'])
@login_required
def delete_attendance(attendance_id):
    try:
        mysql = current_app.mysql
        cur = mysql.connection.cursor()

        # Check if attendance exists first
        cur.execute("SELECT 1 FROM attendance_tracking WHERE attendance_id = %s", (attendance_id,))
        if not cur.fetchone():
            return jsonify({'success': False, 'message': 'Attendance record not found'}), 404

        # Delete the student attendance
        cur.execute("""
            DELETE FROM attendance_tracking 
            WHERE attendance_id = %s
        """, (attendance_id,))
        
        mysql.connection.commit()
        return jsonify({'success': True, 'message': 'Attendance deleted successfully'})
        
    except Exception as e:
        mysql.connection.rollback()
        current_app.logger.error(f"Delete attendance error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@publicBLP.route('/add_absent_students/<int:attendance_session_id>', methods=['POST'])
@login_required
def add_absent_students(attendance_session_id):
    try:
        data = request.get_json()
        student_ids = data.get('student_ids', [])
        
        if not student_ids:
            return jsonify({'success': False, 'message': 'No students selected'}), 400

        mysql = current_app.mysql
        cur = mysql.connection.cursor()
        
        # Insert each student with current timestamp
        for student_id in student_ids:
            cur.execute("""
                INSERT INTO attendance_tracking 
                (attendance_session_id, student_id, attendance_time)
                VALUES (%s, %s, NOW())
            """, (attendance_session_id, student_id))
        
        mysql.connection.commit()
        return jsonify({
            'success': True,
            'message': f'Successfully added {len(student_ids)} students',
            'count': len(student_ids)
        })
        
    except Exception as e:
        mysql.connection.rollback()
        current_app.logger.error(f"Error adding absent students: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@publicBLP.route('/finalize_attendance/<int:attendance_session_id>', methods=['POST'])
@login_required
def finalize_attendance(attendance_session_id):
    try:
        mysql = current_app.mysql
        cur = mysql.connection.cursor()
        
        # Check if already finalized
        cur.execute("SELECT finalized_at FROM attendance_sessions WHERE attendance_session_id = %s", (attendance_session_id,))
        result = cur.fetchone()
        
        if result and result[0]:
            flash("This session is already finalized", "error")
            return redirect(url_for('public.attendance_sheet', attendance_session_id=attendance_session_id))
        
        # Finalize the session (proper parameter passing)
        cur.execute("""
            UPDATE attendance_sessions 
            SET finalized_at = NOW()
            WHERE attendance_session_id = %s
        """, ( attendance_session_id,))  # Note the tuple
        
        mysql.connection.commit()
        flash("Attendance sheet finalized successfully", "success")
        return redirect(url_for('public.attendance_sheet', attendance_session_id=attendance_session_id))
        
    except Exception as e:
        mysql.connection.rollback()
        current_app.logger.error(f"Error finalizing attendance: {str(e)}")
        flash(f"Error finalizing attendance: {str(e)}", "error")
        return redirect(url_for('public.attendance_sheet', attendance_session_id=attendance_session_id))


@publicBLP.route('/get_attendance_analytics/<int:course_professor_id>', methods=['GET'])
@login_required
def get_attendance_analytics(course_professor_id):
    try:
        mysql = current_app.mysql
        cur = mysql.connection.cursor()
        today = datetime.now().date()
        
        # 1. Verify ownership
        cur.execute("""
            SELECT 1 FROM course_professors 
            WHERE id = %s AND professor_id = %s
        """, (course_professor_id, session['user_id']))
        if not cur.fetchone():
            return jsonify(success=False, message="Unauthorized"), 403
        
        cur.execute("""
            SELECT course_code FROM course_professors 
            WHERE id = %s
        """, (course_professor_id,))
        course_code = cur.fetchone()[0]

        #DONUT CHART DATA NEEDED --------------------------------------------------------------------------------------------------------------------------------------------------------------
        # 2. Get current semester
        cur.execute("""
            SELECT id FROM semesters 
            WHERE %s BETWEEN start_date AND end_date
        """, (today,))
        semester = cur.fetchone()
        if not semester:
            return jsonify(success=False, message="No active semester"), 400
        semester_id = semester[0]

        # 3. Get all past weeks and current week (up to today)
        cur.execute("""
            SELECT start_date, end_date FROM study_weeks
            WHERE semester_id = %s AND end_date < %s
        """, (semester_id, today))
        past_weeks = list(cur.fetchall())  

        # Check for current week (if today is inside a study week)
        cur.execute("""
            SELECT start_date, end_date FROM study_weeks
            WHERE semester_id = %s AND start_date <= %s AND end_date >= %s
        """, (semester_id, today, today))
        current_week = cur.fetchone()

        if current_week:
            past_weeks.append(current_week)  # now this is safe



        completed_weeks = len(past_weeks)

        # 4. Get professor's weekly session pattern (unique day-time combinations)
        cur.execute("""
            SELECT DISTINCT day_of_week, start_time, end_time 
            FROM sessions 
            WHERE course_professor_id = %s
        """, (course_professor_id,))
        session_patterns = cur.fetchall()

        # 5. Get all holidays in the semester
        cur.execute("""
            SELECT holiday_date FROM holidays 
            WHERE semester_id = %s
        """, (semester_id,))
        holidays = {row[0] for row in cur.fetchall()}  # Use set for fast lookup

        # 6. Calculate total expected sessions (up to today, skipping holidays)
        total_expected = 0
        holiday_dates = set()

        for week_start, week_end in past_weeks:
            for day_of_week, start_time, end_time in session_patterns:
                session_date = get_date_for_weekday(week_start, day_of_week)

                # Skip sessions beyond today
                if session_date > today:
                    continue

                # Valid date in week and not a holiday
                if week_start <= session_date <= week_end:
                    if session_date not in holidays:
                        total_expected += 1
                    else:
                        holiday_dates.add(session_date)

        # 7. Get actual attendance sessions created (past only)
        cur.execute("""
            SELECT COUNT(*) FROM attendance_sessions
            WHERE course_professor_id = %s 
            AND session_date <= %s
        """, (course_professor_id, today))
        actual_attendance = cur.fetchone()[0] or 0

        # 8. Calculate percentage and extras - RESULT FOR DONUT CHART
        percentage = min(100, round((actual_attendance / total_expected) * 100)) if total_expected > 0 else 0
        extra_sessions = max(0, actual_attendance - total_expected)

        #GAUGE CHART (SECOND VIZUALIZATION)
        # Get all attendance sessions for this course
        cur.execute("""
            SELECT attendance_session_id, group_codes, session_date 
            FROM attendance_sessions 
            WHERE course_professor_id = %s 
            AND session_date <= %s
            AND closed = 1
        """, (course_professor_id, today))
        sessions = cur.fetchall()

        total_possible_attendances = 0
        total_actual_attendances = 0
        session_details = []
        # Get all unique groups the professor teaches (from sessions)
        cur.execute("""
            SELECT DISTINCT group_id
            FROM sessions 
            WHERE course_professor_id = %s
        """, (course_professor_id,))
        group_rows = cur.fetchall()
        professor_groups = set()

        for row in group_rows:
            codes = row[0]
            if codes == 'ALL':
                continue  # We'll handle this recursively if needed, but skip now
            for g in codes.split(','):
                professor_groups.add(g.strip())

        # Now inside the session loop:
        for session_id, group_codes, session_date in sessions:
            if group_codes == 'ALL':
                groups = tuple(professor_groups)
            else:
                groups = tuple(g.strip() for g in group_codes.split(','))

            if not groups:
                student_count = 0
            else:
                format_strings = ','.join(['%s'] * len(groups))
                cur.execute(f"""
                    SELECT COUNT(DISTINCT student_id) 
                    FROM student_courses 
                    WHERE course_code = %s 
                    AND group_id IN ({format_strings})
                """, (course_code, *groups))
                student_count = cur.fetchone()[0] or 0

            # Count actual attendances
            cur.execute("""
                SELECT COUNT(DISTINCT student_id) 
                FROM attendance_tracking 
                WHERE attendance_session_id = %s
            """, (session_id,))
            attended_count = cur.fetchone()[0] or 0

            total_possible_attendances += student_count
            total_actual_attendances += attended_count

            session_details.append({
                'session_id': session_id,
                'session_date': session_date.strftime("%Y-%m-%d"),
                'group_codes': group_codes,
                'total_students': student_count,
                'attended_count': attended_count,
                'attendance_rate': round((attended_count / student_count) * 100, 2) if student_count > 0 else 0
            })


        # Calculate overall attendance rate
        overall_rate = round((total_actual_attendances / total_possible_attendances) * 100, 2) if total_possible_attendances > 0 else 0

 
        #STACKED BAR CHART DATA NEEDED
        # 1. Get all unique groups from all sessions
        all_groups = set()
        for session_o in session_details:
            if session_o['group_codes'] == 'ALL':
                all_groups.update(professor_groups)  # Use the professor_groups we already have
            else:
                all_groups.update(g.strip() for g in session_o['group_codes'].split(','))

        # 2. Initialize group stats
        group_stats = {}
        for group in all_groups:
            group_stats[group] = {
                'total_students': 0,
                'attended_sessions': 0,
                'total_attended': 0,
                'total_absences': 0
            }

        # 3. Calculate student counts per group (only need to do this once)
        for group in all_groups:
            cur.execute("""
                SELECT COUNT(DISTINCT student_id)
                FROM student_courses
                WHERE course_code = %s AND group_id = %s
            """, (course_code, group))
            group_stats[group]['total_students'] = cur.fetchone()[0] or 0

        # 4. Process each session to calculate accurate attendance per group
        for session_o in session_details:
            if session_o['group_codes'] == 'ALL':
                groups_in_session = professor_groups
            else:
                groups_in_session = [g.strip() for g in session_o['group_codes'].split(',')]

            # Get student_ids who attended this session
            cur.execute("""
                SELECT DISTINCT student_id 
                FROM attendance_tracking 
                WHERE attendance_session_id = %s
            """, (session_o['session_id'],))
            attending_students = set(row[0] for row in cur.fetchall())

            for group in groups_in_session:
                # Get students enrolled in this course and group
                cur.execute("""
                    SELECT student_id 
                    FROM student_courses 
                    WHERE course_code = %s AND group_id = %s
                """, (course_code, group))
                group_students = set(row[0] for row in cur.fetchall())

                # Intersect to find how many from this group attended
                attended_from_group = len(attending_students & group_students)

                if group in group_stats:
                    group_stats[group]['attended_sessions'] += 1
                    group_stats[group]['total_attended'] += attended_from_group
                    group_stats[group]['total_absences'] += (group_stats[group]['total_students'] - attended_from_group)

        # 5. Calculate averages and prepare final data
        group_comparison_data = []
        for group, stats in group_stats.items():
            if stats['attended_sessions'] > 0:
                avg_attended = round(stats['total_attended'] / stats['attended_sessions'], 2)
                avg_absent = round(stats['total_absences'] / stats['attended_sessions'], 2)
            else:
                avg_attended = avg_absent = 0
            
            group_comparison_data.append({
                'group_name': group,
                'total_students': stats['total_students'],
                'avg_attended': avg_attended,
                'avg_absent': avg_absent,
                'sessions_counted': stats['attended_sessions']
            })

        #TOP ATTENDEES AND ABSENTEES
        # 6. Get attendance stats per student
        student_attendance_stats = {}  # student_id -> {'attended': x, 'expected': y, 'group': z}

        for session_o in session_details:
            session_id = session_o['session_id']
            if session_o['group_codes'] == 'ALL':
                groups_in_session = professor_groups
            else:
                groups_in_session = [g.strip() for g in session_o['group_codes'].split(',')]

            # Get attending students
            cur.execute("""
                SELECT DISTINCT student_id
                FROM attendance_tracking
                WHERE attendance_session_id = %s
            """, (session_id,))
            attended_students = set(row[0] for row in cur.fetchall())

            for group in groups_in_session:
                cur.execute("""
                    SELECT student_id
                    FROM student_courses
                    WHERE course_code = %s AND group_id = %s
                """, (course_code, group))
                enrolled_students = [row[0] for row in cur.fetchall()]

                for sid in enrolled_students:
                    if sid not in student_attendance_stats:
                        student_attendance_stats[sid] = {
                            'attended': 0,
                            'expected': 0,
                            'group': group
                        }

                    student_attendance_stats[sid]['expected'] += 1
                    if sid in attended_students:
                        student_attendance_stats[sid]['attended'] += 1

        # Fetch student names and build final list
        top_students = []
        if student_attendance_stats:
            cur.execute("SELECT student_id, first_name, last_name FROM students")
            student_names = {row[0]: f"{row[1]} {row[2]}" for row in cur.fetchall()}

            for sid, stats in student_attendance_stats.items():
                full_name = student_names.get(sid, "Unknown")
                top_students.append({
                    'student_id': sid,
                    'student_name': full_name,
                    'group': stats['group'],
                    'attended_sessions': stats['attended'],
                    'expected_sessions': stats['expected'],
                    'attendance_rate': round((stats['attended'] / stats['expected']) * 100, 2) if stats['expected'] > 0 else 0
                })

        # Sort and slice
        top_attendees = sorted(top_students, key=lambda x: (-x['attended_sessions'], x['student_name']))[:5]
        top_absentees = sorted(top_students, key=lambda x: (x['attended_sessions'], x['student_name']))[:5]


        return jsonify(
            success=True,
            data={
                # Donut chart data (existing)
                'expected_sessions': total_expected,
                'actual_attendance': actual_attendance,
                'percentage': percentage,
                'weeks_up_to_today': completed_weeks,
                'holidays_count': len(holiday_dates),
                'extra_sessions': extra_sessions,
                
                # Gauge chart data (new)
                'attendance_rate': {
                    'overall_rate': overall_rate,
                    'total_students': total_possible_attendances,
                    'attended_students': total_actual_attendances,
                    'session_details': session_details  # For future use
                },
                'group_comparison': group_comparison_data,
                'top_attendees': top_attendees,
                'top_absentees': top_absentees
            }
        )
    
    except Exception as e:
        current_app.logger.error(f"Error: {str(e)}")
        return jsonify(success=False, message="Server error"), 500


# Helper function
def get_date_for_weekday(start_date, day_name):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    target_day = days.index(day_name)
    start_day = start_date.weekday()
    return start_date + timedelta(days=(target_day - start_day) % 7)



#log presence to change the classroom availability
@publicBLP.route('/log_professor_presence/<string:room_id>', methods=['POST'])
@login_required
def log_professor_presence(room_id):
    try:
        mysql = current_app.mysql
        cur = mysql.connection.cursor()

        # Optional: Validate room existence
        cur.execute("""
            SELECT room_id FROM classrooms WHERE room_id = %s
        """, (room_id,))
        if not cur.fetchone():
            flash("Classroom not found", category="E")
            return "", 404

        # Update the status to 'full'
        cur.execute("""
            UPDATE classrooms
            SET status = 'full'
            WHERE room_id = %s
        """, (room_id,))
        
        mysql.connection.commit()
        return "", 200

    except Exception as e:
        mysql.connection.rollback()
        current_app.logger.error(f"Error logging professor presence: {str(e)}")
        flash("Server error while updating classroom status", category="E")
        return "", 500


@publicBLP.route('/get_room_statuses_presence')
def get_room_statuses_presence():
    # Access the mysql object from the app
    mysql = current_app.mysql
    cur = mysql.connection.cursor()
    
    # SQL query to get all room statuses
    cur.execute("SELECT room_id, status FROM classrooms")  # Replace 'rooms' with your actual table name
    rooms = cur.fetchall()  # List of tuples (room_id, status)
    
    # Create a dictionary mapping room_id to status
    room_statuses = {room[0]: room[1] for room in rooms}
    
    # Close the cursor
    cur.close()
    
    # Return the room statuses as JSON response
    return jsonify(room_statuses)


#Schedule
@publicBLP.route('/pSchedule')
@login_required
def pSchedule():
    # Get professor ID from Flask's session
    professor_id = session['user_id']
    
    # Get database connection
    mysql = current_app.mysql
    cur = mysql.connection.cursor()
    
    # Query to group sessions by time and classroom, concatenate group IDs
    query = """
        SELECT 
            cp.id AS course_professor_id,
            c.course_code,
            c.course_name,
            c.level,
            cp.session_type,
            s.day_of_week,
            s.start_time,
            s.end_time,
            s.classroom_id,
            GROUP_CONCAT(DISTINCT s.group_id ORDER BY s.group_id SEPARATOR ', ') AS group_list
        FROM course_professors cp
        JOIN courses c ON cp.course_code = c.course_code
        JOIN sessions s ON cp.id = s.course_professor_id
        WHERE cp.professor_id = %s
        GROUP BY 
            cp.id, c.course_code, c.course_name, c.level, cp.session_type,
            s.day_of_week, s.start_time, s.end_time, s.classroom_id
        ORDER BY c.course_name, s.day_of_week, s.start_time
    """
    
    
    cur.execute(query, (professor_id,))
    fetched_sessions = cur.fetchall()

    # Process the fetched sessions
    processed_courses = {}
    for row in fetched_sessions:
        cp_id = row[0]
        course_key = (cp_id, row[1], row[2], row[3], row[4])  # Add cp_id to course_key
        
        if course_key not in processed_courses:
            processed_courses[course_key] = {
                'course_professor_id': cp_id,
                'course_code': row[1],
                'course_name': row[2],
                'level': row[3],
                'session_type': row[4],
                'course_sessions': []
            }

        # Check if we have an existing session for the same time and classroom
        session_exists = False
        for course_session in processed_courses[course_key]['course_sessions']:
            if (course_session['day'] == row[5] and 
                course_session['start'] == str(row[6]) and 
                course_session['end'] == str(row[7]) and 
                course_session['classroom'] == row[8]):
                
                session_exists = True
                course_session['groups'] += ", " + row[9]

        # If no existing session found, add a new one
        if not session_exists:
            processed_courses[course_key]['course_sessions'].append({
                'day': row[5],
                'start': str(row[6]),
                'end': str(row[7]),
                'classroom': row[8],
                'groups': row[9] 
            })
    # Serialize before storing in session
    session['all_courses_data'] = serialize_course_data(list(processed_courses.values()))
    
    # ✅ Debug print
    print("Processed Courses Data:")
    for course in processed_courses.values():
        print(course)

    # Pass the processed data to the template
    return render_template("pSchedule.html", 
                           courses=list(processed_courses.values()))


# Discussions between professors and students 
@publicBLP.route('/get_discussions/<int:course_professor_id>', methods=['GET'])
@login_required
def get_discussions(course_professor_id):
    try:
        mysql = current_app.mysql
        cur = mysql.connection.cursor()

        #  Verify professor owns the course_professor_id
        cur.execute("""
            SELECT course_code FROM course_professors 
            WHERE id = %s AND professor_id = %s
        """, (course_professor_id, session['user_id']))
        
        row = cur.fetchone()
        if not row:
            return jsonify(success=False, message="Unauthorized"), 403

        course_code = row[0]

        # Get group_ids for this course_professor_id from sessions
        cur.execute("""
            SELECT DISTINCT group_id
            FROM sessions
            WHERE course_professor_id = %s
        """, (course_professor_id,))
        group_ids = [r[0] for r in cur.fetchall()]
        if not group_ids:
            return jsonify(success=True, discussions=[], non_discussed_students=[])

        #  Get students enrolled in this course + group
        format_strings = ','.join(['%s'] * len(group_ids))
        cur.execute(f"""
            SELECT DISTINCT s.student_id, s.first_name, s.last_name
            FROM student_courses sc
            JOIN students s ON s.student_id = sc.student_id
            WHERE sc.course_code = %s AND sc.group_id IN ({format_strings})
        """, [course_code] + group_ids)

        all_students = [dict(zip(['student_id', 'first_name', 'last_name'], row)) 
                        for row in cur.fetchall()]
        all_student_ids = {s['student_id'] for s in all_students}

        # Get existing discussions
        cur.execute("""
            SELECT 
                d.discussion_id,
                d.created_at,
                s.student_id,
                s.first_name,
                s.last_name
            FROM discussions d
            JOIN students s ON d.student_id = s.student_id
            WHERE d.course_professor_id = %s
            ORDER BY d.created_at DESC
        """, (course_professor_id,))

        discussions = [dict(zip([col[0] for col in cur.description], row)) 
                       for row in cur.fetchall()]
        discussed_student_ids = {d['student_id'] for d in discussions}

        #  Compute students who didn't start discussions yet
        non_discussed_students = [
            s for s in all_students if s['student_id'] not in discussed_student_ids
        ]

        return jsonify(success=True, 
                       discussions=discussions,
                       non_discussed_students=non_discussed_students)

    except Exception as e:
        current_app.logger.error(f"Error fetching discussions: {str(e)}")
        return jsonify(success=False, message="Server error"), 500


@publicBLP.route('/get_discussion_messages/<int:discussion_id>', methods=['GET'])
@login_required
def get_discussion_messages(discussion_id):
    try:
        mysql = current_app.mysql
        cur = mysql.connection.cursor()

        # Step 1: Confirm the discussion exists and belongs to the current professor
        cur.execute("""
            SELECT 1 FROM discussions d
            JOIN course_professors cp ON d.course_professor_id = cp.id
            WHERE d.discussion_id = %s AND cp.professor_id = %s
        """, (discussion_id, session['user_id']))
        
        if not cur.fetchone():
            return jsonify(success=False, message="Unauthorized"), 403

        # Step 2: Get all messages for this discussion, ordered by time
        cur.execute("""
            SELECT 
                message_id,
                sender_id,
                sender_type,
                message,
                sent_at
            FROM discussion_messages
            WHERE discussion_id = %s
            ORDER BY sent_at ASC
        """, (discussion_id,))

        messages = [dict(zip([col[0] for col in cur.description], row))
                    for row in cur.fetchall()]

        return jsonify(success=True, messages=messages)

    except Exception as e:
        current_app.logger.error(f"Error fetching discussion messages: {str(e)}")
        return jsonify(success=False, message="Server error"), 500


@publicBLP.route('/send_message/<int:discussion_id>', methods=['POST'])
@login_required
def send_message(discussion_id):
    try:
        data = request.get_json()
        message = data.get('message')
        
        if not message:
            return jsonify(success=False, message="Message cannot be empty"), 400

        mysql = current_app.mysql
        cur = mysql.connection.cursor()

        # Verify the discussion belongs to professor
        cur.execute("""
            SELECT 1 FROM discussions d
            JOIN course_professors cp ON d.course_professor_id = cp.id
            WHERE d.discussion_id = %s AND cp.professor_id = %s
        """, (discussion_id, session['user_id']))
        
        if not cur.fetchone():
            return jsonify(success=False, message="Unauthorized"), 403

        # Insert message and return the actual timestamp
        cur.execute("""
            INSERT INTO discussion_messages (
                discussion_id, 
                sender_id, 
                sender_type, 
                message
            ) VALUES (%s, %s, 'professor', %s)
        """, (discussion_id, session['user_id'], message))
        
        # Get the actual timestamp from database
        cur.execute("""
            SELECT sent_at FROM discussion_messages 
            WHERE message_id = LAST_INSERT_ID()
        """)
        sent_at = cur.fetchone()[0]
        
        mysql.connection.commit()
        return jsonify(success=True, sent_at=sent_at)

    except Exception as e:
        current_app.logger.error(f"Error sending message: {str(e)}")
        return jsonify(success=False, message="Server error"), 500
    

@publicBLP.route('/create_discussion', methods=['POST'])
@login_required
def create_discussion():
    try:
        data = request.get_json()
        course_professor_id = data.get('course_professor_id')
        student_id = data.get('student_id')
        
        if not course_professor_id or not student_id:
            return jsonify(success=False, message="Missing required fields"), 400

        mysql = current_app.mysql
        cur = mysql.connection.cursor()

        # Verify professor owns the course_professor_id
        cur.execute("""
            SELECT 1 FROM course_professors 
            WHERE id = %s AND professor_id = %s
        """, (course_professor_id, session['user_id']))
        
        if not cur.fetchone():
            return jsonify(success=False, message="Unauthorized"), 403

        # Create new discussion
        cur.execute("""
            INSERT INTO discussions (course_professor_id, student_id)
            VALUES (%s, %s)
        """, (course_professor_id, student_id))
        
        mysql.connection.commit()
        return jsonify(success=True, discussion_id=cur.lastrowid)

    except Exception as e:
        current_app.logger.error(f"Error creating discussion: {str(e)}")
        return jsonify(success=False, message="Server error"), 500


#Announcements
@publicBLP.route('/get_announcements/<int:course_professor_id>', methods=['GET'])
@login_required
def get_announcements(course_professor_id):
    try:
        mysql = current_app.mysql
        cur = mysql.connection.cursor()

        # Step 1: Verify the professor owns this course_professor_id
        cur.execute("""
            SELECT 1 FROM course_professors 
            WHERE id = %s AND professor_id = %s
        """, (course_professor_id, session['user_id']))
        
        if not cur.fetchone():
            return jsonify(success=False, message="Unauthorized"), 403

        # Step 2: Fetch announcements
        cur.execute("""
            SELECT 
                announcement_id,
                title,
                content,
                created_at
            FROM professor_announcement
            WHERE course_professor_id = %s
            ORDER BY created_at DESC
        """, (course_professor_id,))

        announcements = [
            dict(zip([col[0] for col in cur.description], row))
            for row in cur.fetchall()
        ]

        return jsonify(success=True, announcements=announcements)

    except Exception as e:
        current_app.logger.error(f"Error fetching announcements: {str(e)}")
        return jsonify(success=False, message="Server error"), 500


@publicBLP.route('/create_announcement', methods=['POST'])
@login_required
def create_announcement():
    try:
        data = request.get_json()
        course_professor_id = data.get('course_professor_id')
        title = data.get('title')
        content = data.get('content')
        
        if not all([course_professor_id, title, content]):
            return jsonify(success=False, message="All fields are required"), 400

        mysql = current_app.mysql
        cur = mysql.connection.cursor()

        # Verify the professor owns this course_professor_id
        cur.execute("""
            SELECT 1 FROM course_professors 
            WHERE id = %s AND professor_id = %s
        """, (course_professor_id, session['user_id']))
        
        if not cur.fetchone():
            return jsonify(success=False, message="Unauthorized"), 403

        # Insert announcement (created_at will be auto-set by SQL)
        cur.execute("""
            INSERT INTO professor_announcement (
                course_professor_id,
                title,
                content
            ) VALUES (%s, %s, %s)
        """, (course_professor_id, title, content))

        # Get the newly created announcement
        cur.execute("""
            SELECT 
                announcement_id,
                title,
                content,
                created_at
            FROM professor_announcement
            WHERE announcement_id = LAST_INSERT_ID()
        """)
        
        new_announcement = dict(zip(
            [col[0] for col in cur.description], 
            cur.fetchone()
        ))

        mysql.connection.commit()
        return jsonify(success=True, announcement=new_announcement)

    except Exception as e:
        current_app.logger.error(f"Error creating announcement: {str(e)}")
        return jsonify(success=False, message="Server error"), 500


@publicBLP.route('/delete_announcement/<int:announcement_id>', methods=['DELETE'])
@login_required
def delete_announcement(announcement_id):
    try:
        mysql = current_app.mysql
        cur = mysql.connection.cursor()

        # Verify ownership before deleting
        cur.execute("""
            SELECT 1 FROM professor_announcement pa
            JOIN course_professors cp ON pa.course_professor_id = cp.id
            WHERE pa.announcement_id = %s AND cp.professor_id = %s
        """, (announcement_id, session['user_id']))

        if not cur.fetchone():
            return jsonify(success=False, message="Unauthorized or announcement not found"), 403

        # Perform delete
        cur.execute("DELETE FROM professor_announcement WHERE announcement_id = %s", (announcement_id,))
        mysql.connection.commit()

        return jsonify(success=True, message="Announcement deleted successfully")

    except Exception as e:
        current_app.logger.error(f"Error deleting announcement: {str(e)}")
        return jsonify(success=False, message="Server error"), 500


#QUIZZES
@publicBLP.route('/quizPrep/<int:course_professor_id>', methods=['GET'])
@login_required
def quizPrep(course_professor_id):
    return render_template("quizPrep.html", course_professor_id = course_professor_id)


@publicBLP.route('/createQuiz/<int:course_professor_id>', methods=['POST'])
@login_required
def createQuiz(course_professor_id):
    try:
        data = request.get_json()
        
        # Extracting main quiz details
        title = data.get('quizTitle')
        description = data.get('quizDescription')
        duration = int(data.get('quizDuration', 0))
        date = data.get('quizDate')
        start_time = data.get('quizTime')
        total_grade = float(data.get('totalGrade', 0))
        number_of_questions =  int(data.get('expectedQuestions', 0))
        questions = data.get('questions', [])

        # Validate the input
        if not all([title, description, duration, date, start_time, total_grade]) or not questions:
            return jsonify(success=False, message="All fields are required"), 400

        mysql = current_app.mysql
        cur = mysql.connection.cursor()

        # Verify the professor owns this course_professor_id
        cur.execute("""
            SELECT 1 FROM course_professors 
            WHERE id = %s AND professor_id = %s
        """, (course_professor_id, session['user_id']))
        
        if not cur.fetchone():
            return jsonify(success=False, message="Unauthorized"), 403

        # Insert the quiz
        cur.execute("""
            INSERT INTO quizzes (
                course_professor_id,
                title,
                description,
                duration,
                date,
                start_time,
                grade,
                created_at,
                number_of_questions
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), %s)
        """, (course_professor_id, title, description, duration, date, start_time, total_grade, number_of_questions))

        quiz_id = cur.lastrowid  # Get the newly created quiz ID

        # Insert the questions and choices
        for question in questions:
            question_text = question.get('questionText')
            question_weight = float(question.get('questionWeight', 0))
            choices = question.get('choices', [])

            if not question_text or not choices:
                continue

            # Insert the question
            cur.execute("""
                INSERT INTO quiz_questions (
                    quiz_id,
                    question_text,
                    question_weight
                ) VALUES (%s, %s, %s)
            """, (quiz_id, question_text, question_weight))

            question_id = cur.lastrowid  # Get the question ID

            # Insert the choices
            for choice in choices:
                choice_text = choice.get('text')
                is_correct = choice.get('isCorrect', False)

                if choice_text is None:
                    continue

                cur.execute("""
                    INSERT INTO quiz_choices (
                        question_id,
                        choice_text,
                        is_correct
                    ) VALUES (%s, %s, %s)
                """, (question_id, choice_text, is_correct))

        mysql.connection.commit()
        flash("The Quiz has been Created Successfully !", category="S")
        return jsonify(
            success=True,
            message="Quiz created successfully",
            redirect_url=f"/quizPrep/{course_professor_id}"  # Simple relative URL
        )
    
    except Exception as e:
        mysql.connection.rollback()
        current_app.logger.error(f"Error creating quiz: {str(e)}")
        return jsonify(success=False, message="Server error"), 500


@publicBLP.route('/get_quizzes/<int:course_professor_id>', methods=['GET'])
@login_required
def get_quizzes(course_professor_id):
    try:
        # Verify ownership
        mysql = current_app.mysql
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT 1 FROM course_professors 
            WHERE id = %s AND professor_id = %s
        """, (course_professor_id, session['user_id']))
        
        if not cur.fetchone():
            return jsonify(success=False, message="Unauthorized"), 403

        # Get quizzes with formatted dates/times and accurate status calculation
        cur.execute("""
            SELECT 
                quiz_id,
                title,
                description,
                duration,
                DATE_FORMAT(date, '%%Y-%%m-%%d') as formatted_date,
                TIME_FORMAT(start_time, '%%H:%%i') as formatted_start_time,
                grade,
                created_at,
                CASE 
                    WHEN finalized_at IS NOT NULL THEN 'completed'
                    WHEN CONCAT(date, ' ', start_time) <= NOW() 
                         AND CONCAT(date, ' ', ADDTIME(start_time, SEC_TO_TIME(duration*60))) >= NOW() THEN 'active'
                    WHEN CONCAT(date, ' ', ADDTIME(start_time, SEC_TO_TIME(duration*60))) < NOW() THEN 'completed'
                    ELSE 'upcoming'
                END as status
            FROM quizzes
            WHERE course_professor_id = %s
            ORDER BY date DESC, start_time DESC
        """, (course_professor_id,))
        
        quizzes = [dict(zip([column[0] for column in cur.description], row)) 
                  for row in cur.fetchall()]
        
        return jsonify(success=True, quizzes=quizzes)
        
    except Exception as e:
        current_app.logger.error(f"Error getting quizzes: {str(e)}")
        return jsonify(success=False, message="Server error"), 500


@publicBLP.route('/get_quiz_details/<int:quiz_id>', methods=['GET'])
@login_required
def get_quiz_details(quiz_id):
    try:
        mysql = current_app.mysql
        cur = mysql.connection.cursor()

        # Verify the professor owns this quiz
        cur.execute("""
            SELECT cp.professor_id 
            FROM quizzes q
            JOIN course_professors cp ON q.course_professor_id = cp.id
            WHERE q.quiz_id = %s
        """, (quiz_id,))
        
        quiz_owner = cur.fetchone()
        
        if not quiz_owner or quiz_owner[0] != session['user_id']:
            return jsonify(success=False, message="Unauthorized"), 403

        # Get basic quiz info
        cur.execute("""
            SELECT 
                quiz_id,
                title,
                description,
                duration,
                DATE_FORMAT(date, '%%Y-%%m-%%d') as formatted_date,
                TIME_FORMAT(start_time, '%%H:%%i') as formatted_start_time,
                grade as total_grade,
                number_of_questions,
                created_at,
                is_published,
                finalized_at
            FROM quizzes
            WHERE quiz_id = %s
        """, (quiz_id,))
        
        quiz_data = cur.fetchone()
        
        if not quiz_data:
            return jsonify(success=False, message="Quiz not found"), 404

        quiz = dict(zip([column[0] for column in cur.description], quiz_data))

        # Get all questions for this quiz
        cur.execute("""
            SELECT 
                question_id,
                question_text,
                question_weight
            FROM quiz_questions
            WHERE quiz_id = %s
            ORDER BY question_id
        """, (quiz_id,))
        
        questions = []
        for question_row in cur.fetchall():
            question = dict(zip(['question_id', 'question_text', 'question_weight'], question_row))
            
            # Get all choices for this question
            cur.execute("""
                SELECT 
                    choice_id,
                    choice_text,
                    is_correct
                FROM quiz_choices
                WHERE question_id = %s
                ORDER BY choice_id
            """, (question['question_id'],))
            
            choices = []
            for choice_row in cur.fetchall():
                choices.append(dict(zip(['choice_id', 'choice_text', 'is_correct'], choice_row)))
            
            question['choices'] = choices
            questions.append(question)
        
        quiz['questions'] = questions

        if quiz_data[10]:
            is_finalized = True
        else:
            is_finalized = False

        return jsonify(success=True, quiz=quiz, is_finalized=is_finalized)
        
    except Exception as e:
        current_app.logger.error(f"Error getting quiz details: {str(e)}")
        return jsonify(success=False, message="Server error"), 500


@publicBLP.route('/view_quiz/<int:quiz_id>')
@login_required
def view_quiz(quiz_id):
    # This will render the template we created earlier
    return render_template('viewQuiz.html', quiz_id=quiz_id)


@publicBLP.route('/publish_quiz/<int:quiz_id>', methods=['POST'])
@login_required
def publish_quiz(quiz_id):
    try:
        mysql = current_app.mysql
        cur = mysql.connection.cursor()

        # Verify the professor owns this quiz
        cur.execute("""
            SELECT cp.professor_id, q.is_published
            FROM quizzes q
            JOIN course_professors cp ON q.course_professor_id = cp.id
            WHERE q.quiz_id = %s
        """, (quiz_id,))
        
        result = cur.fetchone()

        # Check if the quiz exists and the professor is the owner
        if not result or result[0] != session['user_id']:
            return jsonify(success=False, message="Unauthorized"), 403

        # Toggle the publish status
        is_published = result[1]
        new_status = not is_published  # Flip the current status

        cur.execute("""
            UPDATE quizzes 
            SET is_published = %s
            WHERE quiz_id = %s
        """, (new_status, quiz_id))

        # Commit the change to make it permanent
        mysql.connection.commit()

        status_message = "Quiz published successfully" if new_status else "Quiz unpublished successfully"
        return jsonify(success=True, message=status_message)

    except Exception as e:
        mysql.connection.rollback()
        current_app.logger.error(f"Error toggling quiz publish status: {str(e)}")
        return jsonify(success=False, message="Server error"), 500


@publicBLP.route('/quiz_grades/<int:quiz_id>/<int:course_professor_id>/<string:course_code>')
@login_required
def quiz_grades(quiz_id, course_professor_id, course_code):
    return render_template('quizGradeSheet.html', quiz_id=quiz_id, course_professor_id=course_professor_id, course_code=course_code)


@publicBLP.route('/get_all_quiz_grades/<int:quiz_id>/<int:course_professor_id>/<string:course_code>', methods=['GET'])
@login_required
def get_all_quiz_grades(quiz_id, course_professor_id, course_code):
    try:
        mysql = current_app.mysql
        cur = mysql.connection.cursor()

        # Step 1: Get all group_ids for this course_professor_id
        cur.execute("""
            SELECT DISTINCT group_id
            FROM sessions
            WHERE course_professor_id = %s
        """, (course_professor_id,))
        
        group_results = cur.fetchall()
        group_ids = [row[0] for row in group_results]

        if not group_ids:
            return jsonify(success=False, message="No groups found for this course professor"), 404
        
        # Step 2: Get all students in these groups for this course_code
        format_strings = ','.join(['%s'] * len(group_ids))
        query = f"""
            SELECT st.student_id, st.national_id, st.first_name, st.last_name, sc.group_id
            FROM student_courses sc
            JOIN students st ON sc.student_id = st.student_id
            WHERE sc.course_code = %s AND sc.group_id IN ({format_strings})
        """
        cur.execute(query, (course_code, *group_ids))
        all_students = cur.fetchall()
        
        # Prepare a dictionary to track all students
        student_grades = {
            student[0]: {
                'student_id': student[0],
                'national_id': student[1],
                'first_name': student[2],
                'last_name': student[3],
                'group_id': student[4],
                'grade': 0.0,
                'note': "Did not submit"
            }
            for student in all_students
        }

        # Step 3: Get all quiz submissions
        cur.execute("""
            SELECT sqs.student_id, sqs.grade, sqs.note
            FROM student_quiz_submissions sqs
            WHERE sqs.quiz_id = %s
        """, (quiz_id,))
        
        submissions = cur.fetchall()

        # Update grades for students who actually submitted
        for submission in submissions:
            student_id, grade, note = submission
            if student_id in student_grades:
                student_grades[student_id]['grade'] = float(grade) if grade is not None else 0.0
                student_grades[student_id]['note'] = note if note else "Submitted without issues"

        # Convert to list for easier JSON formatting
        final_grades_list = list(student_grades.values())

        return jsonify(success=True, students=final_grades_list)

    except Exception as e:
        current_app.logger.error(f"Error getting all quiz grades: {str(e)}")
        return jsonify(success=False, message="Server error"), 500
    finally:
        cur.close()


@publicBLP.route('/finalize_quiz/<int:quiz_id>/<int:course_professor_id>/<string:course_code>', methods=['POST'])
@login_required
def finalize_quiz(quiz_id, course_professor_id, course_code):
    try:
        mysql = current_app.mysql
        cur = mysql.connection.cursor()
        
        # Check if already finalized
        cur.execute("SELECT finalized_at FROM quizzes WHERE quiz_id = %s", (quiz_id,))
        result = cur.fetchone()
        
        if result and result[0]:
            flash("This quiz is already finalized", "error")
            return redirect(url_for('public.quiz_grades', quiz_id=quiz_id, course_professor_id=course_professor_id,course_code=course_code))
        
        # Finalize the sheet (proper parameter passing)
        cur.execute("""
            UPDATE quizzes
            SET finalized_at = NOW()
            WHERE quiz_id = %s
        """, ( quiz_id,))  
        
        mysql.connection.commit()
        flash("Grade sheet finalized successfully", "success")
        return redirect(url_for('public.quiz_grades', quiz_id=quiz_id, course_professor_id=course_professor_id,course_code=course_code))
        
    except Exception as e:
        mysql.connection.rollback()
        current_app.logger.error(f"Error finalizing quiz: {str(e)}")
        flash(f"Error finalizing quiz: {str(e)}", "error")
        return redirect(url_for('public.quiz_grades', quiz_id=quiz_id, course_professor_id=course_professor_id,course_code=course_code))






#STUDENTS FEATURES----------------------------------------------------------------------------------------------------
@publicBLP.route('/Scourses')
@login_required
def studentCourses():
    student_id = session['user_id']
    mysql = current_app.mysql
    cur = mysql.connection.cursor()

    query = """
        SELECT 
            cp.id AS course_professor_id,
            c.course_code,
            c.course_name,
            c.level,
            cp.session_type,
            s.day_of_week,
            s.start_time,
            s.end_time,
            s.classroom_id,
            sc.group_id,
            p.first_name,
            p.last_name
        FROM student_courses sc
        JOIN sessions s ON sc.group_id = s.group_id
        JOIN course_professors cp ON s.course_professor_id = cp.id AND cp.course_code = sc.course_code
        JOIN courses c ON sc.course_code = c.course_code
        JOIN professors p ON cp.professor_id = p.professor_id
        WHERE sc.student_id = %s
        ORDER BY c.course_name, s.day_of_week, s.start_time
    """

    cur.execute(query, (student_id,))
    fetched_sessions = cur.fetchall()

    # Process the fetched sessions
    processed_courses = {}
    for row in fetched_sessions:
        cp_id = row[0]
        course_key = (cp_id, row[1], row[2], row[3], row[4])

        if course_key not in processed_courses:
            processed_courses[course_key] = {
                'course_professor_id': cp_id,
                'course_code': row[1],
                'course_name': row[2],
                'level': row[3],
                'session_type': row[4],
                'professor_name': f"{row[10]} {row[11]}",
                'course_sessions': []
            }

        processed_courses[course_key]['course_sessions'].append({
            'day': row[5],
            'start': str(row[6]),
            'end': str(row[7]),
            'classroom': row[8],
            'group': row[9]
        })

    def serialize_course_dataS(courses):
        return [
            {
                'course_professor_id': course['course_professor_id'],
                'course_code': course['course_code'],
                'course_name': course['course_name'],
                'level': course['level'],
                'session_type': course['session_type'],
                'professor_name': course.get('professor_name', ''),
                'course_sessions': course['course_sessions']
            }
            for course in courses
        ]

    session['student_courses_data'] = serialize_course_dataS(list(processed_courses.values()))


    print("🔍 [DEBUG] Processed Student Courses:")
    for course in processed_courses.values():
        print(f"📘 {course['course_code']} - {course['course_name']} ({course['session_type']})")
        print(f"   👨‍🏫 Professor: {course['professor_name']}")
        for sess in course['course_sessions']:
            print(f"   🗓️ {sess['day']} | {sess['start']} - {sess['end']} @ Room {sess['classroom']} | Group: {sess['group']}")
        print("-----------------------------------------------------")

    return render_template("studentCourses.html", 
                           courses=list(processed_courses.values()),
                           student_name=f"{session.get('first_name', '')} {session.get('last_name', '')}")


@publicBLP.route('/Scourses/<course_code>/<professor_id>')
@login_required
def studentCourseDetails(course_code, professor_id):
    #print(f"Attempting to find details for course: {course_code}, professor ID: {professor_id}")  # Debug print
    
    # Get from session storage
    all_courses = session.get('student_courses_data', [])
    
    # Debugging: print the list of courses to ensure it's correct
    #print(f"All courses: {all_courses}")
    
    # Find the specific course by course_code and course_professor_id
    course = None
    for c in all_courses:
        #print(f"Comparing course {c['course_code']} and professor {c['course_professor_id']} with passed values {course_code} and {professor_id}")
        if str(c['course_professor_id']) == str(professor_id):  # Ensure both are compared as strings or integers
            course = c
            break

    print(f"Found course: {course}")  # Debug print the found course

    if not course:
        abort(404)
    
    return render_template('sCourseDetails.html', course=course)


#Attendance
@publicBLP.route('/get_attendance_sessions_S/<int:course_professor_id>', methods=['GET'])
@login_required
def get_attendance_sessions_S(course_professor_id):
    try:
        mysql = current_app.mysql
        cur = mysql.connection.cursor()
        
        # Get the student ID (assuming it's stored in session['user_id'])
        student_id = session['user_id']
        
        # Get attendance sessions (now including group_codes column)
        cur.execute("""
            SELECT 
                attendance_session_id,
                DATE_FORMAT(session_date, '%%Y-%%m-%%d') as formatted_date,
                TIME_FORMAT(start_time, '%%H:%%i') as start_time,
                TIME_FORMAT(end_time, '%%H:%%i') as end_time,
                location,
                closed,
                details,
                group_codes  # <-- Added this column
            FROM attendance_sessions
            WHERE course_professor_id = %s
            ORDER BY session_date DESC, start_time DESC
        """, (course_professor_id,))
        
        sessions = [dict(zip([column[0] for column in cur.description], row)) 
                   for row in cur.fetchall()]
        
        # Now, for each session, check if the student is present
        for attendance_session in sessions:
            session_id = attendance_session['attendance_session_id']
            
            # Check if the student is marked as present in this session
            cur.execute("""
                SELECT 1
                FROM attendance_tracking
                WHERE attendance_session_id = %s AND student_id = %s
            """, (session_id, student_id))
            
            result = cur.fetchone()
            attendance_session['present'] = bool(result)  # If result exists, the student is present
        
        print(f"Found sessions: {sessions}")  # Debug print

        return jsonify(success=True, sessions=sessions)
        
    except Exception as e:
        current_app.logger.error(f"Error: {str(e)}")
        return jsonify(success=False, message="Server error"), 500
    

@publicBLP.route('/attend_session/<int:attendance_session_id>', methods=['POST'])
@login_required
def attend_session(attendance_session_id):
    try:
        mysql = current_app.mysql
        cur = mysql.connection.cursor()

        # Get the student ID (assuming it's stored in session['user_id'])
        student_id = session['user_id']

        # Get the latitude, longitude, and address from the request body
        data = request.get_json()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        address_of_attendance = data.get('address_of_attendance')

        # 1. Check if the session exists
        cur.execute("""
            SELECT attendance_session_id
            FROM attendance_sessions
            WHERE attendance_session_id = %s
        """, (attendance_session_id,))

        result = cur.fetchone()

        if not result:
            flash("Session not found", category="E")
            return "", 404

        # 2. Register the student for the session and save location and address
        cur.execute("""
            INSERT INTO attendance_tracking (attendance_session_id, student_id, latitude, longitude, address_of_attendance)
            VALUES (%s, %s, %s, %s, %s)
        """, (attendance_session_id, student_id, latitude, longitude, address_of_attendance))

        mysql.connection.commit()

        # Return success response
        return "", 200

    except Exception as e:
        mysql.connection.rollback()
        current_app.logger.error(f"Attend session error: {str(e)}")
        flash("Server error while attending session", category="E")
        return "", 500


#Schedule
@publicBLP.route('/sSchedule')
@login_required
def sSchedule():
    student_id = session['user_id']
    mysql = current_app.mysql
    cur = mysql.connection.cursor()

    query = """
        SELECT 
            cp.id AS course_professor_id,
            c.course_code,
            c.course_name,
            c.level,
            cp.session_type,
            s.day_of_week,
            s.start_time,
            s.end_time,
            s.classroom_id,
            sc.group_id,
            p.first_name,
            p.last_name
        FROM student_courses sc
        JOIN sessions s ON sc.group_id = s.group_id
        JOIN course_professors cp ON s.course_professor_id = cp.id AND cp.course_code = sc.course_code
        JOIN courses c ON sc.course_code = c.course_code
        JOIN professors p ON cp.professor_id = p.professor_id
        WHERE sc.student_id = %s
        ORDER BY c.course_name, s.day_of_week, s.start_time
    """

    cur.execute(query, (student_id,))
    fetched_sessions = cur.fetchall()

    # Process the fetched sessions
    processed_courses = {}
    for row in fetched_sessions:
        cp_id = row[0]
        course_key = (cp_id, row[1], row[2], row[3], row[4])

        if course_key not in processed_courses:
            processed_courses[course_key] = {
                'course_professor_id': cp_id,
                'course_code': row[1],
                'course_name': row[2],
                'level': row[3],
                'session_type': row[4],
                'professor_name': f"{row[10]} {row[11]}",
                'course_sessions': []
            }

        processed_courses[course_key]['course_sessions'].append({
            'day': row[5],
            'start': str(row[6]),
            'end': str(row[7]),
            'classroom': row[8],
            'group': row[9]
        })

    def serialize_course_dataS(courses):
        return [
            {
                'course_professor_id': course['course_professor_id'],
                'course_code': course['course_code'],
                'course_name': course['course_name'],
                'level': course['level'],
                'session_type': course['session_type'],
                'professor_name': course.get('professor_name', ''),
                'course_sessions': course['course_sessions']
            }
            for course in courses
        ]

    session['student_courses_data'] = serialize_course_dataS(list(processed_courses.values()))


    # ✅ Debug print
    print("Processed Courses Data:")
    for course in processed_courses.values():
        print(course)
        
    return render_template("sSchedule.html", 
                           courses=list(processed_courses.values()))


@publicBLP.route('/get_student_discussion_messages/<int:course_professor_id>', methods=['GET'])
@login_required
def get_student_discussion_messages(course_professor_id):
    try:
        mysql = current_app.mysql
        cur = mysql.connection.cursor()

        student_id = session['user_id']  # Assuming students are logged in with their student_id

        # Step 1: Check if a discussion exists
        cur.execute("""
            SELECT discussion_id FROM discussions
            WHERE course_professor_id = %s AND student_id = %s
        """, (course_professor_id, student_id))

        row = cur.fetchone()
        if not row:
            return jsonify(success=True, messages=[], discussion_id=None, message="No discussion started yet")

        discussion_id = row[0]

        # Step 2: Fetch messages if discussion exists
        cur.execute("""
            SELECT 
                message_id,
                sender_id,
                sender_type,
                message,
                sent_at
            FROM discussion_messages
            WHERE discussion_id = %s
            ORDER BY sent_at ASC
        """, (discussion_id,))

        messages = [dict(zip([col[0] for col in cur.description], row))
                    for row in cur.fetchall()]

        return jsonify(success=True, discussion_id=discussion_id, messages=messages)

    except Exception as e:
        current_app.logger.error(f"Error fetching student discussion messages: {str(e)}")
        return jsonify(success=False, message="Server error"), 500


@publicBLP.route('/send_student_message/<int:discussion_id>', methods=['POST'])
@login_required
def send_student_message(discussion_id):
    try:
        data = request.get_json()
        message = data.get('message')

        if not message:
            return jsonify(success=False, message="Message cannot be empty"), 400

        mysql = current_app.mysql
        cur = mysql.connection.cursor()

        #Verify the discussion belongs to the current student
        cur.execute("""
            SELECT 1 FROM discussions 
            WHERE discussion_id = %s AND student_id = %s
        """, (discussion_id, session['user_id']))

        if not cur.fetchone():
            return jsonify(success=False, message="Unauthorized"), 403

        # Insert the message
        cur.execute("""
            INSERT INTO discussion_messages (
                discussion_id,
                sender_id,
                sender_type,
                message
            ) VALUES (%s, %s, 'student', %s)
        """, (discussion_id, session['user_id'], message))

        cur.execute("""
            SELECT sent_at FROM discussion_messages 
            WHERE message_id = LAST_INSERT_ID()
        """)
        sent_at = cur.fetchone()[0]

        mysql.connection.commit()
        return jsonify(success=True, sent_at=sent_at)

    except Exception as e:
        current_app.logger.error(f"Error sending student message: {str(e)}")
        return jsonify(success=False, message="Server error"), 500


@publicBLP.route('/create_student_discussion', methods=['POST'])
@login_required
def create_student_discussion():
    try:
        data = request.get_json()
        course_professor_id = data.get('course_professor_id')
        
        if not course_professor_id:
            return jsonify(success=False, message="Course professor ID required"), 400

        mysql = current_app.mysql
        cur = mysql.connection.cursor()
        student_id = session['user_id']  # Student is always the current user

        # Check if discussion already exists
        cur.execute("""
            SELECT discussion_id FROM discussions
            WHERE course_professor_id = %s AND student_id = %s
        """, (course_professor_id, student_id))
        
        if cur.fetchone():
            return jsonify(success=False, message="Discussion already exists"), 400

        # Create new discussion
        cur.execute("""
            INSERT INTO discussions (course_professor_id, student_id)
            VALUES (%s, %s)
        """, (course_professor_id, student_id))
        
        mysql.connection.commit()
        return jsonify(success=True, discussion_id=cur.lastrowid)

    except Exception as e:
        current_app.logger.error(f"Error creating student discussion: {str(e)}")
        return jsonify(success=False, message="Server error"), 500
    

#Announcements
@publicBLP.route('/get_announcements_student/<int:course_professor_id>', methods=['GET'])
@login_required
def get_announcements_student(course_professor_id):
    try:
        mysql = current_app.mysql
        cur = mysql.connection.cursor()


        # Step 2: Fetch announcements
        cur.execute("""
            SELECT 
                announcement_id,
                title,
                content,
                created_at
            FROM professor_announcement
            WHERE course_professor_id = %s
            ORDER BY created_at DESC
        """, (course_professor_id,))

        announcements = [
            dict(zip([col[0] for col in cur.description], row))
            for row in cur.fetchall()
        ]

        return jsonify(success=True, announcements=announcements)

    except Exception as e:
        current_app.logger.error(f"Error fetching announcements: {str(e)}")
        return jsonify(success=False, message="Server error"), 500


@publicBLP.route('/get_quizzes_s/<int:course_professor_id>', methods=['GET'])
@login_required
def get_quizzes_s(course_professor_id):
    try:
        # Verify ownership
        mysql = current_app.mysql
        cur = mysql.connection.cursor()
        
        # Get quizzes with formatted dates/times and accurate status calculation
        cur.execute("""
            SELECT 
                quiz_id,
                title,
                description,
                duration,
                DATE_FORMAT(date, '%%Y-%%m-%%d') as formatted_date,
                TIME_FORMAT(start_time, '%%H:%%i') as formatted_start_time,
                grade,
                created_at,
                CASE 
                    WHEN finalized_at IS NOT NULL THEN 'completed'
                    WHEN CONCAT(date, ' ', start_time) <= NOW() 
                         AND CONCAT(date, ' ', ADDTIME(start_time, SEC_TO_TIME(duration*60))) >= NOW() THEN 'active'
                    WHEN CONCAT(date, ' ', ADDTIME(start_time, SEC_TO_TIME(duration*60))) < NOW() THEN 'completed'
                    ELSE 'upcoming'
                END as status
            FROM quizzes
            WHERE course_professor_id = %s
            ORDER BY date DESC, start_time DESC
        """, (course_professor_id,))
        
        quizzes = [dict(zip([column[0] for column in cur.description], row)) 
                  for row in cur.fetchall()]
        
        return jsonify(success=True, quizzes=quizzes)
        
    except Exception as e:
        current_app.logger.error(f"Error getting quizzes: {str(e)}")
        return jsonify(success=False, message="Server error"), 500


@publicBLP.route('/view_quiz_s/<int:quiz_id>')
@login_required
def view_quiz_s(quiz_id):
    # This will render the template we created earlier
    return render_template('sViewQuiz.html', quiz_id=quiz_id)


@publicBLP.route('/get_quiz_details_s/<int:quiz_id>', methods=['GET'])
@login_required
def get_quiz_details_s(quiz_id):
    try:
        mysql = current_app.mysql
        cur = mysql.connection.cursor()

        # Fetch quiz details, including publish status
        cur.execute("""
            SELECT 
                quiz_id,
                title,
                description,
                duration,
                DATE_FORMAT(date, '%%Y-%%m-%%d') as formatted_date,
                TIME_FORMAT(start_time, '%%H:%%i') as formatted_start_time,
                grade as total_grade,
                number_of_questions,
                created_at,
                is_published
            FROM quizzes
            WHERE quiz_id = %s
        """, (quiz_id,))
        
        quiz_data = cur.fetchone()
        
        if not quiz_data:
            return jsonify(success=False, message="Quiz not found"), 404

        # Extract publish status
        is_published = quiz_data[9]
        quiz = dict(zip([column[0] for column in cur.description], quiz_data))

        # Get all questions for this quiz
        cur.execute("""
            SELECT 
                question_id,
                question_text,
                question_weight
            FROM quiz_questions
            WHERE quiz_id = %s
            ORDER BY question_id
        """, (quiz_id,))
        
        questions = []
        for question_row in cur.fetchall():
            question = dict(zip(['question_id', 'question_text', 'question_weight'], question_row))
            
            # Get all choices for this question
            if is_published:
                # Include correct answer info if published
                cur.execute("""
                    SELECT 
                        choice_id,
                        choice_text,
                        is_correct
                    FROM quiz_choices
                    WHERE question_id = %s
                    ORDER BY choice_id
                """, (question['question_id'],))
            else:
                # Hide correct answer info if not published
                cur.execute("""
                    SELECT 
                        choice_id,
                        choice_text
                    FROM quiz_choices
                    WHERE question_id = %s
                    ORDER BY choice_id
                """, (question['question_id'],))

            choices = []
            for choice_row in cur.fetchall():
                # Include 'is_correct' only if the quiz is published
                if is_published:
                    choices.append(dict(zip(['choice_id', 'choice_text', 'is_correct'], choice_row)))
                else:
                    # Exclude 'is_correct' for unpublished quizzes
                    choices.append(dict(zip(['choice_id', 'choice_text'], choice_row)))
            
            question['choices'] = choices
            questions.append(question)
        
        quiz['questions'] = questions

        return jsonify(success=True, quiz=quiz)
        
    except Exception as e:
        current_app.logger.error(f"Error getting quiz details: {str(e)}")
        return jsonify(success=False, message="Server error"), 500


@publicBLP.route('/get_quiz_details_to_pass_quiz/<int:quiz_id>', methods=['GET'])
@login_required
def get_quiz_details_to_pass_quiz(quiz_id):
    try:
        mysql = current_app.mysql
        cur = mysql.connection.cursor()

        # Fetch quiz details, including publish status
        cur.execute("""
            SELECT 
                quiz_id,
                title,
                description,
                duration,
                DATE_FORMAT(date, '%%Y-%%m-%%d') as formatted_date,
                TIME_FORMAT(start_time, '%%H:%%i') as formatted_start_time,
                grade as total_grade,
                number_of_questions,
                created_at
            FROM quizzes
            WHERE quiz_id = %s
        """, (quiz_id,))
        
        quiz_data = cur.fetchone()
        
        if not quiz_data:
            return jsonify(success=False, message="Quiz not found"), 404

        # Convert the quiz data to a dictionary
        quiz = dict(zip([column[0] for column in cur.description], quiz_data))

        # Get all questions for this quiz
        cur.execute("""
            SELECT 
                question_id,
                question_text,
                question_weight
            FROM quiz_questions
            WHERE quiz_id = %s
        """, (quiz_id,))
        
        questions = []
        for question_row in cur.fetchall():
            question = dict(zip(['question_id', 'question_text', 'question_weight'], question_row))
            
            # Get the choices for this question
            cur.execute("""
                SELECT 
                    choice_id,
                    choice_text
                FROM quiz_choices
                WHERE question_id = %s
            """, (question['question_id'],))

            # Convert the choices to a list of dictionaries
            choices = [dict(zip(['choice_id', 'choice_text'], choice_row)) for choice_row in cur.fetchall()]

            # Shuffle the choices to randomize their order
            random.shuffle(choices)
            
            question['choices'] = choices
            questions.append(question)
        
        # Shuffle the questions to randomize their order
        random.shuffle(questions)

        # Attach the randomized questions to the quiz
        quiz['questions'] = questions

        return jsonify(success=True, quiz=quiz)
        
    except Exception as e:
        current_app.logger.error(f"Error getting quiz details: {str(e)}")
        return jsonify(success=False, message="Server error"), 500


@publicBLP.route('/pass_quiz/<int:quiz_id>')
@login_required
def pass_quiz(quiz_id):
    # This will render the template we created earlier
    return render_template('passQuiz.html', quiz_id=quiz_id, hide_navbar=True)


@publicBLP.route('/create_submission/<int:quiz_id>', methods=['POST'])
@login_required
def  create_submission(quiz_id):
    try:
        mysql = current_app.mysql
        cur = mysql.connection.cursor()

        student_id = session['user_id']
        cur.execute("""
            SELECT 
                quiz_id,
                student_id
            FROM student_quiz_submissions
            WHERE quiz_id = %s AND student_id = %s
        """, (quiz_id, student_id))
        
        submission = cur.fetchone()
        
        if submission:
            return jsonify(success=True, message="You already submitted your answers")
        else:
            cur.execute("""
            INSERT INTO student_quiz_submissions (quiz_id, student_id)
            VALUES (%s, %s)
            """, (quiz_id,student_id))
            mysql.connection.commit()
            
            return jsonify(success=True, message="Submission created successfully")
        
    except Exception as e:
        current_app.logger.error(f"Error creating submission: {str(e)}")
        return jsonify(success=False, message="Server error"), 500


@publicBLP.route('/submit_quiz_grade/<int:quiz_id>', methods=['POST'])
@login_required
def submit_quiz_grade(quiz_id):
    try:
        mysql = current_app.mysql
        student_id = session['user_id']
        
        # Get the submitted answers from request
        answers = request.json.get('answers', [])
        if not answers:
            return jsonify(success=False, message="No answers provided"), 400
        
        # Begin transaction
        cur = mysql.connection.cursor()
        
        # 1. Verify the submission exists and isn't already graded
        cur.execute("""
            SELECT submission_id, grade 
            FROM student_quiz_submissions 
            WHERE quiz_id = %s AND student_id = %s
            ORDER BY submission_id DESC
            LIMIT 1
        """, (quiz_id, student_id))
        
        submission = cur.fetchone()
        
        if not submission:
            return jsonify(success=False, message="No quiz submission found"), 404
        
        submission_id, current_grade = submission
        if current_grade is not None:
            return jsonify(success=False, message="Quiz already graded"), 400
        
        # 2. Get all questions and correct answers for this quiz
        cur.execute("""
            SELECT q.question_id, q.question_weight, 
                   GROUP_CONCAT(c.choice_id ORDER BY c.choice_id) AS correct_choices
            FROM quiz_questions q
            LEFT JOIN quiz_choices c ON q.question_id = c.question_id AND c.is_correct = 1
            WHERE q.quiz_id = %s
            GROUP BY q.question_id
        """, (quiz_id,))
        
        questions = cur.fetchall()
        if not questions:
            return jsonify(success=False, message="No questions found for this quiz"), 404
        
        # 3. Calculate the grade and increment `answered_wrong` if needed
        total_grade = 0.0
        question_results = []
        
        for question in questions:
            question_id, weight, correct_choices_str = question
            correct_choices = set(correct_choices_str.split(',')) if correct_choices_str else set()
            
            # Find student's answer for this question
            student_answer = next((a for a in answers if a['question_id'] == str(question_id)), None)
            student_choices = set(student_answer['selected_choices']) if student_answer else set()
            
            # Calculate points for this question
            if correct_choices == student_choices:
                points = float(weight)
                total_grade += points
                is_correct = True
            else:
                # Increment answered_wrong for this question
                cur.execute("""
                    UPDATE quiz_questions 
                    SET answered_wrong = answered_wrong + 1
                    WHERE question_id = %s
                """, (question_id,))
                
                points = 0.0
                is_correct = False
            
            question_results.append({
                'question_id': question_id,
                'weight': weight,
                'points_earned': points,
                'is_correct': is_correct
            })
        
        # 4. Update the submission with the final grade
        cur.execute("""
            UPDATE student_quiz_submissions 
            SET grade = %s, submitted_at = NOW()
            WHERE submission_id = %s
        """, (total_grade, submission_id))
        
        # Commit the full transaction
        mysql.connection.commit()
        
        return jsonify(
            success=True,
            message="Quiz submitted successfully",
            total_grade=total_grade,
            question_results=question_results
        )
        
    except Exception as e:
        current_app.logger.error(f"Error submitting quiz: {str(e)}")
        mysql.connection.rollback()
        return jsonify(success=False, message="Server error"), 500
    finally:
        cur.close()


@publicBLP.route('/log_fullscreen_exit', methods=['POST'])
@login_required
def log_fullscreen_exit():
    try:
        mysql = current_app.mysql
        data = request.json
        student_id = session['user_id']
        quiz_id = data.get('quizId')
        timestamp = data.get('timestamp')

        if not quiz_id:
            return jsonify(success=False, message="Quiz ID is required"), 400

        cur = mysql.connection.cursor()
        
        # Get the most recent submission for this student and quiz
        cur.execute("""
            SELECT submission_id 
            FROM student_quiz_submissions 
            WHERE quiz_id = %s AND student_id = %s
            ORDER BY submission_id DESC
            LIMIT 1
        """, (quiz_id, student_id))
        
        submission = cur.fetchone()
        
        if submission:
            submission_id = submission[0]
            # Update the note column with the fullscreen exit info
            cur.execute("""
                UPDATE student_quiz_submissions 
                SET note = CONCAT(IFNULL(note, ''), %s)
                WHERE submission_id = %s
            """, (f"Fullscreen exit detected at {timestamp}. ", submission_id))
            mysql.connection.commit()
            return jsonify(success=True, message="Fullscreen exit logged")
        else:
            return jsonify(success=False, message="No submission found"), 404
            
    except Exception as e:
        current_app.logger.error(f"Error logging fullscreen exit: {str(e)}")
        return jsonify(success=False, message="Server error"), 500
    finally:
        if 'cur' in locals():
            cur.close()


@publicBLP.route('/get_student_quiz_grade/<int:quiz_id>', methods=['GET'])
@login_required
def get_student_quiz_grade(quiz_id):
    try:
        mysql = current_app.mysql
        student_id = session['user_id']
        cur = mysql.connection.cursor()
        
        # Get the student's latest grade for the specified quiz
        cur.execute("""
            SELECT 
                COALESCE(MAX(sqs.grade), 0) AS grade,
                q.grade AS total_grade
            FROM quizzes q
            LEFT JOIN student_quiz_submissions sqs 
                ON q.quiz_id = sqs.quiz_id AND sqs.student_id = %s
            WHERE q.quiz_id = %s
            GROUP BY q.quiz_id
        """, (student_id, quiz_id))
        
        result = cur.fetchone()
        
        if result:
            grade, total_grade = result
            return jsonify(success=True, grade=grade, total_grade=total_grade)
        else:
            return jsonify(success=False, message="Quiz not found"), 404
            
    except Exception as e:
        current_app.logger.error(f"Error getting student grade: {str(e)}")
        return jsonify(success=False, message="Server error"), 500
    finally:
        cur.close()



