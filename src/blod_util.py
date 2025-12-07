# utils_azure.py
import streamlit as st
from azure.storage.blob import BlobServiceClient
import json
from src.config import STORAGE_CONN_STRING
import os


@st.cache_data(ttl=600)  # Cache data for 10 minutes (600 seconds)
def fetch_json_from_blob(blob_name, container_name="configdata"):
    """
    Standalone function to fetch JSON from Azure.
    Can be called from anywhere in the app.
    """
    conn_str = STORAGE_CONN_STRING
    
    if not conn_str:
        st.error("⚠️ Connection string not found! Check secrets/env variables.")
        return None

    try:
        # Create client
        blob_service_client = BlobServiceClient.from_connection_string(conn_str)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

        # Download and Parse
        # print(f"DEBUG: Downloading {blob_name}...") # Uncomment for debugging
        download_stream = blob_client.download_blob()
        json_data = json.loads(download_stream.readall())
        return json_data

    except Exception as e:
        st.error(f"Error fetching {blob_name}: {e}")
        return None