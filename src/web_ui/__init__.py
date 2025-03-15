from flask import Flask
from flask_wtf.csrf import CSRFProtect
from . import routes
import os

def create_app():
    # Get the absolute path to the templates directory
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))
    
    # Create the Flask app with explicit template folder
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    
    # Set a secret key for CSRF protection
    app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'dev-key-for-testing')
    
    # Initialize CSRF protection
    csrf = CSRFProtect(app)
    
    # Register blueprints
    app.register_blueprint(routes.bp)
    app.register_blueprint(routes.main)
    
    # Debug information
    print(f"Flask app created with template folder: {template_dir}")
    print(f"Available routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule}")
    
    return app 