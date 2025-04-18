from flask import Flask, send_from_directory, render_template, session, redirect, url_for, flash
from it_services_section.app import app as it_services_app, mail
from flask_mail import Mail
import os

app = Flask(__name__,
            static_folder='it_services_section/static',
            template_folder='it_services_section/templates')

# Copy configuration from it_services_app
app.config.update(it_services_app.config)

# Set secret key for session management
app.secret_key = it_services_app.secret_key

# Initialize mail for the main app
mail.init_app(app)

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