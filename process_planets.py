import os
import json
import time
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import openai
from dotenv import load_dotenv

# ─── Load API key ───────────────────────────────────────────────────────────────
load_dotenv()  # loads OPENAI_API_KEY into env
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise RuntimeError("OPENAI_API_KEY not found in environment")

# ─── 1. Load & preprocess ───────────────────────────────────────────────────────
df = pd.read_csv("planet_cleaned.csv")
features = ["pl_rade","pl_bmasse","pl_eqt","st_teff","st_rad","st_mass"]
df = df.dropna(subset=features).copy()

# ─── 2. Append Earth ─────────────────────────────────────────────────────────────
earth_vals = {
    "pl_name":"Earth","pl_rade":1,"pl_bmasse":1,"pl_eqt":255,
    "st_teff":5772,"st_rad":1,"st_mass":1
}
df = pd.concat([df, pd.DataFrame([earth_vals])], ignore_index=True)

# ─── 3. Scale & cluster ─────────────────────────────────────────────────────────
X = StandardScaler().fit_transform(df[features])
df["cluster"] = KMeans(n_clusters=4, random_state=0).fit_predict(X)

# ─── 4. Compute EarthSimilarity ─────────────────────────────────────────────────
earth_vec = np.array([earth_vals[f] for f in features])
def compute_similarity(row):
    vec = row[features].values.astype(float)
    d = np.linalg.norm(vec - earth_vec) / np.sqrt(len(features))
    return max(0, 1 - d)
df["similarity"] = df.apply(compute_similarity, axis=1)

# ─── 5. Assign temp_class ───────────────────────────────────────────────────────
def temp_class(teq):
    return "Hot" if teq > 500 else "Warm" if teq >= 300 else "Cold"
df["temp_class"] = df["pl_eqt"].apply(temp_class)

# ─── 6. Find top‑10 by similarity ────────────────────────────────────────────────
top10 = df[df.pl_name != "Earth"].nlargest(10, "similarity")["pl_name"].tolist()

# ─── 7. Prepare the enriched JSON structure ────────────────────────────────────
enriched = {
    "clusters":  df.set_index("pl_name")["cluster"].to_dict(),
    "similarity":df.set_index("pl_name")["similarity"].to_dict(),
    "tempClass": df.set_index("pl_name")["temp_class"].to_dict(),
    "top10":     top10,
    "explainers": {}   # we'll fill this next
}

def save_enriched():
    with open("planet_data_enriched.json", "w") as f:
        json.dump(enriched, f, indent=2)

# save the skeleton so you can re‑run/resume
save_enriched()

# ─── 8. Generate or resume explanations ─────────────────────────────────────────
system_prompt = """
You are a concise, engaging space science communicator.
In about 150 words, explain why this exoplanet is interesting:
{name}, with radius {pl_rade} R⊕, mass {pl_bmasse} M⊕,
equilibrium temperature {pl_eqt} K, host-star T_eff {st_teff} K,
radius {st_rad} R☉ and mass {st_mass} M☉.
""".strip()

for idx, row in df.iterrows():
    name = row.pl_name
    # Skip Earth (we can hardcode its blurb)
    if name == "Earth":
        enriched["explainers"][name] = "Our home planet—the gold standard for habitability."
        save_enriched()
        continue

    # Skip if already done
    if name in enriched["explainers"]:
        continue

    # Build the prompt
    user_msg = {
        "role": "user",
        "content": system_prompt.format(
            name=name,
            pl_rade=row.pl_rade,
            pl_bmasse=row.pl_bmasse,
            pl_eqt=row.pl_eqt,
            st_teff=row.st_teff,
            st_rad=row.st_rad,
            st_mass=row.st_mass
        )
    }

    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4.1-nano",
            temperature=0.7,
            messages=[
                {"role":"system","content":"You are a science communicator."},
                user_msg
            ],
            max_tokens=250
        )
        text = resp.choices[0].message.content.strip()
        enriched["explainers"][name] = text

    except Exception as e:
        print(f"⚠️ Error generating explanation for {name}: {e}. Skipping this planet.")
        # you can optionally put a placeholder:
        enriched["explainers"][name] = "Explanation unavailable."

    # save after every planet so you never lose progress
    save_enriched()
    # very gentle rate‑limit
    time.sleep(1)

print("✅ planet_data_enriched.json complete!")
