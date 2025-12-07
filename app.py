import streamlit as st
from src.config import PAGE_CONFIG, CUSTOM_CSS
from src.data import DataManager
from src.logic import apply_ranking_logic
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
    
if 'list_widget_key' not in st.session_state:
    st.session_state.list_widget_key = 0

if "dataframe_key" not in st.session_state:
    st.session_state.dataframe_key = 0

# -----------------------------------------------------------------------------
# 3. DATA LOADING & PROCESSING
# -----------------------------------------------------------------------------
@st.cache_data
def get_citizen_data():
    # return DataManager.load_data_from_local_json('dummy_data/dataset_250_final.json')
    return DataManager.load_citizen_data_from_blob()

@st.cache_data
def get_fire_data():
    return DataManager.load_fire_data_from_blob()

raw_data = get_citizen_data()
fire_data = get_fire_data()
# Pass None for fire sim coords as they are disabled
processed_data = apply_ranking_logic(raw_data)
# Sorting is already handled in apply_ranking_logic

# -----------------------------------------------------------------------------
# 4. LAYOUT & INTERACTION
# -----------------------------------------------------------------------------

# --- Sidebar (Chat) ---
# render_sidebar now handles chat rendering and input
prompt = render_sidebar(st.session_state.messages)

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Context for AI
    # 1. Selected Citizen
    selected_citizen = None
    # Safer access to session_state
    current_selected_id = st.session_state.get('selected_citizen_id')
    if current_selected_id is not None:
        sel_row = processed_data[processed_data['id'] == current_selected_id]
        if not sel_row.empty:
            selected_citizen = sel_row.iloc[0].to_dict()

    # 2. Top Urgent Cases (Top 5)
    top_urgent_citizens = processed_data.head(5).to_dict('records')

    context_data = {
        "high_risk_count": len(processed_data[processed_data['urgency_score'] > 70]),
        "selected_citizen": selected_citizen,
        "top_urgent_citizens": top_urgent_citizens
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
        fire_df=fire_data,
        center_coords=st.session_state.map_center,
        zoom=st.session_state.zoom,
        selected_id=st.session_state.selected_citizen_id
    )

    # 1. Check if map_data exists AND if a specific object (marker) was clicked.
    # If the user clicks "the void", 'last_object_clicked' is usually None.
    if map_data and map_data.get('last_object_clicked'):
        
        # Extract coordinates from the OBJECT clicked, not the general map click
        click_lat = map_data['last_object_clicked']['lat']
        click_lon = map_data['last_object_clicked']['lng']

        # Find closest citizen/object to clicked lat/lon
        match = processed_data[
            (processed_data['lat'] == click_lat) &
            (processed_data['lon'] == click_lon)
        ]
        
        if not match.empty:
            clicked_id = match.iloc[0]['id']
        
        # CRITICAL STEP: Update the Session State
        if st.session_state.selected_citizen_id != clicked_id:
            st.session_state.selected_citizen_id = clicked_id
            st.rerun()  # <--- Triggers the app to reload with the new ID

        if not match.empty:
            clicked_id = match.iloc[0]['id']
            
            # 2. State Guard: Only rerun if the selection effectively CHANGES
            # This prevents reruns if the user clicks the same marker twice.
            if st.session_state.selected_citizen_id != clicked_id:
                st.session_state.selected_citizen_id = clicked_id
                
                st.session_state.list_widget_key += 1
                st.rerun()

# with col_map:
#     # Render Map and capture click events
#     map_data = render_map(
#         processed_data,
#         center_coords=st.session_state.map_center,
#         zoom=st.session_state.zoom
#     )

#     # Handle Map Clicks (Map -> List)
#     if map_data['last_object_clicked_popup']:
#         # Extract ID from popup text if possible, or use lat/lon matching
#         # Popup format is HTML, but tooltip usually has ID.
#         # Easier: Find closest citizen to clicked lat/lon
#         click_lat = map_data['last_object_clicked']['lat']
#         click_lon = map_data['last_object_clicked']['lng']

#         # Simple exact match check (or very close)
#         # Note: Folium might return slightly different precision
#         # Let's search for exact match first
#         match = processed_data[
#             (processed_data['lat'] == click_lat) &
#             (processed_data['lon'] == click_lon)
#         ]

#         if not match.empty:
#             clicked_id = match.iloc[0]['id']
#             if st.session_state.selected_citizen_id != clicked_id:
#                 st.session_state.selected_citizen_id = clicked_id
#                 st.rerun()

with col_list:
    # Generate a unique key string based on the counter
    # Example: "citizen_list_0", "citizen_list_1", etc.
    dynamic_key = f"citizen_list_{st.session_state.list_widget_key}"

    # Render List using the dynamic key
    selection = render_citizen_list(
        processed_data, 
        st.session_state.selected_citizen_id,
        widget_key=dynamic_key
    )

    # Handle List Selection (List -> Map)
    if selection and selection["selection"]["rows"]:
        selected_index = selection["selection"]["rows"][0]
        selected_row = processed_data.iloc[selected_index]

        # Update map center and selected ID
        new_center = [selected_row['lat'], selected_row['lon']]
        new_id = selected_row['id']

        if (st.session_state.map_center != new_center) or (st.session_state.selected_citizen_id != new_id):
            st.session_state.map_center = new_center
            st.session_state.selected_citizen_id = new_id
            st.session_state.zoom = 18 
            
            # NOTE: We do NOT increment list_widget_key here. 
            # If we did, the box the user just clicked would instantly uncheck.
            
            st.rerun()