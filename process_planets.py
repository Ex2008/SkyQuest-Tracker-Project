import pandas as pd

# Load the raw dataset
df = pd.read_csv("planets.csv")

# Drop any row that has missing (NaN) values in any column
df_clean = df.dropna()

# Save the cleaned full-featured dataset
df_clean.to_csv("planet_cleaned.csv", index=False)

print(f"✅ Cleaned dataset saved with {df_clean.shape[0]} rows and {df_clean.shape[1]} columns.")
