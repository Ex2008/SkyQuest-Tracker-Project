import pandas as pd
import numpy as np
import openai
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm
import json

# ✅ Set your OpenAI key
openai.api_key = "sk-..."

# ✅ Load cleaned planet data
df = pd.read_csv("planet_cleaned.csv")

# ✅ Define important features for clustering
features = ["pl_rade", "pl_bmasse", "pl_eqt", "st_teff", "st_rad", "st_mass"]
df = df.dropna(subset=features).copy()

# ✅ Add Earth for comparison
earth = {
    "pl_name": "Earth", "pl_rade": 1.0, "pl_bmasse": 1.0, "pl_eqt": 288,
    "st_teff": 5778, "st_rad": 1.0, "st_mass": 1.0,
    "explanation": "Our home planet — the gold standard for habitability.",
    "temp_class": "Temperate"
}
df.loc[len(df)] = earth

# ✅ Normalize and cluster using embeddings
X = df[features].values
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

kmeans = KMeans(n_clusters=4, random_state=42)
df["cluster"] = kmeans.fit_predict(X_scaled)

# ✅ Add temp_class based on equilibrium temperature
def classify_temp(temp):
    if temp < 255: return "Frozen"
    elif temp <= 330: return "Temperate"
    return "Hot"

df["temp_class"] = df["pl_eqt"].apply(classify_temp)

# ✅ Generate GPT explanations (skip Earth)
def generate_explanation(row):
    prompt = (
        f"In ~150 words, explain why {row['pl_name']} is interesting as an exoplanet. "
        f"Radius: {row['pl_rade']} Earth radii, Mass: {row['pl_bmasse']} Earth masses, "
        f"Equilibrium Temperature: {row['pl_eqt']} K. Is it potentially habitable?"
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a concise, engaging space science communicator."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=250,
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Error for {row['pl_name']}: {e}")
        return "Explanation unavailable."

tqdm.pandas()
df["explanation"] = df.apply(
    lambda row: "Our home planet — the gold standard for habitability." if row["pl_name"] == "Earth" else generate_explanation(row),
    axis=1
)

# ✅ Save to JSON for web
df[["pl_name", *features, "cluster", "temp_class", "explanation"]].to_json(
    "planet_data.json", orient="records", indent=2
)

print("✅ planet_data.json saved with explanations, clusters, and Earth.")
