import pandas as pd

# Load the full cleaned dataset
df = pd.read_csv("planet_cleaned.csv")

# Save the DataFrame to JSON (for the browser)
df.to_json("planet_data.json", orient="records")

print("✅ Saved: planet_data.json (for dynamic plotting)")
