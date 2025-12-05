import pandas as pd
import numpy as np

class DataManager:
    @staticmethod
    def load_vulnerable_citizens(n=50, center_lat=40.6401, center_lon=22.9444):
        """
        Generates fake data for Thessaloniki (or target area).
        Features: Age, Moving Ability (0-10), Chronic Disease (Boolean).
        """
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
