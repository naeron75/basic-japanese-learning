# config.py
import os
from dotenv import load_dotenv
from pathlib import Path

# --- 1. Robust .env Loading ---
# Determine the base directory of the project.
# Path(__file__).resolve() gets the absolute path of config.py
# .parent goes up one level to the 'api' folder (if applicable)
# .parent goes up another level to the project root where .env should be.
BASE_DIR = Path(__file__).resolve().parent.parent

# Define the absolute path to the .env file
dotenv_path = BASE_DIR / '.env'

# Attempt to load the .env file explicitly
if dotenv_path.exists():
    load_dotenv(dotenv_path)
    # print("DEBUG: .env file found and loaded successfully.")
else:
    # If the file is not found, raise an immediate error.
    # This prevents the silent failure (returning 'None') that caused the ValueError.
    raise FileNotFoundError(
        f"ERROR: .env file not found at {dotenv_path}. Please check the file location."
    )
    
# --- 2. Retrieve Environment Variables ---

DB_USER = os.environ.get("MYSQL_USER")
DB_PASSWORD = os.environ.get("MYSQL_PASSWORD")
DB_HOST = os.environ.get("MYSQL_HOST")
DB_PORT = os.environ.get("MYSQL_PORT") # This should now be a string like '3306'
DB_NAME = os.environ.get("MYSQL_DB_NAME") 

# --- 3. Defensive Check for Missing Variables ---
# If any variable is missing (meaning it wasn't in the .env file), raise an error.
if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
    missing = [k for k, v in {
        "MYSQL_USER": DB_USER, 
        "MYSQL_PASSWORD": DB_PASSWORD, 
        "MYSQL_HOST": DB_HOST, 
        "MYSQL_PORT": DB_PORT, 
        "MYSQL_DB_NAME": DB_NAME
    }.items() if v is None]
    
    raise ValueError(
        f"Missing one or more required environment variables in .env: {', '.join(missing)}"
    )

# --- 4. Flask and SQLAlchemy Configuration ---

class Config:
    # The SQLALCHEMY_DATABASE_URI will now be built using verified string values.
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API Settings
    PER_PAGE = 20 # Default items per page for pagination