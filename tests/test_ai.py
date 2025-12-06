import unittest
from unittest.mock import MagicMock, patch
from src.ai import AIAssistant

class TestAIAssistant(unittest.TestCase):

    def setUp(self):
        self.context_data = {
            'high_risk_count': 10,
            'selected_citizen': {
                'id': '123',
                'fullname': 'John Doe',
                'urgency_score': 85,
                'notes': 'Critical',
                'medical_info': 'Diabetic',
                'mobility': 'Low'
            },
            'top_urgent_citizens': [
                {'id': '101', 'fullname': 'Jane', 'urgency_score': 90},
                {'id': '102', 'fullname': 'Bob', 'urgency_score': 88}
            ]
        }

    def test_format_context(self):
        """Test if context is formatted correctly into string."""
        formatted = AIAssistant._format_context(self.context_data)

        self.assertIn("High Urgency Cases: 10", formatted)
        self.assertIn("John Doe", formatted)
        self.assertIn("Diabetic", formatted)
        self.assertIn("Top 5 Critical Targets", formatted)
        self.assertIn("Jane", formatted)
        self.assertIn("Bob", formatted)

    @patch('src.ai.AzureOpenAI')
    @patch('src.ai.AZURE_OPENAI_API_KEY', 'dummy_key')
    @patch('src.ai.AZURE_OPENAI_ENDPOINT', 'dummy_endpoint')
    @patch('src.ai.AZURE_OPENAI_DEPLOYMENT_NAME', 'dummy_deployment')
    def test_get_response_success(self, mock_azure):
        """Test successful API call."""

        # Mock the client and response
        mock_client = MagicMock()
        mock_azure.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices[0].message.content = "This is a mock response."
        mock_client.chat.completions.create.return_value = mock_response

        response = AIAssistant.get_response("Hello", self.context_data)

        self.assertEqual(response, "This is a mock response.")
        mock_client.chat.completions.create.assert_called_once()

    @patch('src.ai.AZURE_OPENAI_API_KEY', None)
    def test_get_response_missing_config(self):
        """Test response when config is missing."""
        response = AIAssistant.get_response("Hello", self.context_data)
        self.assertIn("configuration is missing", response)

if __name__ == '__main__':
    unittest.main()
