from flask import Flask, send_from_directory, render_template, session, redirect, url_for, flash
from it_services_section.app import app as it_services_app, mail
from flask_mail import Mail
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('it_services_section/manage.env')

app = Flask(__name__,
            static_folder='it_services_section/static',
            template_folder='it_services_section/templates')

# Set secret key for session management
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')

# Copy email configuration from it_services_app
app.config.update(
    MAIL_SERVER=it_services_app.config['MAIL_SERVER'],
    MAIL_PORT=it_services_app.config['MAIL_PORT'],
    MAIL_USE_TLS=it_services_app.config['MAIL_USE_TLS'],
    MAIL_USE_SSL=it_services_app.config['MAIL_USE_SSL'],
    MAIL_USERNAME=it_services_app.config['MAIL_USERNAME'],
    MAIL_PASSWORD=it_services_app.config['MAIL_PASSWORD'],
    MAIL_DEFAULT_SENDER=it_services_app.config['MAIL_DEFAULT_SENDER'],
    MAIL_MAX_EMAILS=it_services_app.config['MAIL_MAX_EMAILS'],
    MAIL_ASCII_ATTACHMENTS=it_services_app.config['MAIL_ASCII_ATTACHMENTS']
)

# Initialize mail for the main app
mail.init_app(app)

# Debug mail configuration
print("Mail Configuration:")
print(f"MAIL_SERVER: {app.config['MAIL_SERVER']}")
print(f"MAIL_PORT: {app.config['MAIL_PORT']}")
print(f"MAIL_USE_TLS: {app.config['MAIL_USE_TLS']}")
print(f"MAIL_USE_SSL: {app.config['MAIL_USE_SSL']}")
print(f"MAIL_USERNAME: {app.config['MAIL_USERNAME']}")
print(f"MAIL_PASSWORD: {'*' * len(app.config['MAIL_PASSWORD']) if app.config['MAIL_PASSWORD'] else 'Not set'}")
print(f"MAIL_DEFAULT_SENDER: {app.config['MAIL_DEFAULT_SENDER']}")

# Main static index page
@app.route('/')
def serve_index():
    return send_from_directory('it_services_section/static', 'index.html')

# IT Services section - serve from templates
@app.route('/it-services')
def it_services():
    return render_template('index.html')

# Copy all routes from it_services_app
for rule in it_services_app.url_map.iter_rules():
    if not str(rule).startswith('/static') and str(rule) != '/':
        app.add_url_rule(
            str(rule),
            view_func=it_services_app.view_functions[rule.endpoint],
            methods=rule.methods
        )

# Serve static files
@app.route('/<path:path>')
def serve_static(path):
    # Check if the path is for static files
    if path.startswith(('css/', 'js/', 'images/', 'files/')):
        return send_from_directory('it_services_section/static', path)
    
    # For HTML files, serve them directly
    if path.endswith('.html'):
        return send_from_directory('it_services_section/static', path)
    
    # For any other path, try to serve from static
    try:
        return send_from_directory('it_services_section/static', path)
    except:
        return "Page not found", 404

if __name__ == '__main__':
    app.run(debug=True) 
