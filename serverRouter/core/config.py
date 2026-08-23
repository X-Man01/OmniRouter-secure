"""Shared configuration constants for the OmniLLM API."""
import json
import os

import firebase_admin
from dotenv import load_dotenv
from firebase_admin import credentials, firestore

load_dotenv()

_FIREBASE_CREDENTIALS_JSON = os.getenv("FIREBASE_CREDENTIALS_JSON")
if not _FIREBASE_CREDENTIALS_JSON:
    raise RuntimeError(
        "FIREBASE_CREDENTIALS_JSON is not set. Put the full Firebase service-account "
        "JSON (as a single-line string) in your .env file or secrets manager — see "
        ".env.example. Never write it to a file in the repo."
    )

cred = credentials.Certificate(json.loads(_FIREBASE_CREDENTIALS_JSON))
app = firebase_admin.initialize_app(cred)
db = firestore.client()
VALID_API_KEYS = set()

def update_api_keys(keys_snapshot, changes, read_time):
    """Update the VALID_API_KEYS set when changes occur in Firestore."""
    global VALID_API_KEYS
    VALID_API_KEYS = {key.id for key in keys_snapshot}

initial_keys = db.collection('api_keys').get()
update_api_keys(initial_keys, None, None)
api_keys_watch = db.collection('api_keys').on_snapshot(update_api_keys)

PROVIDERS = {}
MAX_TOKENS = 100000
