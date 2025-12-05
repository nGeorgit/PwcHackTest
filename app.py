import streamlit as st
from openai import AzureOpenAI

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Hackathon MVP",
    page_icon="🚀",
    layout="centered"
)

# --- SIDEBAR: SETTINGS & DEBUGGING ---
with st.sidebar:
    st.header("⚙️ Configuration")
    # In a real hackathon, you might hardcode these or use st.secrets
    # But this input allows you to swap keys quickly if one burns out.
    api_key = st.text_input("Azure API Key", type="password")
    endpoint = st.text_input("Azure Endpoint", placeholder="https://your-resource.openai.azure.com/")
    deployment_name = st.text_input("Deployment Name", placeholder="gpt-4")
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# --- MAIN SETUP ---
st.title("🚀 My Hackathon MVP2")
st.caption("Powered by Azure OpenAI + Streamlit")

# 1. Initialize Chat History (The Fix for "Refresh Death")
# We check if 'messages' exists in session_state. If not, we create it.
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful AI assistant for a startup hackathon."}
    ]

# 2. Display Existing Chat History
# This loop ensures that when the app re-runs (which happens on every interaction),
# the old messages stay on screen.
for message in st.session_state.messages:
    if message["role"] != "system": # Hide system prompt from UI
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 3. Handle User Input
if prompt := st.chat_input("What is your question?"):
    
    # Check if keys are provided
    if not api_key or not endpoint:
        st.error("🚨 Please enter your Azure API Key and Endpoint in the sidebar!")
        st.stop()

    # Add User Message to UI and State
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 4. Generate Response (The "Magic")
    try:
        client = AzureOpenAI(
            api_key=api_key,
            api_version="2024-02-15-preview", # Check specific version at event
            azure_endpoint=endpoint
        )

        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model=deployment_name,
                messages=st.session_state.messages,
                stream=True, # Stream response for "hacker" feel
            )
            response = st.write_stream(stream)
        
        # Add Assistant Response to State
        st.session_state.messages.append({"role": "assistant", "content": response})

    except Exception as e:
        st.error(f"❌ Error: {e}")