import folium
from streamlit_folium import st_folium
from src.speech import recognize_speech
from src.sms import send_infobip_sms
from src.config import DEFAULT_LAT, DEFAULT_LON
import pandas as pd
import streamlit as st

def render_chat_interface(messages, on_voice_input=None):
    """
    Renders the chat interface. 
    Uses a placeholder to clear the 'Review' UI immediately upon clicking Retry.
    """
    st.sidebar.subheader("🤖 AI Mission Support")

  
        
    # 1. Initialize draft state
    if "voice_draft" not in st.session_state:
        st.session_state.voice_draft = None

    # 2. Display Chat History
    for message in messages:
        with st.sidebar.chat_message(message["role"]):
            st.sidebar.markdown(message["content"])


    # 3. Voice Input Logic
    
    # CASE A: No draft -> Show Start Button
    if st.session_state.voice_draft is None:
        if st.sidebar.button("Start Voice Input"):
            voice_input = recognize_speech()
            if voice_input:
                st.session_state.voice_draft = voice_input
                st.rerun()

    # CASE B: Draft exists -> Show Review Controls
    else:
        # Create a PLACEHOLDER. This is the magic box we can empty later.
        review_ui = st.sidebar.empty()

        # Render the Review UI *inside* the placeholder container
        with review_ui.container():
            st.info(f"**Review:** \"{st.session_state.voice_draft}\"")
            col1, col2 = st.columns(2)
            
            # We assign the button clicks to variables
            send_clicked = col1.button("Send", use_container_width=True)
            retry_clicked = col2.button("Retry", use_container_width=True)

        # --- LOGIC HANDLING ---
        
        if send_clicked:
            if on_voice_input:
                on_voice_input(st.session_state.voice_draft)
                st.session_state.voice_draft = None
                st.rerun()

        if retry_clicked:
            # 1. VISUAL TRICK: Clear the Review UI (text & buttons) immediately!
            review_ui.empty()
            
            # 2. NOW listen. The 'Review' box is gone, so the 'Listening' status 
            #    (from speech.py) will appear clearly, just like the first time.
            new_voice_input = recognize_speech()
            
            # 3. Update the draft with the new attempt
            if new_voice_input:
                st.session_state.voice_draft = new_voice_input
            else:
                # If they stayed silent or canceled, reset to the beginning
                st.session_state.voice_draft = None
                
            st.rerun()
    if "last_audio" in st.session_state and st.session_state.last_audio:
            st.sidebar.audio(st.session_state.last_audio, format="audio/wav")
    return st.sidebar.chat_input("Ask about the situation...")

def render_sidebar(messages, on_voice_input=None):
    """Renders the sidebar controls."""
    st.sidebar.header("🚒 Operation Controls")
    
    # Pass the callback down
    return render_chat_interface(messages, on_voice_input)



def render_header():
    """Renders the main header with an SOS action."""
    col_head1, col_head2 = st.columns([3, 1])
    
    with col_head1:
        st.title("🛡️ Aegis: Intelligent Rescue Response")
        st.markdown("Real-time prioritization of vulnerable populations during crisis.")
    
    with col_head2:
        st.metric(label="System Status", value="ACTIVE", delta="CRITICAL ALERT")
        
        # --- SOS BUTTON ADDED HERE ---
        # Using type="primary" to make it stand out visually
        if st.button("Sent SOS SMS", type="primary", use_container_width=True):
            # 1. Δείχνουμε ότι κάτι συμβαίνει (UX)
            with st.spinner("Contacting Infobip API..."):
                result = None
                # 2. Καλούμε τη συνάρτηση
                result = send_infobip_sms(
                    recipients=[{'to': '306943428465'}, {'to': '4915202042012'}],#, {'to':'306980800178'}],  # nikos 306943428465, theodora 4915202042012, veroniki 306980800178
                    message_text="🆘 SOS ALERT! Critical situation reported via PwC Hackathon App. 📍 Check dashboard."
                )
            
            # 3. Ελέγχουμε το αποτέλεσμα και ενημερώνουμε το UI
            if result:
                st.toast("🚨 SOS SMS has been broadcasted!", icon="⚠️")
                st.success("Message sent successfully!") # Προαιρετικό, μένει στην οθόνη
            else:
                st.error("Failed to send SMS. Check console/logs.")
            
