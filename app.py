import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import math

# -----------------------------------------------------------------------------
# 1. CONFIGURATION & PAGE SETUP
# -----------------------------------------------------------------------------
st.set_page_config(layout="wide", page_title="RescuerAI - Emergency Command", page_icon="🚑")

# Custom CSS for that "Command Center" feel
st.markdown("""
<style>
    .reportview-container {
        background: #0e1117;
    }
    .big-font {
        font-size:20px !important;
        font-weight: bold;
    }
    .urgent {
        color: #ff4b4b;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. MOCK DATA GENERATION (Simulating IoT/Government Database)
# -----------------------------------------------------------------------------
@st.cache_data
def load_vulnerable_citizens(n=50, center_lat=40.6401, center_lon=22.9444):
    """
    Generates fake data for Thessaloniki (or target area).
    Features: Age, Moving Ability (0-10), Chronic Disease (Boolean).
    """
    data = []
    for i in range(n):
        # Random location around center
        lat = center_lat + np.random.normal(0, 0.005)
        lon = center_lon + np.random.normal(0, 0.005)
        
        # Random features
        age = np.random.randint(20, 95)
        mobility = np.random.randint(1, 11) # 1 = bedridden, 10 = athlete
        has_disease = np.random.choice([True, False], p=[0.3, 0.7])
        oxygen_sensor = np.random.randint(90, 100) # Mock health sensor
        
        data.append({
            "id": f"P-{100+i}",
            "lat": lat,
            "lon": lon,
            "age": age,
            "mobility": mobility,
            "has_disease": has_disease,
            "oxygen_level": oxygen_sensor
        })
    return pd.DataFrame(data)

# -----------------------------------------------------------------------------
# 3. AI LOGIC: RANKING ALGORITHM
# -----------------------------------------------------------------------------
def calculate_urgency_score(df, fire_lat, fire_lon):
    """
    This is your 'AI' Model. 
    It calculates a priority score (0-100) based on features.
    """
    scores = []
    
    for index, row in df.iterrows():
        score = 0
        
        # 1. Feature: Distance to Fire (Closer = Higher Urgency)
        dist = np.sqrt((row['lat'] - fire_lat)**2 + (row['lon'] - fire_lon)**2)
        dist_score = max(0, 50 - (dist * 10000)) # Normalize roughly
        score += dist_score
        
        # 2. Feature: Mobility (Lower Mobility = Higher Urgency)
        # We weight this heavily
        score += (10 - row['mobility']) * 3
        
        # 3. Feature: Age (Older = Higher Urgency)
        if row['age'] > 70:
            score += 15
        elif row['age'] < 10:
            score += 10
            
        # 4. Feature: Medical History
        if row['has_disease']:
            score += 10
            
        scores.append(min(100, max(0, score))) # Cap at 0-100
        
    df['urgency_score'] = scores
    return df.sort_values(by='urgency_score', ascending=False)

# -----------------------------------------------------------------------------
# 4. UI LAYOUT & MAIN LOGIC
# -----------------------------------------------------------------------------

# Sidebar: Controls
st.sidebar.header("🚒 Operation Controls")
show_routes = st.sidebar.checkbox("Show Rescue Routes", value=True)
fire_sim_lat = st.sidebar.slider("Fire Latitude", 40.6300, 40.6500, 40.6401)
fire_sim_lon = st.sidebar.slider("Fire Longitude", 22.9300, 22.9600, 22.9444)
rescuer_lat = 40.6350
rescuer_lon = 22.9400

# Main Header
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.title("🛡️ Aegis: Intelligent Rescue Response")
    st.markdown("Real-time prioritization of vulnerable populations during crisis.")
with col_head2:
    st.metric(label="System Status", value="ACTIVE", delta="CRITICAL ALERT")

# Load and Process Data
raw_data = load_vulnerable_citizens()
processed_data = calculate_urgency_score(raw_data, fire_sim_lat, fire_sim_lon)

# Top 3 Priorities for Routing
top_priorities = processed_data.head(3)

# -----------------------------------------------------------------------------
# 5. MAP VISUALIZATION (PyDeck)
# -----------------------------------------------------------------------------
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

# -----------------------------------------------------------------------------
# 6. DETAILED DATA & CHAT
# -----------------------------------------------------------------------------
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 Priority Extraction List")
    # Display the top targets nicely
    for i, row in top_priorities.iterrows():
        with st.container():
            st.warning(f"🚨 **{row['id']}** | Urgency: {int(row['urgency_score'])}/100")
            st.write(f"Age: {row['age']} | Mobility: {row['mobility']}/10 | Disease: {row['has_disease']}")
            st.progress(int(row['urgency_score']))
    
    with st.expander("View Full Database"):
        st.dataframe(processed_data[['id', 'age', 'mobility', 'has_disease', 'urgency_score']])

with col2:
    st.subheader("🤖 AI Mission Support")
    
    # Simple Session State for Chat
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Initial greeting from AI
        st.session_state.messages.append({
            "role": "assistant", 
            "content": f"Briefing: Fire detected at {fire_sim_lat:.4f}, {fire_sim_lon:.4f}. I have analyzed sensor data. {len(top_priorities)} critical targets identified requiring immediate evacuation based on mobility and proximity. Awaiting instructions."
        })

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    if prompt := st.chat_input("Ask about the situation..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Mock AI Response Logic (You would connect LLM here normally)
        with st.chat_message("assistant"):
            response = ""
            if "route" in prompt.lower():
                response = f"Calculating optimal path... The most efficient route is to Target {top_priorities.iloc[0]['id']} first due to low mobility scores. Traffic data suggests avoiding Main Street."
            elif "count" in prompt.lower() or "how many" in prompt.lower():
                response = f"There are currently {len(processed_data[processed_data['urgency_score'] > 70])} individuals in the 'High Risk' category within the blast radius."
            else:
                response = "Copy that. Maintaining monitoring of vital signs. Routing updated based on fire spread predictions."
            
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})