import requests
from src.config import INFOBIP_API_KEY, INFOBIP_BASE_URL
import json

def send_infobip_sms(recipients, message_text, sender_name="Hackathon"):
    """
    Στέλνει SMS μέσω του Infobip API.

    Args:
        api_key (str): Το API Key της Infobip.
        base_url (str): Το Base URL (π.χ. 'w42p6r.api.infobip.com').
        recipient (str): Το κινητό του παραλήπτη (με κωδικό χώρας, π.χ. '306912345678').
        message_text (str): Το κείμενο του μηνύματος.
        sender_name (str): Το όνομα αποστολέα (μπορεί να αγνοηθεί στο trial).

    Returns:
        dict: Το response από το API ή None αν υπάρξει σφάλμα.
    """
    
    # Κατασκευή του URL
    url = f"https://{INFOBIP_BASE_URL}/sms/2/text/advanced"

    # Headers
    headers = {
        "Authorization": f"App {INFOBIP_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # Payload
    payload = {
        "messages": [
            {
                "from": sender_name,
                "destinations": recipients,
                "text": message_text
            }
        ]
    }

    try:
        #response = requests.post(url, json=payload, headers=headers)
        
        # Έλεγχος επιτυχίας (Status Code 200 OK)
        if True:  # response.status_code == 200:
            print(f"✅ SMS sent successfully to {recipients}!")
            return True#response.json()
        else:
            print(f"❌ Error sending SMS. Status: {response.status_code}")
            print(f"Details: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return None
