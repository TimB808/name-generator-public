import streamlit as st
import requests
import os
from google.cloud import storage
import base64

API_URL = os.getenv("API_URL", "http://127.0.0.1:8080")

st.set_page_config(page_title="What's in a Name?")

st.markdown(
    """
    <style>
    /* Title */
    .stApp h1 {
        font-size: 40px !important;
        font-weight: bold;
        color: #000000;
        text-shadow: 1px 1px 3px rgba(255, 255, 255, 0.6);
    }

    /* Subtitles/Headings */
    .stApp h2 {
        font-size: 30px !important;
        font-weight: bold;
        color: #000000;
        text-shadow: 1px 1px 3px rgba(255, 255, 255, 0.6);
    }

    /* Body Text */
    .stApp p, .stApp label, .stApp div {
        font-size: 18px !important;
        font-weight: normal;
        color: #000000;
        text-shadow: 1px 1px 3px rgba(255, 255, 255, 0.6);
    }

    /* Ensure database info is NOT bold */
    .stApp p:has(span[aria-hidden="true"]) {
        font-weight: normal !important;
    }

    /* Style input boxes */
    .stTextInput > div > div > input {
        border: 1px solid #ccc !important;
        border-radius: 5px !important;
        background-color: rgba(255, 255, 255, 0.9) !important;
        color: #000000 !important;
        font-size: 16px !important;
        padding: 8px !important;
    }

    /* Restore default button styles */
    .stButton > button {
        all: unset !important;
        display: inline-block !important;
        padding: 8px 16px !important;
        border-radius: 5px !important;
        font-size: 16px !important;
        font-weight: bold !important;
        background-color: #f0f0f0 !important;
        color: #000000 !important;
        border: 1px solid #ccc !important;
        cursor: pointer !important;
    }

    .stButton > button:hover {
        background-color: #e0e0e0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("What's in a Name?")
st.write("Need a name for your child, plant or pet tarantula? This app is here to help!")
st.write("Create a new, unique name with a random letter combination. Every new name generated is added to our database, available for you to explore below. \n ")

# Section 1: Name Generation
st.header("Generate a New Name")
first_letter_input = st.text_input("Enter first letter of name (optional):", "")
length_input = st.text_input("Enter desired name length (optional):", "")

if st.button("Generate Name"):
    params = {}
    if first_letter_input:
        params["first_letter"] = first_letter_input
    if length_input.isdigit():
        params["length"] = int(length_input)

    response = requests.post(f"{API_URL}/generate_name", params=params)

    if response.status_code == 200:
        st.success(f"Generated Name: {response.json().get('generated_name')}")
    else:
        st.error("Error generating name. Please try again.")

# Section 2: Show the Number of Names in the Database
st.header("Database Information")

# Fetch the total number of names
db_info = requests.get(f"{API_URL}/count_names")
if db_info.status_code == 200:
    total_names = db_info.json().get("count", 0)
    st.write(f"📊 Total names stored in the database: **{total_names}**")
else:
    st.write("⚠️ Error retrieving database information.")

# Section 3: Retrieve a Name from the Database
st.header("Retrieve a Stored Name")
st.write("Enter a first letter or a row number to see a name from the database. "
         )

retrieve_input = st.text_input("If both are entered, the number will be used. Or just leave the field blank and click the button to see a random name!", "")

if st.button("Retrieve Name"):
    params = {}
    message = None  # Placeholder for an optional info message

    if retrieve_input:
        letters = "".join([char for char in retrieve_input if char.isalpha()])
        numbers = "".join([char for char in retrieve_input if char.isdigit()])

        if numbers:
            params["index"] = int(numbers)
            if letters:
                message = "You entered both a letter and a number. Retrieving by index."
        elif letters and len(letters) == 1:
            params["first_letter"] = letters
        else:
            st.error("Invalid input. Enter either a number (index) or a single letter.")
            st.stop()

    response = requests.get(f"{API_URL}/retrieve_name", params=params)

    if response.status_code == 200:
        retrieved_name = response.json().get("name", "No name found.")
        st.success(f"Retrieved Name: {retrieved_name}")
        if message:
            st.info(message)
    else:
        st.error("Error retrieving name. Please try again.")

# Section 4: background image
def add_bg_from_gcs(bucket_name, image_blob_name):
    """Reads an image from Google Cloud Storage and sets it as the background."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(image_blob_name)
    image_data = blob.download_as_bytes()
    encoded_string = base64.b64encode(image_data).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url(data:image/png;base64,{encoded_string});
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-position: center;
            opacity: 0.7;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

bucket_name = "taxifare_timb808"
image_blob_name = "wordcloud_faint_15pc.png"

def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
        opacity: 0.7;
    }}
    </style>
    """,
    unsafe_allow_html=True
    )

# Determine if running locally or in Cloud Run
if "GOOGLE_CLOUD_PROJECT" in os.environ:
    # Running in Cloud Run
    bucket_name = "taxifare_timb808"
    image_blob_name = "wordcloud_faint_15pc.png"
    add_bg_from_gcs(bucket_name, image_blob_name)
else:
    # Running locally
    add_bg_from_local('wordcloud_faint_15pc.png')
