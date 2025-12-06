import folium
from streamlit_folium import st_folium
import pandas as pd
import streamlit as st

def render_sidebar():
    """Renders the sidebar controls and returns the configuration values."""
    st.sidebar.header("🚒 Operation Controls")
    show_routes = st.sidebar.checkbox("Show Rescue Routes", value=True)
    # Fire simulation sliders commented out
    # fire_sim_lat = st.sidebar.slider("Fire Latitude", 40.6300, 40.6500, 40.6401)
    # fire_sim_lon = st.sidebar.slider("Fire Longitude", 22.9300, 22.9600, 22.9444)
    # Returning None for fire coordinates since they are unused
    return show_routes, None, None

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
    m = folium.Map(location=[38.049498421610664, 23.98779210235504], zoom_start=14)

    # Layer 2: The Fire (Heatmap/Circle) - Commented out
    # if fire_sim_lat is not None and fire_sim_lon is not None:
    #     folium.Circle(
    #         location=[fire_sim_lat, fire_sim_lon],
    #         radius=400, # Fire radius in meters
    #         color="orangered",
    #         fill=True,
    #         fill_color="orangered",
    #         fill_opacity=0.4,
    #         tooltip="Fire Zone"
    #     ).add_to(m)

    # Layer 1: The People (Scatterplot equivalent)
    for _, row in processed_data.iterrows():
        # Color logic: Red (High Urgency) to Green (Low Urgency)
        color = 'red' if row['urgency_score'] > 50 else 'green'

        # Helper to safely get life_support
        life_support = "Yes" if row.get('life_support', 0) == 1 else "No"
        notes = row.get('notes', 'N/A')
        fullname = row.get('fullname', 'Unknown')

        popup_html = f"""
        <b>ID:</b> {row['id']}<br>
        <b>Name:</b> {fullname}<br>
        <b>Urgency:</b> {int(row['urgency_score'])}<br>
        <b>Life Support:</b> {life_support}<br>
        <b>Notes:</b> {notes}
        """

        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=5,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{fullname} ({row['id']})"
        ).add_to(m)

    # Render Map using streamlit-folium
    st_folium(m, width=None, height=500)

def render_priority_list(top_priorities, full_data):
    """Renders the priority list and data expander."""
    st.subheader("📋 Priority Extraction List")
    # Display the top targets nicely
    for i, row in top_priorities.iterrows():
        life_support = "Yes" if row.get('life_support', 0) == 1 else "No"
        with st.container():
            st.warning(f"🚨 **{row.get('fullname', row['id'])}** | Urgency: {int(row['urgency_score'])}/100")
            st.write(f"Life Support: {life_support} | Notes: {row.get('notes', '-')}")
            st.progress(int(row['urgency_score']))

    with st.expander("View Full Database"):
        # Select columns that exist in the dataframe
        cols = ['id', 'fullname', 'life_support', 'danger_level', 'urgency_score', 'notes']
        # Filter cols to only those present in full_data to avoid errors if something is missing
        available_cols = [c for c in cols if c in full_data.columns]
        st.dataframe(full_data[available_cols])

def render_chat_interface(messages, on_submit):
    """
    Renders the chat interface.

    Args:
        messages: List of message dicts {"role": "...", "content": "..."}
        on_submit: Callback function when user submits input.
    """
    st.subheader("🤖 AI Mission Support")

    # Display chat history
    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    return st.chat_input("Ask about the situation...")
