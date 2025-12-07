import os
from openai import AzureOpenAI
from src.config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_DEPLOYMENT_NAME
)

class AIAssistant:
    @staticmethod
    def _format_context(context_data: dict) -> str:
        """Helper to format the context dictionary into a readable string for the LLM."""

        # # 1. General Situation
        # total_high_risk = context_data.get('high_risk_count', 0)

        # context_str = f"## Situation Summary\n"
        # context_str += f"- High Urgency Cases: {total_high_risk}\n\n"

        # 2. Selected Citizen (Detailed View)
        # print()
        # selected = context_data.get('selected_citizen')
        # print("selected_________________________________:", selected)
        # if selected:
        #     context_str += "## Currently Selected Citizen (Focus)\n"
        #     context_str += f"- ID: {selected.get('id', 'N/A')}\n"
        #     context_str += f"- Name: {selected.get('fullname', 'Unknown')}\n"
        #     context_str += f"- Notes: {selected.get('notes', 'None')}\n"
        #     context_str += f"- Medical Info: {selected.get('medical_info', 'None')}\n"
        #     context_str += f"- Mobility Issues: {selected.get('mobility', 'Unknown')}\n"
        #     context_str += "\n"

        # # 3. Top Critical Targets
        # top_targets = context_data.get('top_critical_citizens', [])
        # if top_targets:
        #     context_str += "##Critical Targets\n"
        #     for i, citizen in enumerate(top_targets, 1):
        #         context_str += f"{i}. ID {citizen.get('id')} ({citizen.get('fullname')}) - Score: {int(citizen.get('urgency_score', 0))}\n"

        return context_data

    @staticmethod
    def get_response(prompt: str, context_data: dict, chat_history: list = None) -> str:
        """
        Generates a response using Azure OpenAI based on the user prompt and system context.

        Args:
            prompt: User input string.
            context_data: Dictionary containing real-time context.
        """

        # 1. Check Configuration
        if not all([AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT_NAME]):
            return "⚠️ System Alert: Azure OpenAI configuration is missing. Please check your environment variables."

        # 2. Initialize Client
        try:
            client = AzureOpenAI(
                api_key=AZURE_OPENAI_API_KEY,
                api_version=AZURE_OPENAI_API_VERSION,
                azure_endpoint=AZURE_OPENAI_ENDPOINT
            )
        except Exception as e:
            return f"⚠️ System Alert: Failed to initialize AI client. Error: {str(e)}"

        # 3. Build System Prompt with Context
        formatted_context = AIAssistant._format_context(context_data)

        # system_message = (
        #     "You are the 'Aegis' Emergency Response Coordinator AI. "
        #     "Your role is to assist the rescue commander in prioritizing life-saving actions during a crisis.\n\n"
        #     "## Guidelines:\n"
        #     "- Be concise, direct, and professional.\n"
        #     "- Prioritize high-urgency cases (score > 50).\n"
        #     "- Use the provided context data to answer questions accurately.\n"
        #     "- If the user asks about a specific person, refer to the 'Currently Selected Citizen' section.\n"
        #     "- If asked for recommendations, suggest the 'Top Critical Targets'.\n\n"
        #     f"{formatted_context}"
        # )
        
        system_message = ("""
You are SAFEcube, an AI Rescue Agent assisting field responders during natural disasters (fires, floods, earthquakes).
Your role is to help rescuers make fast, safe and well-justified decisions using ONLY the data provided in the JSON dataset of citizens.

---------------------------
ROLE & BEHAVIOR
---------------------------
• You act as a real-time decision-support assistant.
• Be concise, operational, and focused on safety.
• Prioritize clarity over long explanations.
• Never invent medical or location details not included in the dataset.
• If someone asks an ID that doesn't exist in the dataset say that you can't answer.

---------------------------
YOUR CAPABILITIES
---------------------------
You must be able to:
1. Read the citizen JSON data.
2. Use the data to answer to the rescuer accurately.
3. Explain your reasoning.
   When giving a recommendation, always include a short explanation: "Προτείνεται επειδή: ..."
4. Provide rescue guidance.
   Use the "notes" field (or other relevant data) to generate actionable instructions for the rescuer.
5. Answer structured questions from the rescuer (e.g., "Who has the highest risk?")
6. Provide concise summaries.

---------------------------
TONE & STYLE
---------------------------
• Short and mission-critical.
• Avoid technical jargon.
• Always provide next steps ("Δράση: …").

---------------------------
SAFETY RULES
---------------------------
• Do not give medical advice beyond basic first-aid and safety actions.
• Do not hallucinate data.
• If unsure, ask for clarification.

---------------------------
RESPONSE FORMAT
---------------------------
Use Greek and structure your response clearly:


---------------------------
[DATA INPUT - Το JSON που έχει φιλτραριστεί]
Below is the dataset you must use to answer the rescuer's questions:"""

f"""{formatted_context}"""
"""

INSTRUCTIONS ON MISSING DATA:
Άμα η παραπάνω λίστα δεδομένων είναι κενή ή το άτομο δεν είναι παρόν, μην βγάζεις οδηγίες διάσωσης.
""")

        # messages = [
        #     {"role": "system", "content": system_message},
        #     {"role": "user", "content": prompt}
        # ]
        
        messages = [{"role": "system", "content": system_message}]
        
        if chat_history:
            messages.extend(chat_history)

        # 3. Append the Current Prompt
        messages.append({"role": "user", "content": prompt})

        # 4. Call API
        try:
            response = client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=messages,
                temperature=0.3, # Low temperature for more factual/consistent responses
                max_tokens=300
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"⚠️ System Alert: Communication with AI module failed. Error: {str(e)}"
