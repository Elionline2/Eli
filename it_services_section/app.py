from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from datetime import datetime
import time

# === Load environment variables ===
load_dotenv('it_services_section/manage.env')

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')  # Use environment variable for secret key

# === File Upload Configuration ===
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {
    # Document files
    'txt', 'doc', 'docx', 'pdf', 'rtf', 'odt', 'pages',
    # Image files
    'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'svg',
    # Spreadsheet files
    'xls', 'xlsx', 'csv', 'ods', 'numbers',
    # Presentation files
    'ppt', 'pptx', 'key', 'odp',
    # Archive files
    'zip', 'rar', '7z', 'tar', 'gz'
}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# === Mail Configuration ===
app.config.update(
    MAIL_SERVER=os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
    MAIL_PORT=int(os.getenv('MAIL_PORT', '587')),
    MAIL_USE_TLS=os.getenv('MAIL_USE_TLS', 'True').lower() == 'true',
    MAIL_USE_SSL=os.getenv('MAIL_USE_SSL', 'False').lower() == 'true',
    MAIL_USERNAME=os.getenv('EMAIL_USER'),
    MAIL_PASSWORD=os.getenv('EMAIL_PASS'),
    MAIL_DEFAULT_SENDER=os.getenv('EMAIL_USER'),
    MAIL_MAX_EMAILS=None,
    MAIL_ASCII_ATTACHMENTS=False,
    MAIL_DEBUG=os.getenv('FLASK_ENV') == 'development'
)

# Initialize mail
mail = Mail(app)  # Initialize mail with the app instance
s = URLSafeTimedSerializer(app.secret_key)

# Debug mail configuration
if os.getenv('FLASK_ENV') == 'development':
    print("Mail Configuration:")
    print(f"MAIL_SERVER: {app.config['MAIL_SERVER']}")
    print(f"MAIL_PORT: {app.config['MAIL_PORT']}")
    print(f"MAIL_USE_TLS: {app.config['MAIL_USE_TLS']}")
    print(f"MAIL_USE_SSL: {app.config['MAIL_USE_SSL']}")
    print(f"MAIL_USERNAME: {app.config['MAIL_USERNAME']}")
    print(f"MAIL_PASSWORD: {'*' * len(app.config['MAIL_PASSWORD']) if app.config['MAIL_PASSWORD'] else 'Not set'}")
    print(f"MAIL_DEFAULT_SENDER: {app.config['MAIL_DEFAULT_SENDER']}")

# === Admin Credentials ===
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@site.com')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')

# === Create database directory if not exists ===
os.makedirs('database', exist_ok=True)

