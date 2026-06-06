import pandas as pd
import numpy as np
import json

# ==============================================================================
# 1. DATA LOADING
# ==============================================================================
print("Loading pre-cleaned dataset...")
mec_data = pd.read_csv(r"data\cleaned_data_FULL_iqr_NEW.csv")

# ==============================================================================
# 2. STRICT BROWSER & GAME FILTERING
# ==============================================================================
print("Filtering tasks and strictly isolating Safari, Chrome, and Firefox...")
# Remove tasks missing hardware data
mec_data = mec_data[~mec_data['GameType'].isin(['Tova', 'mAID'])].copy()

# Keep ONLY Safari, Chrome, and Firefox
mec_data['Browser_Clean'] = mec_data['deviceModel'].str.split(' ').str[0]
mec_data = mec_data[mec_data['Browser_Clean'].isin(['Safari', 'Chrome', 'Firefox'])].copy()

# Map friendly game names
game_name_map = {
    "ISHIHARA": "Color Blindness Test", "COLOR_PICKING": "Color Swatch",
    "TASK_SWITCH_V2": "Sun & Moon", "BOXED": "Boxed", "FILTER": "Filter",
    "STROOP": "Color Tricker", "TNT": "Triangle Trace", "FLANKER": "Flanker",
    "SAAT_SUSTAINED": "Venus UFO", "SAAT_IMPULSIVE": "Mars UFO",
    "ADP": "Face Switch", "SPATIAL_CUEING": "Compass", "BRT": "Basic Response Time"
}
mec_data['GameType'] = mec_data['GameType'].map(game_name_map).fillna(mec_data['GameType'])

# ==============================================================================
# 3. FEATURE ENGINEERING & INDIVIDUAL VARIANCE TIERS
# ==============================================================================
print("Calculating intra-individual behavioral variance profiles...")

# Calculate base performance metrics
mec_data['FPS_CV'] = np.sqrt(mec_data['FPS_var']) / mec_data['FPS_mean']
mec_data['Profile_Combo'] = mec_data['systemMemorySize'].astype(str) + "GB_" + mec_data['GPU_Brand']

# Calculate Reaction Time Standard Deviation per individual participant
rt_std_per_person = mec_data.groupby('pid')['RT'].std().reset_index().rename(columns={'RT': 'RT_std'})

# Merge variance back into the main dataframe
mec_data = pd.merge(mec_data, rt_std_per_person, on='pid', how='left')

# Fill any NaNs from 1-trial participants with the median variance to prevent invisibly small dots
mec_data['RT_std'] = mec_data['RT_std'].fillna(mec_data['RT_std'].median())

# Bin variance into 4 distinct cosmic magnitude classes using quantiles
quantiles = mec_data['RT_std'].quantile([0.25, 0.50, 0.75]).values

def assign_star_size(val):
    if val <= quantiles[0]:
        return 2.5  # Hyper-Focused Stars (Tiny, sharp)
    elif val <= quantiles[1]:
        return 3.5  # Stable Stars (Standard)
    elif val <= quantiles[2]:
        return 4.5  # Drifting Stars (Larger)
    else:
        return 6.0  # Nebulous Stars (Large, diffuse)

mec_data['Star_Size'] = mec_data['RT_std'].apply(assign_star_size)

mec_data_filtered = mec_data.copy()

# ==============================================================================
# 4. GAME-AWARE CENTROID HUB COMPUTATION (Forced Reset Index Fix)
# ==============================================================================
print("Generating game-aware hardware, browser, and GPU centroid spaces...")

# Layer A: Full Hardware Profile Combo
centroid_hardware = mec_data_filtered.groupby(['GameType', 'Profile_Combo']).agg(
    {'FPS_mean': 'mean', 'FPS_CV': 'mean', 'RT': 'mean', 'pid': 'count'}
).rename(columns={'pid': 'Cluster_Size'}).reset_index()
centroid_hardware.rename(columns={'Profile_Combo': 'Hub_Key'}, inplace=True)

# Layer B: Pure Browser Engine
centroid_browser = mec_data_filtered.groupby(['GameType', 'Browser_Clean']).agg(
    {'FPS_mean': 'mean', 'FPS_CV': 'mean', 'RT': 'mean', 'pid': 'count'}
).rename(columns={'pid': 'Cluster_Size'}).reset_index()
centroid_browser.rename(columns={'Browser_Clean': 'Hub_Key'}, inplace=True)

# Layer C: Pure GPU Graphics Profile
centroid_gpu = mec_data_filtered.groupby(['GameType', 'GPU_Brand']).agg(
    {'FPS_mean': 'mean', 'FPS_CV': 'mean', 'RT': 'mean', 'pid': 'count'}
).rename(columns={'pid': 'Cluster_Size'}).reset_index()
centroid_gpu.rename(columns={'GPU_Brand': 'Hub_Key'}, inplace=True)

# Clean calculations of NaNs safely
centroid_hardware = centroid_hardware.replace({np.nan: None})
centroid_browser = centroid_browser.replace({np.nan: None})
centroid_gpu = centroid_gpu.replace({np.nan: None})
mec_data_filtered = mec_data_filtered.replace({np.nan: None})

# ==============================================================================
# 5. DICTIONARY MATRIX CONVERSION & JSON EXPORT
# ==============================================================================
print("Serializing cosmic records to clean JSON formats...")

# Include 'Star_Size' in the exported matrix
trials_json = mec_data_filtered[[
    'pid', 'GameType', 'FPS_mean', 'FPS_CV', 'RT', 
    'Browser_Clean', 'Profile_Combo', 'GPU_Brand', 'Star_Size'
]].to_dict(orient='records')

centroids_package = {
    "hardware": centroid_hardware.to_dict(orient='records'),
    "browser": centroid_browser.to_dict(orient='records'),
    "gpu": centroid_gpu.to_dict(orient='records')
}

with open('trials.json', 'w') as f:
    json.dump(trials_json, f)
    
with open('centroids.json', 'w') as f:
    json.dump(centroids_package, f)

print(f"\nSuccess! Filtered dataset contains {len(mec_data_filtered)} total trials.")