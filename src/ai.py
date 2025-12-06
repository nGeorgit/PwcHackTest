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

        # 1. General Situation
        total_high_risk = context_data.get('high_risk_count', 0)

        context_str = f"## Situation Summary\n"
        context_str += f"- High Urgency Cases: {total_high_risk}\n\n"

        # 2. Selected Citizen (Detailed View)
        selected = context_data.get('selected_citizen')
        if selected:
            context_str += "## Currently Selected Citizen (Focus)\n"
            context_str += f"- ID: {selected.get('id', 'N/A')}\n"
            context_str += f"- Name: {selected.get('fullname', 'Unknown')}\n"
            context_str += f"- Urgency Score: {int(selected.get('urgency_score', 0))}\n"
            context_str += f"- Notes: {selected.get('notes', 'None')}\n"
            context_str += f"- Medical Info: {selected.get('medical_info', 'None')}\n"
            context_str += f"- Mobility Issues: {selected.get('mobility', 'Unknown')}\n"
            context_str += "\n"

        # 3. Top Critical Targets
        top_targets = context_data.get('top_urgent_citizens', [])
        if top_targets:
            context_str += "## Top 5 Critical Targets (Recommendation)\n"
            for i, citizen in enumerate(top_targets, 1):
                context_str += f"{i}. ID {citizen.get('id')} ({citizen.get('fullname')}) - Score: {int(citizen.get('urgency_score', 0))}\n"

        return context_str

    @staticmethod
    def get_response(prompt: str, context_data: dict) -> str:
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

        system_message = (
            "You are the 'Aegis' Emergency Response Coordinator AI. "
            "Your role is to assist the rescue commander in prioritizing life-saving actions during a crisis.\n\n"
            "## Guidelines:\n"
            "- Be concise, direct, and professional.\n"
            "- Prioritize high-urgency cases (score > 50).\n"
            "- Use the provided context data to answer questions accurately.\n"
            "- If the user asks about a specific person, refer to the 'Currently Selected Citizen' section.\n"
            "- If asked for recommendations, suggest the 'Top Critical Targets'.\n\n"
            f"{formatted_context}"
        )

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]

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
