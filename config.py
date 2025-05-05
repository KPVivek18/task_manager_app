import os
from dotenv import load_dotenv

# Load .env file values into environment variables
load_dotenv()

class Config:
    SECRET_KEY = 'your-secret-key'  # Needed for Flask-Login

    # MySQL connection string
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Visca10$@localhost/task_manager'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # AWS credentials from .env
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')
    AWS_REGION = os.getenv('AWS_REGION')
