import streamlit as st
from src.config import PAGE_CONFIG, CUSTOM_CSS, RESCUER_LAT, RESCUER_LON
from src.data import DataManager
from src.logic import calculate_urgency_score
from src.ui import render_sidebar, render_header, render_map, render_priority_list, render_chat_interface
from src.ai import AIAssistant
import os

# -----------------------------------------------------------------------------
# 1. CONFIGURATION & PAGE SETUP
# -----------------------------------------------------------------------------
st.set_page_config(**PAGE_CONFIG)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. MAIN APP FLOW
# -----------------------------------------------------------------------------

# Sidebar & Controls
show_routes, fire_sim_lat, fire_sim_lon = render_sidebar()

# Header
render_header()

# Data Loading & Processing
@st.cache_data
def get_data():
    # Load from the specific JSON file
    return DataManager.load_data_from_json('dummy_data/dataset_250_final.json')

raw_data = get_data()
processed_data = calculate_urgency_score(raw_data, fire_sim_lat, fire_sim_lon)

# Top Priorities
top_priorities = processed_data.head(3)

# Map Visualization
render_map(
    processed_data,
    fire_sim_lat,
    fire_sim_lon,
    RESCUER_LAT,
    RESCUER_LON,
    top_priorities,
    show_routes
)

# Detailed Data & Chat
col1, col2 = st.columns([1, 1])

with col1:
    render_priority_list(top_priorities, processed_data)

with col2:
    # Chat Logic using Session State
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Initial greeting - updated to reflect new mode (no fire sim)
        st.session_state.messages.append({
            "role": "assistant", 
            "content": f"Briefing: Vulnerable population data loaded. {len(top_priorities)} critical targets identified based on danger levels. Awaiting instructions."
        })

    # Render Interface and capture input
    prompt = render_chat_interface(st.session_state.messages, None)

    if prompt:
        # Add User Message
        st.session_state.messages.append({"role": "user", "content": prompt})

        context_data = {
            "top_target_id": top_priorities.iloc[0]['id'],
            "high_risk_count": len(processed_data[processed_data['urgency_score'] > 70])
        }

        # Get AI Response
        response_text = AIAssistant.get_response(prompt, context_data)

        st.session_state.messages.append({"role": "assistant", "content": response_text})
        st.rerun()
