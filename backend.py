from fastapi import FastAPI, Response
import sqlite3
import random
import os
from datetime import datetime
from typing import Optional
from google.cloud import storage

from name_gen import generate_name

app = FastAPI()

@app.get("/")
def home():
    return {"message": "API is running!"}

if "DB_PATH" in os.environ:
    # Production environment
    DB_PATH = os.environ["DB_PATH"]
else:
    # Local environment
    DB_PATH = os.path.join(os.path.dirname(__file__), "names.db")

# Set bucket and database file details
BUCKET_NAME = "taxifare_timb808"
DB_FILENAME = "names.db"
LOCAL_DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), DB_FILENAME))

def download_db_from_gcs():
    """Always download the latest names.db from Google Cloud Storage."""
    print(f"Downloading {DB_FILENAME} from GCS...")
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(DB_FILENAME)
    blob.download_to_filename(LOCAL_DB_PATH)
    print("Download complete.")

# Run this on startup (only in production)
if "DB_PATH" in os.environ:  # Check if we're in a production environment
    download_db_from_gcs()


def create_table():
    """Create the names table if it doesn't exist."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS names (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)
create_table()

def store_name(name):
    """Store a generated name in the database."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO names (name) VALUES (?)", (name,))
        conn.commit()

def get_name_by_index(index):
    """Retrieve a name by its position."""
    # Subtract 1 from user input to reflect that index starts at 0
    index = index - 1
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT name FROM names LIMIT 1 OFFSET ?", (index,))
        result = cursor.fetchone()
        return result[0] if result else None

def get_name_by_first_letter(first_letter):
    """Retrieve a random name starting with a given letter."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT name FROM names WHERE name LIKE ? ORDER BY RANDOM() LIMIT 1", (first_letter + '%',))
        result = cursor.fetchone()
        return result[0] if result else None


def get_random_name():
    """Retrieve a random name from the database."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT name FROM names ORDER BY RANDOM() LIMIT 1")
        result = cursor.fetchone()
        return result[0] if result else None

@app.get("/count_names")
def count_names():
    """Return the total number of names in the database."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM names")
        count = cursor.fetchone()[0]
    return {"count": count}

@app.post("/generate_name")
def generate_name_endpoint(length: Optional[int] = None, first_letter: Optional[str] = None):
    """Generate and store a name with optional length and first letter."""
    name = generate_name(length=length, first_letter=first_letter)
    store_name(name)
    return {"generated_name": name}

@app.get("/retrieve_name")
def retrieve_name(index: Optional[int] = None, first_letter: Optional[str] = None):
    """Retrieve a name by index or first letter. If both are provided, index is prioritised."""
    message = None
    name = None

    if index is not None:
        name = get_name_by_index(index)
        if first_letter:
            message = "Both an index and a letter were provided. Retrieving by index."
    elif first_letter:
        name = get_name_by_first_letter(first_letter)
    else:
        name = get_random_name()

    if name:
        response = {"name": name}
        if message:
            response["message"] = message
        return response
    return {"error": "No name found"}


@app.get("/random_name")
def random_name(first_letter: Optional[str] = None):
    """Retrieve a random name, optionally starting with a specific letter."""
    if first_letter:
        name = get_name_by_first_letter(first_letter)
    else:
        name = get_random_name()

    return {"random_name": name} if name else {"error": "No names found"}


# Start the FastAPI server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
