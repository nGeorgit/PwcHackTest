import streamlit as st
from src.config import PAGE_CONFIG, CUSTOM_CSS
from src.data import DataManager
from src.logic import calculate_urgency_score
from src.ui import render_sidebar, render_header, render_map, render_citizen_list
from src.ai import AIAssistant
import pandas as pd

# -----------------------------------------------------------------------------
# 1. CONFIGURATION & PAGE SETUP
# -----------------------------------------------------------------------------
st.set_page_config(**PAGE_CONFIG)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. STATE MANAGEMENT
# -----------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Briefing: Vulnerable population data loaded. Awaiting instructions."
    })

if "map_center" not in st.session_state:
    st.session_state.map_center = [38.049498421610664, 23.98779210235504]

if "zoom" not in st.session_state:
    st.session_state.zoom = 14

if "selected_citizen_id" not in st.session_state:
    st.session_state.selected_citizen_id = None

# -----------------------------------------------------------------------------
# 3. DATA LOADING & PROCESSING
# -----------------------------------------------------------------------------
@st.cache_data
def get_data():
    return DataManager.load_data_from_json('dummy_data/dataset_250_final.json')

raw_data = get_data()
# Pass None for fire sim coords as they are disabled
processed_data = calculate_urgency_score(raw_data, None, None)

# Sort by Urgency Score (Highest to Lowest)
processed_data = processed_data.sort_values(by='urgency_score', ascending=False)

# -----------------------------------------------------------------------------
# 4. LAYOUT & INTERACTION
# -----------------------------------------------------------------------------

# --- Sidebar (Chat) ---
# render_sidebar now handles chat rendering and input
prompt = render_sidebar(st.session_state.messages)

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Context for AI
    top_target = processed_data.iloc[0] if not processed_data.empty else None
    context_data = {
        "top_target_id": top_target['id'] if top_target is not None else "N/A",
        "high_risk_count": len(processed_data[processed_data['urgency_score'] > 70])
    }

    response_text = AIAssistant.get_response(prompt, context_data)
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    st.rerun()

# --- Main Area ---
render_header()

# Create layout: Map (Left/Large) | List (Right/Small)
col_map, col_list = st.columns([7, 3])

with col_map:
    # Render Map and capture click events
    map_data = render_map(
        processed_data,
        center_coords=st.session_state.map_center,
        zoom=st.session_state.zoom,
        selected_id=st.session_state.selected_citizen_id
    )

    # Handle Map Clicks (Map -> List)
    # We check if 'last_object_clicked' is available and valid
    if map_data.get('last_object_clicked'):
        click_lat = map_data['last_object_clicked']['lat']
        click_lon = map_data['last_object_clicked']['lng']

        # Find closest citizen to clicked lat/lon
        # Using a small tolerance (e.g. 0.0001 degrees) or exact match
        # Since we use CircleMarkers, the click should be exact coordinate of the marker center
        # (folium usually returns the marker's lat/lon if clicked ON the marker)

        match = processed_data[
            (processed_data['lat'] == click_lat) &
            (processed_data['lon'] == click_lon)
        ]

        if not match.empty:
            clicked_id = match.iloc[0]['id']
            # Only update if it's different to avoid loops, AND allow re-clicking to confirm
            if st.session_state.selected_citizen_id != clicked_id:
                st.session_state.selected_citizen_id = clicked_id
                st.rerun()

with col_list:
    # Render List and capture selection events
    selection = render_citizen_list(processed_data, st.session_state.selected_citizen_id)

    # Handle List Selection (List -> Map)
    if selection and selection["selection"]["rows"]:
        selected_index = selection["selection"]["rows"][0]
        # Get the row from the *displayed* dataframe (which matches processed_data order)
        selected_row = processed_data.iloc[selected_index]

        # Update map center and selected ID
        new_center = [selected_row['lat'], selected_row['lon']]
        new_id = selected_row['id']

        # Only rerun if changed to prevent loops
        if (st.session_state.map_center != new_center) or (st.session_state.selected_citizen_id != new_id):
            st.session_state.map_center = new_center
            st.session_state.selected_citizen_id = new_id
            st.session_state.zoom = 18 # Zoom in on selection
            st.rerun()
