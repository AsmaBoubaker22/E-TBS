from flask import Blueprint, request, jsonify, flash, render_template, current_app, redirect, url_for, session, abort, json
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL
import re
from datetime import time, timedelta, datetime
from .auth import login_required




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
                        'notification_email': notification_email
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
                        'notification_email': notification_email
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
                su.notification_email
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
                pu.notification_email
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
        session.update({
            'user_id': user[1],          # id
            'role': user[0],             # role
            'username': user[2],         # username
            'first_name': user[4],      # first_name
            'last_name': user[5],        # last_name
            'email': user[6],           # university_email
            'notification_email': user[7]
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
    #print("Processed Courses Data:")
    #for course in processed_courses.values():
    #    print(course)

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
    #print("Selected Course Details:")
    #print(course)
    
    return render_template('pCourseDetails.html', course=course)



@publicBLP.route('/create-attendance', methods=['POST'])
@login_required
def create_attendance():
    try:
        # Get form data
        course_professor_id = request.form.get('course_professor_id')
        session_date = request.form.get('session_date')
        start_time = request.form.get('start_time') or None  # default to None if missing
        end_time = request.form.get('end_time') or None      # default to None if missing
        location = request.form.get('location') or None      # default to None if missing
        details = request.form.get('details', '')            # default to empty string if missing
        course_code = request.form.get('course_code')        # Get the course code from the form

        # Log form data for debugging
        current_app.logger.debug(f"Form data received: course_professor_id={course_professor_id}, "
                                 f"session_date={session_date}, start_time={start_time}, "
                                 f"end_time={end_time}, location={location}, details={details}, "
                                 f"course_code={course_code}")

        # Ensure session_date is valid
        if not session_date:
            raise ValueError("Session date is required.")
        
        # Get database connection
        mysql = current_app.mysql
        cur = mysql.connection.cursor()

        # Insert attendance session
        cur.execute(""" 
            INSERT INTO attendance_sessions (
                course_professor_id,
                session_date,
                start_time,
                end_time,
                location,
                details,
                attendance_csv_url,
                finalized_at
            ) VALUES (%s, %s, %s, %s, %s, %s, NULL, NULL)
        """, (
            course_professor_id,
            session_date,
            start_time,
            end_time,
            location,
            details
        ))

        mysql.connection.commit()
        attendance_session_id = cur.lastrowid

        # Flash a success message and redirect to the course details page using course_code
        flash('Attendance session created successfully!', category='S')
        
        # Redirect back to the course details page using the course_code
        return redirect(url_for('public.professorCourseDetails', course_code=course_code, professor_id=course_professor_id))

    except Exception as e:
        # Log the exception to get more details
        current_app.logger.error(f"Error creating attendance: {str(e)}")
        
        # Rollback in case of error
        mysql.connection.rollback()
        
        # Flash an error message and redirect back to the professor's courses
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

        # Get sessions (now including details column)
        cur.execute("""
            SELECT 
                attendance_session_id,
                DATE_FORMAT(session_date, '%%Y-%%m-%%d') as formatted_date,
                TIME_FORMAT(start_time, '%%H:%%i') as start_time,
                TIME_FORMAT(end_time, '%%H:%%i') as end_time,
                location,
                closed,
                details  # <-- Added this line
            FROM attendance_sessions
            WHERE course_professor_id = %s
            ORDER BY session_date DESC, start_time DESC
        """, (course_professor_id,))
        
        sessions = [dict(zip([column[0] for column in cur.description], row)) 
                   for row in cur.fetchall()]
        
        # ✅ Debug print
        #print("Processed sessions Data:")
        #print(sessions)
        
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
        course_code = request.form.get('course_code')
        course_professor_id = request.form.get('course_professor_id')  # For redirect

        # Log form data for debugging
        current_app.logger.debug(f"Update form data: attendance_session_id={attendance_session_id}, "
                               f"session_date={session_date}, start_time={start_time}, "
                               f"end_time={end_time}, location={location}, details={details}, "
                               f"course_code={course_code},"
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

        # Update the session
        cur.execute("""
            UPDATE attendance_sessions
            SET session_date = %s,
                start_time = %s,
                end_time = %s,
                location = %s,
                details = %s
            WHERE attendance_session_id = %s
        """, (
            session_date,
            start_time,
            end_time,
            location,
            details,
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

       
        cur.execute("""
            SELECT 
                s.national_id,
                s.first_name,
                s.last_name,
                a.address_of_attendance,
                a.latitude,
                a.longitude,
                a.attendance_time,
                a.comment
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
                s.details
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

        return render_template(
            'attendanceSheet.html',
            students_attendance=students_attendance,
            session_info=session_info,
            students_absent=students_absent
        )

    except Exception as e:
        current_app.logger.error(f"Error retrieving attendance data: {str(e)}")
        flash("Error loading attendance sheet", category="E")
        return redirect('/Pcourses')



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


    #print("🔍 [DEBUG] Processed Student Courses:")
    #for course in processed_courses.values():
    #    print(f"📘 {course['course_code']} - {course['course_name']} ({course['session_type']})")
    #    print(f"   👨‍🏫 Professor: {course['professor_name']}")
    #    for sess in course['course_sessions']:
    #        print(f"   🗓️ {sess['day']} | {sess['start']} - {sess['end']} @ Room {sess['classroom']} | Group: {sess['group']}")
    #    print("-----------------------------------------------------")

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

    #print(f"Found course: {course}")  # Debug print the found course

    if not course:
        abort(404)
    
    return render_template('sCourseDetails.html', course=course)


@publicBLP.route('/get_attendance_sessions_S/<int:course_professor_id>', methods=['GET'])
@login_required
def get_attendance_sessions_S(course_professor_id):
    try:
        mysql = current_app.mysql
        cur = mysql.connection.cursor()
        
        # Get the student ID (assuming it's stored in session['user_id'])
        student_id = session['user_id']
        
        # Get attendance sessions (now including details column)
        cur.execute("""
            SELECT 
                attendance_session_id,
                DATE_FORMAT(session_date, '%%Y-%%m-%%d') as formatted_date,
                TIME_FORMAT(start_time, '%%H:%%i') as start_time,
                TIME_FORMAT(end_time, '%%H:%%i') as end_time,
                location,
                closed,
                details
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
        
        print(f"Found course: {sessions}")  

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
