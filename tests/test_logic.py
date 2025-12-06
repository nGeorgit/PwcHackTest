import unittest
import pandas as pd
import numpy as np
import os
from src.logic import calculate_urgency_score
from src.data import DataManager

class TestLogic(unittest.TestCase):
    def test_urgency_score_calculation(self):
        # Create a mock dataframe with new fields
        data = {
            'id': ['1', '2', '3'],
            'lat': [40.6401, 40.6402, 40.6403],
            'lon': [22.9444, 22.9445, 22.9446],
            'danger_level': [20, 90, 50]
        }
        df = pd.DataFrame(data)

        # Fire location is ignored in new logic
        fire_lat = 0
        fire_lon = 0

        # Run calculation
        result = calculate_urgency_score(df, fire_lat, fire_lon)

        # Check if urgency_score is assigned correctly from danger_level
        self.assertEqual(result[result['id'] == '1']['urgency_score'].values[0], 20)
        self.assertEqual(result[result['id'] == '2']['urgency_score'].values[0], 90)
        self.assertEqual(result[result['id'] == '3']['urgency_score'].values[0], 50)

        # Check if sorted correctly (descending by urgency_score)
        self.assertEqual(result.iloc[0]['id'], '2') # 90
        self.assertEqual(result.iloc[1]['id'], '3') # 50
        self.assertEqual(result.iloc[2]['id'], '1') # 20

    def test_urgency_score_missing_danger_level(self):
        # Fallback case
        data = {
            'id': ['1'],
            'lat': [40.0],
            'lon': [22.0]
        }
        df = pd.DataFrame(data)
        result = calculate_urgency_score(df, 0, 0)
        self.assertEqual(result.iloc[0]['urgency_score'], 0)

class TestData(unittest.TestCase):
    def test_data_generation(self):
        # Test original generation method
        df = DataManager.load_vulnerable_citizens(n=10)
        self.assertEqual(len(df), 10)
        expected_cols = ['id', 'lat', 'lon', 'age', 'mobility', 'has_disease', 'oxygen_level']
        for col in expected_cols:
            self.assertIn(col, df.columns)

    def test_json_loading(self):
        # Test new JSON loading method using the existing dummy data
        json_path = 'dummy_data/dataset_250_final.json'
        if os.path.exists(json_path):
            df = DataManager.load_data_from_json(json_path)
            self.assertFalse(df.empty)
            self.assertIn('lat', df.columns)
            self.assertIn('lon', df.columns)
            self.assertIn('danger_level', df.columns)
            self.assertIn('fullname', df.columns)
            self.assertEqual(len(df), 250)
