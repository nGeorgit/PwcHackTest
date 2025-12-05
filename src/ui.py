import folium
from streamlit_folium import st_folium
import pandas as pd
import streamlit as st

def render_sidebar():
    """Renders the sidebar controls and returns the configuration values."""
    st.sidebar.header("🚒 Operation Controls")
    show_routes = st.sidebar.checkbox("Show Rescue Routes", value=True)
    fire_sim_lat = st.sidebar.slider("Fire Latitude", 40.6300, 40.6500, 40.6401)
    fire_sim_lon = st.sidebar.slider("Fire Longitude", 22.9300, 22.9600, 22.9444)
    return show_routes, fire_sim_lat, fire_sim_lon

def render_header():
    """Renders the main header."""
    col_head1, col_head2 = st.columns([3, 1])
    with col_head1:
        st.title("🛡️ Aegis: Intelligent Rescue Response")
        st.markdown("Real-time prioritization of vulnerable populations during crisis.")
    with col_head2:
        st.metric(label="System Status", value="ACTIVE", delta="CRITICAL ALERT")

def render_map(processed_data, fire_sim_lat, fire_sim_lon, rescuer_lat, rescuer_lon, top_priorities, show_routes):
    """Renders the Folium map."""
    st.subheader("📍 Live Tactical Map")

    # Initialize Map centered at the fire (or generic center)
    m = folium.Map(location=[40.6401, 22.9444], zoom_start=14)

    # Layer 2: The Fire (Heatmap/Circle)
    folium.Circle(
        location=[fire_sim_lat, fire_sim_lon],
        radius=400, # Fire radius in meters
        color="orangered",
        fill=True,
        fill_color="orangered",
        fill_opacity=0.4,
        tooltip="Fire Zone"
    ).add_to(m)

    # Layer 1: The People (Scatterplot equivalent)
    for _, row in processed_data.iterrows():
        # Color logic: Red (High Urgency) to Green (Low Urgency)
        color = 'red' if row['urgency_score'] > 50 else 'green'

        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=5,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=folium.Popup(f"ID: {row['id']}<br>Urgency: {int(row['urgency_score'])}", max_width=200),
            tooltip=f"{row['id']}"
        ).add_to(m)

    # Layer 3: The Rescuer
    folium.Marker(
        location=[rescuer_lat, rescuer_lon],
        popup="Rescuer Unit",
        tooltip="Rescuer",
        icon=folium.Icon(color="blue", icon="ambulance", prefix='fa')
    ).add_to(m)

    # Layer 4: Routing (Lines from Rescuer to High Urgency Targets)
    if show_routes:
        for _, row in top_priorities.iterrows():
            folium.PolyLine(
                locations=[[rescuer_lat, rescuer_lon], [row['lat'], row['lon']]],
                color="yellow",
                weight=5,
                opacity=0.8,
                tooltip=f"Route to {row['id']}"
            ).add_to(m)

    # Render Map using streamlit-folium
    st_folium(m, width=None, height=500)

def render_priority_list(top_priorities, full_data):
    """Renders the priority list and data expander."""
    st.subheader("📋 Priority Extraction List")
    # Display the top targets nicely
    for i, row in top_priorities.iterrows():
        with st.container():
            st.warning(f"🚨 **{row['id']}** | Urgency: {int(row['urgency_score'])}/100")
            st.write(f"Age: {row['age']} | Mobility: {row['mobility']}/10 | Disease: {row['has_disease']}")
            st.progress(int(row['urgency_score']))

    with st.expander("View Full Database"):
        st.dataframe(full_data[['id', 'age', 'mobility', 'has_disease', 'urgency_score']])

def render_chat_interface(messages, on_submit):
    """
    Renders the chat interface.

    Args:
        messages: List of message dicts {"role": "...", "content": "..."}
        on_submit: Callback function when user submits input.
                   NOTE: In Streamlit's simple model, we usually handle this
                   outside the function by returning the input or checking chat_input.
                   Here we just render the history and the input box.
    """
    st.subheader("🤖 AI Mission Support")

    # Display chat history
    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    return st.chat_input("Ask about the situation...")
