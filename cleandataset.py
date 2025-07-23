import pandas as pd

# 1. Load the raw dataset
df = pd.read_csv("planets.csv")

# 2. Define your six key features
key_features = ["pl_rade", "pl_bmasse", "pl_eqt", "st_teff", "st_rad", "st_mass"]

# 3. Drop only those rows where _all_ key features are NaN
#    (so you keep any planet that has at least one of the six measurements)
df_clean = df.dropna(subset=key_features, how="all").copy()

# 4. Optionally: if you want to require _all six_ be present, use how="any" instead:
#    df_clean = df.dropna(subset=key_features, how="any").copy()

# 5. Save the cleaned dataset
df_clean.to_csv("planet_cleaned.csv", index=False)

print(f"✅ Cleaned dataset saved with {df_clean.shape[0]} rows and {df_clean.shape[1]} columns.")
