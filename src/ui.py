import pydeck as pdk
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
    """Renders the PyDeck map."""
    st.subheader("📍 Live Tactical Map")

    # Layer 1: The People (Scatterplot)
    # Color logic: Red (High Urgency) to Green (Low Urgency)
    processed_data['color_r'] = processed_data['urgency_score'].apply(lambda x: 255 if x > 50 else 0)
    processed_data['color_g'] = processed_data['urgency_score'].apply(lambda x: 0 if x > 50 else 255)

    people_layer = pdk.Layer(
        "ScatterplotLayer",
        processed_data,
        get_position='[lon, lat]',
        get_color='[color_r, color_g, 0, 160]',
        get_radius=30,
        pickable=True,
        auto_highlight=True
    )

    # Layer 2: The Fire (Heatmap/Circle)
    fire_data = pd.DataFrame([{'lon': fire_sim_lon, 'lat': fire_sim_lat}])
    fire_layer = pdk.Layer(
        "ScatterplotLayer",
        fire_data,
        get_position='[lon, lat]',
        get_color='[255, 69, 0, 200]',
        get_radius=400, # Fire radius
        stroked=True,
        filled=True,
        line_width_min_pixels=2,
    )

    # Layer 3: The Rescuer
    rescuer_data = pd.DataFrame([{'lon': rescuer_lon, 'lat': rescuer_lat}])
    rescuer_layer = pdk.Layer(
        "ScatterplotLayer",
        rescuer_data,
        get_position='[lon, lat]',
        get_color='[0, 128, 255, 255]',
        get_radius=50,
        stroked=True,
        line_width_min_pixels=3,
        get_line_color=[255, 255, 255]
    )

    # Layer 4: Routing (Lines from Rescuer to High Urgency Targets)
    routes_data = []
    if show_routes:
        for _, row in top_priorities.iterrows():
            routes_data.append({
                "start": [rescuer_lon, rescuer_lat],
                "end": [row['lon'], row['lat']],
                "name": row['id']
            })

    route_layer = pdk.Layer(
        "LineLayer",
        routes_data,
        get_source_position="start",
        get_target_position="end",
        get_color=[255, 255, 0], # Yellow lines
        get_width=5,
        pickable=True
    )

    # Render Map
    st.pydeck_chart(pdk.Deck(
        map_style=None, # Set to None to use default CARTO map (no API key required)
        initial_view_state=pdk.ViewState(
            latitude=40.6401,
            longitude=22.9444,
            zoom=13,
            pitch=50,
        ),
        layers=[fire_layer, people_layer, rescuer_layer, route_layer],
        tooltip={"text": "Target: {id}\nUrgency: {urgency_score}"}
    ))

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
