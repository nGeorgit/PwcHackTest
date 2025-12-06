import numpy as np

def calculate_urgency_score(df, fire_lat, fire_lon):
    """
    Calculates a priority score based on features.
    Updated to use 'danger_level' from the dataset directly.
    """
    # Original logic commented out as requested
    # scores = []
    # for index, row in df.iterrows():
    #     score = 0
    #     # 1. Feature: Distance to Fire
    #     dist = np.sqrt((row['lat'] - fire_lat)**2 + (row['lon'] - fire_lon)**2)
    #     dist_score = max(0, 50 - (dist * 10000))
    #     score += dist_score
    #     # 2. Feature: Mobility
    #     score += (10 - row['mobility']) * 3
    #     # 3. Feature: Age
    #     if row['age'] > 70:
    #         score += 15
    #     elif row['age'] < 10:
    #         score += 10
    #     # 4. Feature: Medical History
    #     if row['has_disease']:
    #         score += 10
    #     scores.append(min(100, max(0, score)))
    # df['urgency_score'] = scores

    # New logic: Use danger_level directly
    if 'danger_level' in df.columns:
        df['urgency_score'] = df['danger_level']
    else:
        # Fallback if danger_level is missing (should not happen with new dataset)
        df['urgency_score'] = 0

    return df.sort_values(by='urgency_score', ascending=False)
