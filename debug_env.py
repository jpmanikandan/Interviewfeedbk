import os
from dotenv import load_dotenv, find_dotenv

print(f"Current Working Directory: {os.getcwd()}")

env_file = find_dotenv()
print(f"Found .env file at: {env_file}")

if not env_file:
    print("WARNING: No .env file found by find_dotenv()!")
    # Try looking for it explicitly in current dir
    if os.path.exists(".env"):
        print("BUT .env exists in current directory.")
    else:
        print("AND .env does not exist in current directory.")

print("Attempting to load .env...")
loaded = load_dotenv(verbose=True)
print(f"load_dotenv returned: {loaded}")

api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    print(f"SUCCESS: OPENAI_API_KEY found. Length: {len(api_key)}")
    print(f"Starts with: {api_key[:7]}...")
else:
    print("FAILURE: OPENAI_API_KEY not found in environment variables.")

# Check secrets.toml as fallback check (simulating app logic)
try:
    import streamlit as st
    if "OPENAI_API_KEY" in st.secrets:
        print("INFO: OPENAI_API_KEY found in st.secrets.")
    else:
        print("INFO: OPENAI_API_KEY NOT found in st.secrets.")
except ImportError:
    print("Streamlit not installed or not running in streamlit context (expected for this script).")
except Exception as e:
    print(f"Error checking secrets: {e}")
