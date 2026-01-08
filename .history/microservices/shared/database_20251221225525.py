"""
Shared database configuration for all microservices.
All services use the same SQLite database.
"""
import os
from pathlib import Path

# Base directory is the project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Database configuration - shared across all microservices
DATABASE_CONFIG = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

def get_database_path():
    """Returns the absolute path to the shared database"""
    return str(BASE_DIR / 'db.sqlite3')