def render_map(processed_data, fire_df, center_coords=None, zoom=10, selected_id=None):
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
        center_coords = [DEFAULT_LAT, DEFAULT_LON]

    m = folium.Map(location=center_coords, zoom_start=zoom)

        # Layer 1: Fire Location
    for fire_id, fire_group in fire_df.groupby('fire_id'):
            

            # Extract the list of coordinates [[lat, lon], [lat, lon]] for this polygon
            locations = fire_group[['lat', 'lon']].values.tolist()

            # Visual Logic: Fire is usually Red. 
            # If selected, we make the border thicker and opacity higher to make it pop.
            color = "#DA101090"  # Dark Red for border
            fill_color = 'red' # Standard Red for fill
           
         

            popup_html = f"""
            <b>Fire Zone ID:</b> {fire_id}<br>
            <b>Type:</b> Active Perimeter<br>
            <b>Vertices:</b> {len(locations)}
            """

            folium.Polygon(
                locations=locations,
                color=color,
                fill=True,
                fill_color=fill_color,
                # popup=folium.Popup(popup_html, max_width=200, show=is_selected_fire),
                # tooltip=f"Fire Zone {fire_id}"
            ).add_to(m)

    # Layer 2: The People
    for _, row in processed_data.iterrows():
        if row['present'] == 0:
            continue  # Skip non-present citizens
        is_selected = (selected_id is not None) and (row['id'] == selected_id)

        # Color logic: Red (High Urgency) to Green (Low Urgency)
        if row['risk_category'] == 'CRITICAL':
            color = 'red'
        elif row['risk_category'] == 'HIGH':
            color = 'orange'
        else:
            color = 'green'

        # Helper to safely get life_support
        life_support = "Yes" if row.get('life_support', 0) == 1 else "No"
        notes = row.get('notes', 'N/A')
        fullname = row.get('fullname', 'Unknown')

        should_show = (row['id'] == selected_id)

        popup_html = f"""
        <b>ID:</b> {row['id']}<br>
        <b>Name:</b> {fullname}<br>
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
            fill_color=color,
            fill_opacity=0.7,
            popup=folium.Popup(popup_html, max_width=250, show=should_show),
            tooltip=f"{fullname} ({row['id']})"
        ).add_to(m)
        


    # Render Map using streamlit-folium with maximized size
    return st_folium(m, use_container_width=True, height=700)

def render_citizen_list(full_data, selected_id=None, widget_key="citizen_list"):
    """
    Renders the citizen list as a selectable dataframe with visual highlighting.
    Filters out citizens who are not present (present == 0).
    """
    st.subheader("Citizens")

    # 1. Detail View
    # We use full_data here to ensure we can still see details of a selected person 
    # even if they just became "not present" in the latest update.
    if selected_id is not None:
        selected_row = full_data[full_data['id'] == selected_id]
        if not selected_row.empty:
            row = selected_row.iloc[0]
            st.info(f"🎯 **Selected:** {row.get('fullname', row['id'])}")

    # --- FILTERING LOGIC START ---
    # Create a new dataframe for the list view that excludes non-present citizens
    if 'present' in full_data.columns:
        list_source = full_data[full_data['present'] != 0].copy()
    else:
        list_source = full_data.copy()
    # --- FILTERING LOGIC END ---

    # 2. Prepare Data
    cols = ['id', 'fullname', 'risk_category', 'life_support']
    # Ensure we use list_source here, not full_data
    available_cols = [c for c in cols if c in list_source.columns]
    display_df = list_source[available_cols].copy()

    # 3. Define the Highlighter Logic
    def highlight_selected(row):
        if selected_id is not None and row['id'] == selected_id:
            return ['background-color: #ffffb3; color: black'] * len(row)
        return [''] * len(row)

    # 4. Apply the Style
    styled_df = display_df.style.apply(highlight_selected, axis=1)

    # 5. Render with Dynamic Key
    return st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun",
        height=600,
        key=widget_key
    )