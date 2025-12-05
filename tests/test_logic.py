import unittest
import pandas as pd
import numpy as np
from src.logic import calculate_urgency_score
from src.data import DataManager

class TestLogic(unittest.TestCase):
    def test_urgency_score_calculation(self):
        # Create a mock dataframe
        data = {
            'id': ['1', '2'],
            'lat': [40.6401, 40.6402],
            'lon': [22.9444, 22.9445],
            'age': [30, 80],
            'mobility': [10, 2],
            'has_disease': [False, True]
        }
        df = pd.DataFrame(data)

        # Fire at the first person's location
        fire_lat = 40.6401
        fire_lon = 22.9444

        # Run calculation
        result = calculate_urgency_score(df, fire_lat, fire_lon)

        # Person 2 should have higher score because:
        # - Older (80 > 70) -> +15
        # - Low mobility (2) -> (10-2)*3 = +24
        # - Disease -> +10
        # - Distance -> slightly further but distance score is max(0, 50 - dist*10000).
        #   dist is small (~0.00014). 50 - 1.4 = 48.6.
        # Total approx: 15 + 24 + 10 + 48 = ~97

        # Person 1:
        # - Young -> 0
        # - High mobility (10) -> 0
        # - No disease -> 0
        # - Distance -> 0 (at fire) -> 50
        # Total: 50

        # Check if sorted correctly (descending)
        self.assertEqual(result.iloc[0]['id'], '2')
        self.assertEqual(result.iloc[1]['id'], '1')

        # Check if scores are within expected ranges
        score_p2 = result[result['id'] == '2']['urgency_score'].values[0]
        score_p1 = result[result['id'] == '1']['urgency_score'].values[0]

        self.assertTrue(score_p2 > score_p1)
        self.assertTrue(0 <= score_p1 <= 100)
        self.assertTrue(0 <= score_p2 <= 100)

class TestData(unittest.TestCase):
    def test_data_generation(self):
        df = DataManager.load_vulnerable_citizens(n=10)
        self.assertEqual(len(df), 10)
        expected_cols = ['id', 'lat', 'lon', 'age', 'mobility', 'has_disease', 'oxygen_level']
        for col in expected_cols:
            self.assertIn(col, df.columns)

if __name__ == '__main__':
    unittest.main()
