import folium
from streamlit_folium import st_folium
import pandas as pd
import streamlit as st

def render_chat_interface(messages):
    """
    Renders the chat interface.

    Args:
        messages: List of message dicts {"role": "...", "content": "..."}
    """
    st.sidebar.subheader("🤖 AI Mission Support")

    # Display chat history
    for message in messages:
        with st.sidebar.chat_message(message["role"]):
            st.sidebar.markdown(message["content"])

    return st.sidebar.chat_input("Ask about the situation...")

def render_sidebar(messages):
    """Renders the sidebar controls (now primarily Chat) and returns the chat prompt."""
    st.sidebar.header("🚒 Operation Controls")

    # Render Chat Interface
    return render_chat_interface(messages)

def render_header():
    """Renders the main header."""
    col_head1, col_head2 = st.columns([3, 1])
    with col_head1:
        st.title("🛡️ Aegis: Intelligent Rescue Response")
        st.markdown("Real-time prioritization of vulnerable populations during crisis.")
    with col_head2:
        st.metric(label="System Status", value="ACTIVE", delta="CRITICAL ALERT")

def render_map(processed_data, center_coords=None, zoom=14, selected_id=None):
    """
    Renders the Folium map.

    Args:
        processed_data: Dataframe containing citizen data.
        center_coords: Tuple (lat, lon) to center the map.
        zoom: Initial zoom level.
        selected_id: ID of the citizen to automatically open the popup for.

    Returns:
        The clicked object from st_folium.
    """
    st.subheader("📍 Live Tactical Map")

    # Initialize Map
    if center_coords is None:
        center_coords = [38.049498421610664, 23.98779210235504]

    m = folium.Map(location=center_coords, zoom_start=zoom)

    # Layer 1: The People
    for _, row in processed_data.iterrows():
        is_selected = (selected_id is not None) and (row['id'] == selected_id)

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

        # Create Popup with show=True if this is the selected citizen
        popup = folium.Popup(popup_html, max_width=250, show=is_selected)

        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=8 if is_selected else 5, # Make selected marker slightly larger
            color='blue' if is_selected else color, # Highlight selection with specific color
            fill=True,
            fill_color='blue' if is_selected else color,
            fill_opacity=0.9 if is_selected else 0.7,
            popup=popup,
            tooltip=f"{fullname} ({row['id']})"
        ).add_to(m)

    # Render Map using streamlit-folium with maximized size
    return st_folium(m, use_container_width=True, height=700)

def render_citizen_list(full_data, selected_id=None, key=None):
    """
    Renders the citizen list as a selectable dataframe.

    Args:
        full_data: DataFrame of citizens.
        selected_id: ID of the citizen to highlight (if possible) or display details for.
        key: Streamlit key for the dataframe widget.

    Returns:
        Selection event from st.dataframe.
    """
    st.subheader("📋 Priority List")

    # Display selected citizen details if one is selected
    if selected_id is not None:
        selected_row = full_data[full_data['id'] == selected_id]
        if not selected_row.empty:
            row = selected_row.iloc[0]
            st.info(f"🎯 **Selected:** {row.get('fullname', row['id'])} | Urgency: {int(row['urgency_score'])}")

    # Prepare data for display
    cols = ['id', 'fullname', 'urgency_score', 'danger_level', 'life_support']
    available_cols = [c for c in cols if c in full_data.columns]

    display_df = full_data[available_cols].copy()

    # Apply Highlight Style if selected_id is present
    def highlight_selected(row):
        if selected_id is not None and row['id'] == selected_id:
            # Using a distinct color for selection (e.g. dark blue background with white text)
            return ['background-color: #1f77b4; color: white; font-weight: bold'] * len(row)
        return [''] * len(row)

    # Note: st.dataframe supports styled dataframes
    styled_df = display_df.style.apply(highlight_selected, axis=1)

    # Return the selection event
    return st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun",
        height=600,
        key=key  # Use provided key
    )
