import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'csir-crri-secret-2026')
    
    DATABASE_URL = os.environ.get('DATABASE_URL', '')
    MYSQL_URL = os.environ.get('MYSQL_URL', '')
    
    # Railway gives MYSQL_URL, handle both formats
    db_url = DATABASE_URL or MYSQL_URL
    if db_url.startswith('mysql://'):
        db_url = db_url.replace('mysql://', 'mysql+pymysql://', 1)
    
    SQLALCHEMY_DATABASE_URI = db_url or \
        'mysql+pymysql://root:your_password@localhost/csir_canteen'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True