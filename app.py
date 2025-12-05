import streamlit as st
from src.config import PAGE_CONFIG, CUSTOM_CSS, RESCUER_LAT, RESCUER_LON
from src.data import DataManager
from src.logic import calculate_urgency_score
from src.ui import render_sidebar, render_header, render_map, render_priority_list, render_chat_interface
from src.ai import AIAssistant

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
# Using cache_data decorator on a wrapper function or using session state is common.
# Since DataManager is static, we can wrap the call to use streamlit's cache.
#I have set some cortnates of mati [38.049498421610664, 23.98779210235504]
@st.cache_data
def get_data():
    return DataManager.load_vulnerable_citizens(center_lat=38.049498421610664, center_lon=23.98779210235504)

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
        # Initial greeting
        st.session_state.messages.append({
            "role": "assistant", 
            "content": f"Briefing: Fire detected at {fire_sim_lat:.4f}, {fire_sim_lon:.4f}. I have analyzed sensor data. {len(top_priorities)} critical targets identified requiring immediate evacuation based on mobility and proximity. Awaiting instructions."
        })

    # Render Interface and capture input
    prompt = render_chat_interface(st.session_state.messages, None)

    if prompt:
        # Add User Message
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Force a rerun to display the user message immediately isn't strictly necessary
        # as the next loop handles it, but st.chat_input behaves uniquely.
        # We need to manually append and rerun or just display it.
        # Standard pattern is: if prompt, append, then generate response.

        # We need to redisplay the user message because `render_chat_interface`
        # was called *before* we appended the new message.
        # Alternatively, we can rely on the rerun that happens on interaction,
        # but let's just create the response now.

        context_data = {
            "top_target_id": top_priorities.iloc[0]['id'],
            "high_risk_count": len(processed_data[processed_data['urgency_score'] > 70])
        }

        # Get AI Response
        response_text = AIAssistant.get_response(prompt, context_data)

        st.session_state.messages.append({"role": "assistant", "content": response_text})
        st.rerun()
