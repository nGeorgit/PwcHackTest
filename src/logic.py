import numpy as np

def calculate_urgency_score(df, fire_lat, fire_lon):
    """
    This is your 'AI' Model.
    It calculates a priority score (0-100) based on features.
    """
    scores = []

    for index, row in df.iterrows():
        score = 0

        # 1. Feature: Distance to Fire (Closer = Higher Urgency)
        dist = np.sqrt((row['lat'] - fire_lat)**2 + (row['lon'] - fire_lon)**2)
        dist_score = max(0, 50 - (dist * 10000)) # Normalize roughly
        score += dist_score

        # 2. Feature: Mobility (Lower Mobility = Higher Urgency)
        # We weight this heavily
        score += (10 - row['mobility']) * 3

        # 3. Feature: Age (Older = Higher Urgency)
        if row['age'] > 70:
            score += 15
        elif row['age'] < 10:
            score += 10

        # 4. Feature: Medical History
        if row['has_disease']:
            score += 10

        scores.append(min(100, max(0, score))) # Cap at 0-100

    df['urgency_score'] = scores
    return df.sort_values(by='urgency_score', ascending=False)
