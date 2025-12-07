

# 🛡️ Aegis: Intelligent Rescue Response

**Aegis** is a real-time decision-support system designed to assist emergency responders during natural disasters (such as fires, floods, and earthquakes). It prioritizes vulnerable populations by analyzing health data, mobility constraints, and proximity to danger zones, providing actionable guidance through an AI-powered interface.

## 🚀 Key Features

  * **📍 Live Tactical Map**: Visualizes vulnerable citizens and active danger zones (e.g., fire perimeters) on an interactive map using Folium. Color-coded markers indicate urgency levels (Critical, High, Low).
  * **🤖 AI Mission Support**: Powered by **Azure OpenAI**, the "SAFEcube" assistant provides real-time operational advice, explains risk assessments, and suggests rescue strategies based on specific citizen data.
  * **🗣️ Voice Command & Audio Feedback**: Hands-free interaction using **Azure Cognitive Services**. Responders can speak commands and receive audio briefings (Text-to-Speech) in English or Greek.
  * **🚨 SOS Broadcasting**: Integrated with **Infobip API** to send immediate SMS alerts to defined recipients in critical situations.
  * **⚡ Dynamic Risk Scoring**: Calculates urgency scores based on distance from danger, health sensors (e.g., oxygen levels), and mobility issues, prioritizing the most critical cases automatically.
  * **☁️ Cloud Integration**: Fetches real-time citizen and hazard data from **Azure Blob Storage**.

## 🛠️ Architecture & Tech Stack

  * **Frontend**: [Streamlit](https://streamlit.io/) (Python)
  * **AI/LLM**: Azure OpenAI (GPT-4o/GPT-3.5)
  * **Voice Services**: Azure Speech SDK (Speech-to-Text & Text-to-Speech)
  * **Data Storage**: Azure Blob Storage & Local JSON
  * **Mapping**: Folium & Streamlit-Folium
  * **Communications**: Infobip SMS API
  * **Logic**: Custom ranking algorithms & Azure Functions integration

## 📂 Project Structure

```text
.
├── app.py                  # Main application entry point
├── startup.sh              # Shell script to launch the app
├── requirements.txt        # Python dependencies
├── .gitignore              # Git ignore rules
├── LICENSE.txt             # MIT License
├── src/
│   ├── ai.py               # Azure OpenAI integration logic
│   ├── speech.py           # Azure Speech (STT/TTS) logic
│   ├── sms.py              # Infobip SMS sending function
│   ├── logic.py            # Urgency scoring and ranking algorithms
│   ├── data.py             # Data loading (Local & Azure Blob)
│   ├── ui.py               # UI components (Sidebar, Map, Chat)
│   ├── config.py           # Configuration & Environment variables
│   └── blod_util.py        # Azure Blob Storage utilities
├── tests/
│   ├── test_ai.py          # Unit tests for AI module
│   └── test_logic.py       # Unit tests for scoring logic
└── dummy_data/
    └── dataset_250_finalDEL.json # Sample citizen dataset
```

## ⚙️ Setup & Installation

### Prerequisites

  * Python 3.9+
  * Azure Cloud Account (for OpenAI, Speech, Blob Storage)
  * Infobip Account (for SMS)

### 1\. Clone the Repository

```bash
git clone <repository-url>
cd <repository-folder>
```

### 2\. Install Dependencies

It is recommended to use a virtual environment.

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3\. Configure Environment Variables

Create a `.env` file in the root directory and add your API keys:

```env
# Map Defaults
DEFAULT_LAT=40.6401
DEFAULT_LON=22.9444
RESCUER_LAT=38.0417850
RESCUER_LON=23.995306

# Azure OpenAI
AZURE_OPENAI_API_KEY=your_openai_key
AZURE_OPENAI_ENDPOINT=your_openai_endpoint
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2024-12-01-preview

# Azure Speech Service
SPEECH_KEY=your_speech_key
SPEECH_REGION=your_speech_region

# Azure Blob Storage
STORAGE_CONN_STRING=your_connection_string

# Ranking API (Optional External Logic)
RANKING_API_URL=your_azure_function_url

# Infobip SMS
INFOBIP_API_KEY=your_infobip_key
INFOBIP_BASE_URL=your_infobip_url
```

## 🚀 Usage

You can run the application directly using Streamlit:

```bash
streamlit run app.py
```

Or use the provided startup script:

```bash
bash startup.sh
```

The application will launch on `http://localhost:8501` (or the port specified in the script).

## 🧪 Testing

To run the unit tests for the logic and AI modules:

```bash
python -m unittest discover tests
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE.txt](https://www.google.com/search?q=LICENSE.txt) file for details.

## 👥 Team

**PwC Hackathon Team**
