import numpy as np
import requests
import pandas as pd
from src.config import RANKING_API_URL

def fetch_rankings_from_api():
    """
    Fetches ranking data from the external Azure Function API.
    Returns a list of dicts or None if failed.
    """
    try:
        response = requests.get(RANKING_API_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching rankings: {e}")
        return None

def apply_ranking_logic(df):
    """
    Applies ranking logic:
    1. Tries to fetch from API.
    2. If successful, merges API data (risk_category, ai_score).
    3. If failed, falls back to local 'danger_level' and derives category.
    4. Returns sorted DataFrame.
    """
    api_data = fetch_rankings_from_api()
    
    # Initialize columns
    df['risk_category'] = 'Low'
    df['urgency_score'] = 0.0

    if api_data:
        # --- API SUCCESS PATH ---
        # Convert API list to DataFrame for easier merging
        ranking_df = pd.DataFrame(api_data)
        
        # Ensure we have 'id' for merging
        if 'id' in ranking_df.columns:
            # FORCE INTEGER IDs for merging
            # Coerce errors='coerce' turns non-ints into NaN, then we fill with 0 and cast to int
            # This handles cases where ID might be "P-101" (test data) vs 101 (real data)
            
            # 1. Clean Local DF 'id'
            # Remove non-digit characters if it's a string, or just cast if simple
            # Simple approach: try pd.to_numeric first
            df['id'] = pd.to_numeric(df['id'], errors='coerce').fillna(0).astype(int)
            
            # 2. Clean API DF 'id'
            ranking_df['id'] = pd.to_numeric(ranking_df['id'], errors='coerce').fillna(0).astype(int)

            # Merge logic
            # We left join to keep all citizens even if API misses some (though it shouldn't)
            # Suffixes: _local (original), _api (new)
            merged = df.merge(ranking_df, on='id', how='left', suffixes=('', '_api'))
            
            # Update risk_category and urgency_score from API columns
            # API returns 'risk_category' (e.g. "CRITICAL", "Low") and 'ai_score'
            
            # Fill NaNs for rows not in API (fallback to safe defaults)
            merged['risk_category'] = merged['risk_category_api'].fillna('Low')
            merged['urgency_score'] = merged['ai_score'].fillna(0.0)
            
            # Normalize risk category (Uppercase)
            merged['risk_category'] = merged['risk_category'].astype(str).str.upper()
            
            # Clean up temporary columns if any
            if 'risk_category_api' in merged.columns:
                del merged['risk_category_api']
            if 'ai_score' in merged.columns:
                del merged['ai_score']
                
            df = merged
        else:
            print("API response missing 'id' column. Falling back.")
            api_data = None # Trigger fallback

    if not api_data:
        # --- FALLBACK PATH ---
        print("Using local fallback logic.")
        if 'danger_level' in df.columns:
            # Map danger_level to risk_category
            # Thresholds: >75 Critical, >50 High, else Low
            def get_category(level):
                if level > 75:
                    return 'CRITICAL'
                elif level > 50:
                    return 'HIGH'
                else:
                    return 'LOW'
            
            df['risk_category'] = df['danger_level'].apply(get_category)
            df['urgency_score'] = df['danger_level'].astype(float)
        else:
            df['urgency_score'] = 0.0
            df['risk_category'] = 'LOW'

    # Sorting Logic
    # We want Critical first, then High, then Low.
    # Within categories, sort by urgency_score descending.
    
    # Create a helper for category sort order
    cat_order = {'CRITICAL': 3, 'HIGH': 2, 'LOW': 1, 'MEDIUM': 1} # Handle potentially other values
    
    # Create a temporary rank column
    df['cat_rank'] = df['risk_category'].map(lambda x: cat_order.get(x.upper(), 0))
    
    # Sort by Category Rank (desc), then Score (desc)
    df = df.sort_values(by=['cat_rank', 'urgency_score'], ascending=[False, False])
    
    # Drop temp column
    df = df.drop(columns=['cat_rank'])
    
    return df

# Deprecated but kept for compatibility if imported elsewhere temporarily
def calculate_urgency_score(df, fire_lat, fire_lon):
    return apply_ranking_logic(df)