class AIAssistant:
    @staticmethod
    def get_response(prompt: str, context_data: dict) -> str:
        """
        Mock AI Response Logic.
        In the future, this can be replaced with AzureOpenAI calls.

        Args:
            prompt: User input string
            context_data: Dictionary containing real-time context (e.g., top priorities, stats)
        """
        prompt_lower = prompt.lower()

        if "route" in prompt_lower:
            target_id = context_data.get('top_target_id', 'Unknown')
            return f"Calculating optimal path... The most efficient route is to Target {target_id} first due to low mobility scores. Traffic data suggests avoiding Main Street."

        elif "count" in prompt_lower or "how many" in prompt_lower:
            high_risk_count = context_data.get('high_risk_count', 0)
            return f"There are currently {high_risk_count} individuals in the 'High Risk' category within the blast radius."

        else:
            return "Copy that. Maintaining monitoring of vital signs. Routing updated based on fire spread predictions."
