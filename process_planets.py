import os
import json
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import openai
from dotenv import load_dotenv

# ─── Load API key ───────────────────────────────────────────────────────────────
load_dotenv()  # reads .env and exports into os.environ
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise RuntimeError("OPENAI_API_KEY not found in environment")

# ─── 1. Load key features ────────────────────────────────────────────────────────
df = pd.read_csv("planet_cleaned.csv")
features = ["pl_rade", "pl_bmasse", "pl_eqt", "st_teff", "st_rad", "st_mass"]
df = df.dropna(subset=features).copy()

# ─── 2. Append Earth ─────────────────────────────────────────────────────────────
earth_vals = {
    "pl_name": "Earth", "pl_rade": 1, "pl_bmasse": 1, "pl_eqt": 255,
    "st_teff": 5772, "st_rad": 1, "st_mass": 1
}
df = pd.concat([df, pd.DataFrame([earth_vals])], ignore_index=True)

# ─── 3. Scale & cluster ──────────────────────────────────────────────────────────
X = StandardScaler().fit_transform(df[features])
df["cluster"] = KMeans(n_clusters=4, random_state=0).fit_predict(X)

# ─── 4. Compute EarthSimilarity ─────────────────────────────────────────────────
earth_vec = np.array([earth_vals[f] for f in features])
def similarity(row):
    vec = row[features].values.astype(float)
    # normalized Euclidean distance
    d = np.linalg.norm(vec - earth_vec) / np.sqrt(len(features))
    return max(0, 1 - d)
df["similarity"] = df.apply(similarity, axis=1)

# ─── 5. Temp class ───────────────────────────────────────────────────────────────
def temp_class(teq):
    return "Hot" if teq > 500 else "Warm" if teq >= 300 else "Cold"
df["temp_class"] = df["pl_eqt"].apply(temp_class)

# ─── 6. Pick top 10 ─────────────────────────────────────────────────────────────
top10 = df[df.pl_name != "Earth"].nlargest(10, "similarity")["pl_name"].tolist()

# ─── 7. Build GPT payload ────────────────────────────────────────────────────────
payload = []
for _, row in df.iterrows():
    payload.append({
        "name": row.pl_name,
        **{f: row[f] for f in features}
    })

system_prompt = """
You are a science communicator. Given an array of planet records:
  [{ name, pl_rade, pl_bmasse, pl_eqt, st_teff, st_rad, st_mass }, ...]
Return **one** JSON object with:
  clusters:  { "<name>": cluster_id, … }
  similarity: { "<name>": score, … }
  top10:      [ … ]
  tempClass: { "<name>": "Hot"/"Warm"/"Cold", … }
  explainers: { "<name>": "≈150‑word explanation", … }
No extra wrapping text.
""".strip()

# ─── 8. Call ChatCompletion ─────────────────────────────────────────────────────
response = openai.ChatCompletion.create(
    model="gpt-4.1-nano",
    temperature=0.7,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json.dumps({
            "data": payload,
            "top10": top10,
            "clusters": df.set_index("pl_name")["cluster"].to_dict(),
            "similarity": df.set_index("pl_name")["similarity"].to_dict(),
            "tempClass": df.set_index("pl_name")["temp_class"].to_dict()
        })}
    ]
)

# ─── 9. Parse & save enriched JSON ──────────────────────────────────────────────
enriched = json.loads(response.choices[0].message.content)
with open("planet_data_enriched.json", "w") as f:
    json.dump(enriched, f, indent=2)

print("✅ planet_data_enriched.json saved with clusters, similarity, tempClass, and explainers!")
