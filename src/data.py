import pandas as pd
import numpy as np
from src.blod_util import fetch_json_from_blob
import json

class DataManager:
    @staticmethod
    def load_vulnerable_citizens(n=50, center_lat=40.6401, center_lon=22.9444):

        data = []
        for i in range(n):
            # Random location around center
            lat = center_lat + np.random.normal(0, 0.005)
            lon = center_lon + np.random.normal(0, 0.005)

            # Random features
            age = np.random.randint(20, 95)
            mobility = np.random.randint(1, 11) # 1 = bedridden, 10 = athlete
            has_disease = np.random.choice([True, False], p=[0.3, 0.7])
            oxygen_sensor = np.random.randint(90, 100) # Mock health sensor

            data.append({
                "id": f"P-{100+i}",
                "lat": lat,
                "lon": lon,
                "age": age,
                "mobility": mobility,
                "has_disease": has_disease,
                "oxygen_level": oxygen_sensor
            })
        return pd.DataFrame(data)

    @staticmethod
    def load_data_from_local_json(filepath):
        """
        Loads data from a specific JSON file structure.
        Expected fields: id, fullname, coordinates(lat, lon), gender, life_support,
        vulnerability_score, notes, present, distance_from_danger, danger_level
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Flatten coordinates
            processed_data = []
            for item in data:
                entry = item.copy()
                coords = entry.pop('coordinates', {})
                entry['lat'] = coords.get('lat')
                entry['lon'] = coords.get('lon')
                processed_data.append(entry)

            return pd.DataFrame(processed_data)
        except Exception as e:
            print(f"Error loading JSON data: {e}")
            return pd.DataFrame()
        
    @staticmethod
    def load_citizen_data_from_blob():
        """
        Loads citizen data JSON from Azure Blob Storage.
        """
        json_data = fetch_json_from_blob("dataset_250_final.json")
        if not json_data:
            return pd.DataFrame()

        # Flatten coordinates
        processed_data = []
        for item in json_data:
            entry = item.copy()
            coords = entry.pop('coordinates', {})
            entry['lat'] = coords.get('lat')
            entry['lon'] = coords.get('lon')
            processed_data.append(entry)

        return pd.DataFrame(processed_data)
