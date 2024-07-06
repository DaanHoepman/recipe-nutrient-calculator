import os
from dotenv import load_dotenv

#--------------------

# Load environment variables from a .env file
load_dotenv()

class Config(object):
    """
    Configuration class for the Flask app; all environments
    """
    # Base variables
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True

    # Logging variables
    LOG_FILE = os.path.join(os.path.dirname(__file__), 'logs', 'app.log')
    LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

    # Secret key for session management and CSRF protection
    #SECRET_KEY = os.getenv('SECRET_KEY')
    SECRET_KEY = os.getenv('SECRET_KEY', 'mysecretkey')
    
    # Database URI for SQLAlchemy
    #SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Bootstrap settings
    BOOTSTRAP_FONTAWESOME = True
    
    # Folder to store uploaded files
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')

    # FoodData Central API key
    FDC_API_KEY = os.getenv("API_KEY")

class ProductionConfig(Config):
    """
    Configuration class for the Flask app in production
    """
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Security
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600

class DebugConfig(Config):
    """
    Configuration class for the Flask app in development
    """
    DEBUG = True

config_dict = {
    'development': DebugConfig,
    'production': ProductionConfig,
    'default': DebugConfig
}