# === Initialize SQLite DB ===
def init_db():
    conn = sqlite3.connect('database/users.db')
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        firstname TEXT,
        lastname TEXT,
        gender TEXT,
        email TEXT UNIQUE,
        password TEXT
    )""")
    
    # ✅ Add this for services
    c.execute("""CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        price TEXT,
        photo TEXT
    )""")
    
    # Add KRA registrations table
    c.execute("""CREATE TABLE IF NOT EXISTS kra_registrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        fullname TEXT,
        dob TEXT,
        id_number TEXT,
        county TEXT,
        town TEXT,
        po_box TEXT,
        email TEXT,
        phone TEXT,
        transaction_code TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )""")
    
    # Add typesetting requests table
    c.execute("""CREATE TABLE IF NOT EXISTS typesetting_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        fullname TEXT,
        email TEXT,
        phone TEXT,
        document_type TEXT,
        document_file TEXT,
        transaction_code TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )""")
    
    # Add photo column if it doesn't exist
    try:
        c.execute("ALTER TABLE services ADD COLUMN photo TEXT")
    except sqlite3.OperationalError:
        # Column already exists
        pass
    
    conn.commit()
    conn.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

init_db()

# === Routes ===

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/terms')
def terms():
    return render_template('terms.html', now=datetime.now())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect('database/users.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE email=?', (email,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[5], password):
            session['user'] = user[0]
            flash('Login successful ✅', 'success')
            return redirect('/dashboard')
        else:
            flash('Invalid email or password', 'danger')
            return redirect('/login')
    return render_template('login.html')

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if 'admin' in session:
        return redirect('/admin-dashboard')

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session['admin'] = True
            flash('Welcome Admin 👑', 'success')
            return redirect('/admin-dashboard')
        else:
            flash('Invalid admin credentials ❌', 'danger')
            return redirect('/admin-login')
    return render_template('admin_login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        if request.form['password'] != request.form['confirm_password']:
            flash('Passwords do not match ❌', 'danger')
            return redirect('/signup')

        hashed_password = generate_password_hash(request.form['password'])
        data = (
            request.form['firstname'],
            request.form['lastname'],
            request.form['gender'],
            request.form['email'],
            hashed_password
        )

        conn = sqlite3.connect('database/users.db')
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (firstname, lastname, gender, email, password) VALUES (?, ?, ?, ?, ?)', data)
            conn.commit()
            flash('Account created successfully! 🎉 Please log in.', 'success')
            return redirect('/login')
        except sqlite3.IntegrityError:
            flash('Email already registered ❌', 'danger')
        finally:
            conn.close()
    return render_template('signup.html')

@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        if not email:
            flash('Please enter your email address.', 'warning')
            return redirect('/forgot')

        # Debug: Check mail configuration
        if not app.config['MAIL_USERNAME']:
            app.logger.error('MAIL_USERNAME not configured')
            flash('Email service not configured (MAIL_USERNAME missing)', 'danger')
            return redirect('/forgot')
            
        if not app.config['MAIL_PASSWORD']:
            app.logger.error('MAIL_PASSWORD not configured')
            flash('Email service not configured (MAIL_PASSWORD missing)', 'danger')
            return redirect('/forgot')

        conn = sqlite3.connect('database/users.db')
        c = conn.cursor()
        try:
            c.execute('SELECT * FROM users WHERE LOWER(email)=?', (email,))
            user = c.fetchone()
            
            if user:
                try:
                    # Generate token with user ID and timestamp
                    token_data = {'user_id': user[0], 'email': email, 'timestamp': time.time()}
                    token = s.dumps(token_data, salt='email-reset')
                    reset_url = url_for('reset_password', token=token, _external=True)
                    
                    # Debug: Print email configuration
                    app.logger.info(f'Attempting to send email to {email}')
                    app.logger.info(f'MAIL_USERNAME: {app.config["MAIL_USERNAME"]}')
                    app.logger.info(f'MAIL_SERVER: {app.config["MAIL_SERVER"]}')
                    app.logger.info(f'MAIL_PORT: {app.config["MAIL_PORT"]}')
                    
                    msg = Message('Reset Your Password',
                                sender=app.config['MAIL_DEFAULT_SENDER'],
                                recipients=[email])
                    msg.body = f'''Hi {user[1]},

Someone requested a password reset for your account. If this was you, click the link below to reset your password:

{reset_url}

This link will expire in 1 hour.

If you did not request this reset, please ignore this email and make sure you can still login to your account.

Best regards,
ELI Online Support Team'''
                    
                    mail.send(msg)
                    app.logger.info('Reset email sent successfully')
                    flash('Reset instructions sent to your email! Please check your inbox and spam folder.', 'success')
                except Exception as e:
                    app.logger.error(f'Email error: {str(e)}')
                    flash(f'Unable to send reset email: {str(e)}. Please make sure email configuration is correct.', 'danger')
            else:
                # Still show the same message even if email not found (security through obscurity)
                flash('If your email is registered, you will receive reset instructions shortly.', 'info')
            
        except sqlite3.Error as e:
            app.logger.error(f'Database error in forgot password: {str(e)}')
            flash('An error occurred. Please try again later.', 'danger')
        finally:
            conn.close()
        
        return redirect('/forgot')
    return render_template('forgot.html')

@app.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        token_data = s.loads(token, salt='email-reset', max_age=3600)  # 1 hour expiry
        
        # Validate token data structure
        if not isinstance(token_data, dict) or 'user_id' not in token_data or 'email' not in token_data:
            raise ValueError('Invalid token structure')
        
        # Check if token is too old (optional additional check)
        if time.time() - token_data['timestamp'] > 3600:
            raise ValueError('Token has expired')
        
        user_id = token_data['user_id']
        email = token_data['email']
        
    except Exception as e:
        app.logger.warning(f'Invalid reset attempt with token: {str(e)}')
        flash('The reset link is invalid or has expired. Please request a new one.', 'danger')
        return redirect('/forgot')

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        
        # Validate password strength
        if len(password) < 8:
            flash('Password must be at least 8 characters long', 'warning')
            return redirect(request.url)
            
        if password != confirm:
            flash('Passwords do not match ❌', 'warning')
            return redirect(request.url)

        try:
            conn = sqlite3.connect('database/users.db')
            c = conn.cursor()
            
            # Verify user still exists
            c.execute('SELECT * FROM users WHERE id=? AND LOWER(email)=?', (user_id, email.lower()))
            user = c.fetchone()
            
            if not user:
                flash('Account no longer exists', 'danger')
                return redirect('/forgot')
            
            # Update password with new hash
            hashed = generate_password_hash(password)
            c.execute("UPDATE users SET password = ? WHERE id = ?", (hashed, user_id))
            conn.commit()
            
            # Optional: Invalidate all other reset tokens for this user
            # This would require maintaining a table of used/invalidated tokens
            
            flash('Your password has been updated successfully! ✅ Please login with your new password.', 'success')
            return redirect('/login')
            
        except sqlite3.Error as e:
            app.logger.error(f'Database error in reset password: {str(e)}')
            flash('An error occurred. Please try again later.', 'danger')
            return redirect('/forgot')
        finally:
            conn.close()

    return render_template('reset_password.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    
    try:
        conn = sqlite3.connect('database/users.db')
        c = conn.cursor()
        
        # Get user info
        c.execute('SELECT * FROM users WHERE id=?', (session['user'],))
        user = c.fetchone()
        if not user:
            flash('User not found', 'danger')
            return redirect('/logout')

        # Get services
        c.execute("SELECT * FROM services")
        services = c.fetchall()

        # Get KRA registration history for the user
        c.execute("""
            SELECT * FROM kra_registrations 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        """, (session['user'],))
        kra_history = c.fetchall()

        # Get typesetting requests history for the user
        c.execute("""
            SELECT * FROM typesetting_requests 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        """, (session['user'],))
        typesetting_history = c.fetchall()

        return render_template('dashboard.html', 
                             user=user, 
                             services=services, 
                             kra_history=kra_history,
                             typesetting_history=typesetting_history)
                             
    except sqlite3.Error as e:
        flash(f'Database error: {str(e)}', 'danger')
        return redirect('/')
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user' not in session:
        return redirect('/login')
    conn = sqlite3.connect('database/users.db')
    c = conn.cursor()

    if request.method == 'POST':
        # Handle profile picture upload
        profile_picture = request.files.get('profile_picture')
        profile_picture_filename = None
        
        if profile_picture and profile_picture.filename:
            if allowed_file(profile_picture.filename):
                filename = secure_filename(profile_picture.filename)
                profile_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                profile_picture_filename = filename
            else:
                flash('Invalid file type for profile picture', 'error')
                return redirect('/edit-profile')

        # Update user data
        data = (
            request.form['firstname'],
            request.form['lastname'],
            request.form['gender'],
            request.form['email'],
            session['user']
        )
        
        if profile_picture_filename:
            c.execute('UPDATE users SET firstname=?, lastname=?, gender=?, email=?, profile_picture=? WHERE id=?', 
                     (*data[:-1], profile_picture_filename, data[-1]))
        else:
            c.execute('UPDATE users SET firstname=?, lastname=?, gender=?, email=? WHERE id=?', data)
            
        conn.commit()
        flash('Profile updated successfully ✅', 'success')
        return redirect('/dashboard')

    c.execute('SELECT * FROM users WHERE id=?', (session['user'],))
    user = c.fetchone()
    conn.close()
    return render_template('edit_profile.html', user=user)

@app.route('/admin-dashboard')
def admin_dashboard():
    if 'admin' not in session:
        flash('You must be an admin to view this page.', 'danger')
        return redirect('/admin-login')
    return render_template('admin_dashboard.html')

@app.route('/admin/users')
def admin_users():
    if 'admin' not in session:
        flash('Admin access required.', 'danger')
        return redirect('/admin-login')

    conn = sqlite3.connect('database/users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users')
    users = c.fetchall()
    conn.close()
    return render_template('admin_users.html', users=users)

@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'admin' not in session:
        flash('Admin access required.', 'danger')
        return redirect('/admin-login')

    conn = sqlite3.connect('database/users.db')
    c = conn.cursor()
    c.execute('DELETE FROM users WHERE id=?', (user_id,))
    conn.commit()
    conn.close()
    flash(f'User ID {user_id} deleted successfully ✅', 'success')
    return redirect('/admin/users')


@app.route('/admin/services')
def admin_services():
    if 'admin' not in session:
        flash('Admin access required.', 'danger')
        return redirect('/admin-login')
    
    conn = sqlite3.connect('database/users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM services")
    services = c.fetchall()
    conn.close()

    return render_template('admin_services.html', services=services)


@app.route('/admin/services/add', methods=['GET', 'POST'])
def admin_add_service():
    if 'admin' not in session:
        return redirect('/admin-login')
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        
        # Handle file upload
        if 'photo' not in request.files:
            flash('No photo uploaded', 'danger')
            return redirect(request.url)
            
        photo = request.files['photo']
        if photo.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
            
        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            conn = sqlite3.connect('database/users.db')
            c = conn.cursor()
            c.execute('INSERT INTO services (title, description, price, photo) VALUES (?, ?, ?, ?)',
                     (title, description, price, filename))
            conn.commit()
            conn.close()
            
            flash('Service added successfully!', 'success')
            return redirect('/admin/services')
        else:
            flash('Invalid file type. Allowed types: PNG, JPG, JPEG, GIF', 'danger')
            return redirect(request.url)
            
    return render_template('admin_add_service.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out 👋', 'info')
    return redirect('/')





@app.route('/admin/services/edit/<int:service_id>', methods=['GET', 'POST'])
def edit_service(service_id):
    if 'admin' not in session:
        return redirect('/admin-login')
    
    conn = sqlite3.connect('database/users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM services WHERE id = ?', (service_id,))
    service = c.fetchone()
    
    if not service:
        conn.close()
        flash('Service not found', 'danger')
        return redirect('/admin/services')
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        
        # Handle file upload
        photo = request.files['photo']
        if photo.filename != '':  # If a new photo was uploaded
            if photo and allowed_file(photo.filename):
                filename = secure_filename(photo.filename)
                photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                
                # Delete old photo if it exists
                if len(service) > 4 and service[4]:  # Check if photo exists
                    old_photo_path = os.path.join(app.config['UPLOAD_FOLDER'], service[4])
                    if os.path.exists(old_photo_path):
                        os.remove(old_photo_path)
                
                c.execute('UPDATE services SET title=?, description=?, price=?, photo=? WHERE id=?',
                         (title, description, price, filename, service_id))
            else:
                flash('Invalid file type. Allowed types: PNG, JPG, JPEG, GIF', 'danger')
                return redirect(request.url)
        else:  # If no new photo was uploaded, keep the existing one
            c.execute('UPDATE services SET title=?, description=?, price=? WHERE id=?',
                     (title, description, price, service_id))
        
        conn.commit()
        conn.close()
        flash('Service updated successfully!', 'success')
        return redirect('/admin/services')
    
    conn.close()
    return render_template('edit_service.html', service=service)



@app.route('/admin/services/delete/<int:service_id>', methods=['POST'])
def delete_service(service_id):
    if 'admin' not in session:
        flash('Admin access required.', 'danger')
        return redirect('/admin-login')

    conn = sqlite3.connect('database/users.db')
    c = conn.cursor()
    c.execute("DELETE FROM services WHERE id = ?", (service_id,))
    conn.commit()
    conn.close()

    flash('Service deleted successfully ✅', 'success')
    return redirect('/admin/services')

@app.route('/services')
def services():
    conn = sqlite3.connect('database/users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM services")
    services = c.fetchall()
    conn.close()
    return render_template('services.html', services=services)

@app.route('/kra-registration', methods=['GET', 'POST'])
def kra_registration():
    if 'user' not in session:
        flash('Please login to access this page', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            # Get form data
            fullname = request.form.get('fullname')
            dob = request.form.get('dob')
            id_number = request.form.get('id_number')
            county = request.form.get('county')
            town = request.form.get('town')
            po_box = request.form.get('po_box')
            email = request.form.get('email')
            phone = request.form.get('phone')
            transaction_code = request.form.get('transaction_code')

            # Validate required fields
            if not all([fullname, dob, id_number, county, town, po_box, email, phone, transaction_code]):
                flash('Please fill in all required fields', 'error')
                return redirect(url_for('kra_registration'))

            conn = sqlite3.connect('database/users.db')
            c = conn.cursor()
            
            # Insert KRA registration data
            c.execute("""
                INSERT INTO kra_registrations (
                    user_id, fullname, dob, id_number, county, town, 
                    po_box, email, phone, transaction_code, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
            """, (
                session['user'],
                fullname,
                dob,
                id_number,
                county,
                town,
                po_box,
                email,
                phone,
                transaction_code
            ))
            
            conn.commit()
            conn.close()
            
            flash('KRA registration submitted successfully! We will process your request shortly.', 'success')
            return redirect(url_for('dashboard'))
            
        except sqlite3.Error as e:
            flash(f'Database error: {str(e)}', 'error')
            return redirect(url_for('kra_registration'))
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')
            return redirect(url_for('kra_registration'))
    
    return render_template('kra_registration.html')

@app.route('/admin/kra-registrations')
def admin_kra_registrations():
    if 'admin' not in session:
        flash('Admin access required.', 'danger')
        return redirect('/admin-login')

    conn = sqlite3.connect('database/users.db')
    c = conn.cursor()
    
    # Get all KRA registrations with user information
    c.execute("""
        SELECT kr.id, kr.fullname, kr.dob, kr.id_number, kr.county, kr.town, 
               kr.po_box, kr.email, kr.phone, kr.transaction_code, kr.status, 
               kr.created_at, u.firstname, u.lastname, u.email as user_email
        FROM kra_registrations kr
        JOIN users u ON kr.user_id = u.id
        ORDER BY kr.created_at DESC
    """)
    registrations = c.fetchall()
    conn.close()

    return render_template('admin_kra_registrations.html', registrations=registrations)

@app.route('/admin/kra-registrations/update-status/<int:reg_id>', methods=['POST'])
def update_kra_registration_status(reg_id):
    if 'admin' not in session:
        flash('Admin access required.', 'danger')
        return redirect('/admin-login')

    new_status = request.form.get('status')
    if new_status not in ['pending', 'processing', 'completed']:
        flash('Invalid status', 'danger')
        return redirect('/admin/kra-registrations')

    conn = sqlite3.connect('database/users.db')
    c = conn.cursor()
    c.execute("UPDATE kra_registrations SET status = ? WHERE id = ?", (new_status, reg_id))
    conn.commit()
    conn.close()

    flash('Status updated successfully', 'success')
    return redirect('/admin/kra-registrations')

def recreate_kra_registrations_table():
    conn = sqlite3.connect('database/users.db')
    c = conn.cursor()
    
    # Drop existing table
    c.execute("DROP TABLE IF EXISTS kra_registrations")
    
    # Create new table with correct structure
    c.execute("""CREATE TABLE kra_registrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        fullname TEXT NOT NULL,
        dob TEXT NOT NULL,
        id_number TEXT NOT NULL,
        county TEXT NOT NULL,
        town TEXT NOT NULL,
        po_box TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        transaction_code TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )""")
    
    conn.commit()
    conn.close()

# Call this function to recreate the table
recreate_kra_registrations_table()

@app.route('/kra-history')
def kra_history():
    if 'user' not in session:
        flash('Please login to view your history', 'error')
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('database/users.db')
    c = conn.cursor()
    
    # Get KRA registration history for the user
    c.execute("""
        SELECT * FROM kra_registrations 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    """, (session['user'],))
    kra_history = c.fetchall()
    
    # Get typesetting requests history for the user
    c.execute("""
        SELECT * FROM typesetting_requests 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    """, (session['user'],))
    typesetting_history = c.fetchall()
    
    conn.close()
    
    return render_template('kra_history.html', 
                         kra_history=kra_history,
                         typesetting_history=typesetting_history)

@app.route('/typesetting', methods=['GET', 'POST'])
def typesetting():
    if 'user' not in session:
        flash('Please login to access this page', 'error')
        return redirect('/login')
    
    if request.method == 'POST':
        transaction_code = request.form['transaction_code']
        
        # Handle file upload
        if 'document_file' not in request.files:
            flash('No document uploaded', 'error')
            return redirect(request.url)
            
        document = request.files['document_file']
        if document.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
            
        if document and allowed_file(document.filename):
            filename = secure_filename(document.filename)
            document.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            conn = sqlite3.connect('database/users.db')
            c = conn.cursor()
            
            # Get user details
            c.execute('SELECT firstname, lastname, email FROM users WHERE id = ?', (session['user'],))
            user = c.fetchone()
            
            # Create new request
            c.execute('INSERT INTO typesetting_requests (user_id, fullname, email, document_file, transaction_code) VALUES (?, ?, ?, ?, ?)',
                     (session['user'], f"{user[0]} {user[1]}", user[2], filename, transaction_code))
            conn.commit()
            conn.close()
            
            flash('Your typesetting request has been submitted successfully!', 'success')
            return redirect('/dashboard')
        else:
            flash('Invalid file type. Allowed types: DOC, DOCX, TXT, PDF', 'error')
            return redirect(request.url)
            
    return render_template('typesetting.html')

def recreate_typesetting_requests_table():
    conn = sqlite3.connect('database/users.db')
    c = conn.cursor()
    
    # Drop existing table
    c.execute("DROP TABLE IF EXISTS typesetting_requests")
    
    # Create new table with correct structure
    c.execute("""CREATE TABLE typesetting_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        fullname TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT,
        document_type TEXT,
        document_file TEXT NOT NULL,
        transaction_code TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )""")
    
    conn.commit()
    conn.close()

# Call this function to recreate the table
recreate_typesetting_requests_table()

@app.route('/admin/typesetting')
def admin_typesetting():
    if 'admin' not in session:
        flash('Admin access required.', 'danger')
        return redirect('/admin-login')

    conn = sqlite3.connect('database/users.db')
    c = conn.cursor()
    
    # Get all typesetting requests with user information
    c.execute("""
        SELECT tr.id, tr.fullname, tr.email, tr.document_file, 
               tr.transaction_code, tr.status, tr.created_at,
               u.firstname, u.lastname, u.email as user_email
        FROM typesetting_requests tr
        JOIN users u ON tr.user_id = u.id
        ORDER BY tr.created_at DESC
    """)
    typesetting_requests = c.fetchall()
    conn.close()

    return render_template('admin_typesetting.html', typesetting_requests=typesetting_requests)

@app.route('/admin/typesetting/update-status/<int:req_id>', methods=['POST'])
def update_typesetting_status(req_id):
    if 'admin' not in session:
        flash('Admin access required.', 'danger')
        return redirect('/admin-login')

    new_status = request.form.get('status')
    if new_status not in ['pending', 'processing', 'completed']:
        flash('Invalid status', 'danger')
        return redirect('/admin/typesetting')

    try:
        conn = sqlite3.connect('database/users.db')
        c = conn.cursor()
        
        # First verify the request exists
        c.execute("SELECT id FROM typesetting_requests WHERE id = ?", (req_id,))
        if not c.fetchone():
            flash('Typesetting request not found', 'danger')
            return redirect('/admin/typesetting')
        
        # Update the status
        c.execute("UPDATE typesetting_requests SET status = ? WHERE id = ?", (new_status, req_id))
        conn.commit()
        
        flash('Status updated successfully', 'success')
        return redirect('/admin/typesetting')
        
    except sqlite3.Error as e:
        flash(f'Database error: {str(e)}', 'danger')
        return redirect('/admin/typesetting')
    finally:
        if 'conn' in locals():
            conn.close()

def add_profile_picture_column():
    conn = sqlite3.connect('database/users.db')
    c = conn.cursor()
    try:
        c.execute("ALTER TABLE users ADD COLUMN profile_picture TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        # Column already exists
        pass
    conn.close()

# Call this function to add the profile picture column
add_profile_picture_column()

@app.route('/donate')
def donate():
    return render_template('donate.html')

# === Start App ===
if __name__ == '__main__':
    app.run(debug=True)
