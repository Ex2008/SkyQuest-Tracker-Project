# SkyQuest Exo‑Ranker  
**Earth Similarity Mapping of Confirmed Exoplanets**

---

## Abstract  
We present **Exo‑Ranker**, a fully client‑side, static web application that visualizes the “Earth‑likeness” of 5,600+ confirmed exoplanets.  Using six canonical features—planet radius (R⊕), planet mass (M⊕), equilibrium temperature (Tₑq), host‑star temperature (T_*), host‑star radius (R_*), and host‑star mass (M_*)—we compute an **Earth Similarity Index (ESI)** and colour‑code a 2D scatter‐plot by k‑means clusters.  A live “Top 10” bar chart ranks planets by ESI.  GPT‑4o auto‑generates 150 word lay summaries for each world, and a dropdown lets users explore any two numeric axes.  Exo‑Ranker requires no server or keys—data is fetched once, then all interactions are instantaneous.

---

## 1  Data Source  

| **Item**               | **Details**                                                                                                                                                     |
|:-----------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Primary catalogue**  | NASA Exoplanet Archive – “Confirmed Planets” table [Akeson et al. 2013]                                                                                          |
| **Access method**      | HTTPS GET to the public API:  
`https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=SELECT+*+FROM+ps&format=json`                                                                            |
| **Snapshot date**      | 2025‑07‑20                                                                                                         |
| **Rows kept**          | 5,934 confirmed planets; **+1 synthetic “Earth”** row added for benchmarking.                                                                                   |
| **Rationale**          | Peer‑reviewed, constantly updated, harmonised SI units—all essential for reproducible, large‑scale habitability analysis.                                         |

---

## 2  Feature Set  

| **Category**            | **Columns (code‑names)**                                                                                                                   |
|:------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------|
| **Key similarity axes** | `pl_rade`, `pl_bmasse`, `pl_eqt`, `st_teff`, `st_rad`, `st_mass`                                                                           |
| **Orbital geometry**    | `pl_orbper`, `pl_orbsmax`, `pl_orbeccen`, …                                                                                                |
| **Energy budget**       | `pl_insol` (+ error columns)                                                                                                               |
| **Stellar atmosphere**  | `st_met`, `st_logg`, `st_spectype`, …                                                                                                      |
| **Photometry & distance** | `sy_dist`, `sy_vmag`, `sy_kmag`, `sy_gaiamag`                                                                                              |

> *Any unused fields can be hidden in the dropdown without touching the JSON.*

---

## 3  Pre‑processing  

1. **Load** JSON → JavaScript object (or pandas DataFrame)  
2. **Filter** out rows missing _all six_ key‐feature values  
3. **Cast** numeric fields to `float` (coerce errors → `NaN`), strip unit strings  
4. **Standardise** host‑star quantities to Solar units; planet radius/mass already in Earth units  
5. **Append** a synthetic “Earth” record (all canonical values = 1) for comparison  
6. **k‑means++** clustering (_k_ = 4 by elbow‐method) → assign `cluster` labels for scatter colouring  

---

## 4  Earth Similarity Index (ESI)  

\[
\mathrm{ESI} = 1 \;-\; \sqrt{\,
   (R_p-1)^2
 + (M_p-1)^2
 + \bigl(\tfrac{T_{eq}-255}{255}\bigr)^2
 + \bigl(\tfrac{T_* -5772}{5772}\bigr)^2
 + (R_* -1)^2
 + (M_* -1)^2
}\;\,,
\]

- **Clamped** to [0–1] (1 ≡ identical to Earth)  
- Emphasises multidimensional distance from our home world  

---

## 5  Visual‑Analytics Suite  

| **Tab**      | **Plot type**              | **Description**                                                                               | **Library**    |
|:-------------|:---------------------------|:---------------------------------------------------------------------------------------------|:---------------|
| **Scatter**  | 2‑D scatter (Plotly)       | Choose any two numeric axes; colour‑by cluster; Earth highlighted as a star symbol.          | Plotly scatter |
| **Rankings** | Horizontal bar (Plotly)    | Live Top‑10 planets by ESI (bar length = ESI score, hover shows exact value).                | Plotly bar     |

> All tabs share the same in‑memory JSON—switching is instantaneous.

---

## 6  Embedding & Clustering (Future Work)  

- **Embeddings**: feed the 6‑D key‐feature matrix → UMAP (n_neighbors≈15, min_dist=0.1) → 2‑D latent map preserving local similarity  
- **Clustering**: apply DBSCAN (eps≈0.25) on UMAP space → discovers arbitrarily‑shaped clusters  
- **GPT‑4o “planet cards”**: few‑shot prompt with name, discovery info & six features → 150‑word lay summary; cache into `planet_data.json` so site remains static  

---

## 7  Limitations  

1. **Axis weighting**: ESI treats all six dimensions equally; future work will incorporate PCA loadings or expert‐driven weights  
2. **Temperature model**: assumes zero albedo & perfect redistribution; real surface temps may vary by ±100 K  
3. **Missing physics**: ignores host‑star metallicity, UV flux, and atmospheric effects—key for habitability  

---

## 8  ## Reproducibility & Deployment Checklist

Follow these steps **in order** to regenerate all data files and launch the interactive Exo‑Ranker site.

---

### 1. Download Raw Data  
Fetch the “Confirmed Planets” table from the NASA Exoplanet Archive and convert to CSV.

# run the download script
python3 download_rawdata.py
output: planets.csv (flattened CSV)

### 2. Clean & Augment Dataset
Filter out incomplete records, cast types, strip units, standardize units, and append a synthetic “Earth” row.

python3 clean_dataset.py
Input: planets.csv
Processing:
Drop rows missing all six key features
Cast numeric columns → float
Standardize host‑star values (Solar units)
Add “Earth” record (all key‑features = 1)
Output: planet_cleaned.csv

### 3. Compute Clusters & ESI for Visualization
Run clustering and ESI calculation to prepare the static JSON used by the front‑end.

python3 generate_plot.py
Input: planet_cleaned.csv
Processing:
Standardize the six key features
k‑means++ clustering (k = 4) → assign cluster
Compute Earth Similarity Index (ESI) for each planet
Output: planet_data.json

### 4. Enrich with Embeddings & GPT‑4o Explanations
One‐shot call to OpenAI’s GPT‑4.1‑nano for:

UMAP embedding + DBSCAN clustering (optional)
150‑word lay explanations
Temperature class labels
python3 process_planets.py
Input: planet_cleaned.csv
Processing:
Compute UMAP embeddings of key features
DBSCAN clustering on 2D embedding
Build single payload of all planets
Call openai.ChatCompletion with model=gpt-4.1-nano
Parse GPT response into keys:
clusters
similarity (ESI)
tempClass (“Hot”/“Warm”/“Cold”)
explainers (≈150‑word summary per planet)
Output: planet_data_enriched.json

### 5. Launch Exo‑Ranker
Serve or open the static HTML page—no server‑side code required.

Ensure both JSON files live alongside the HTML:
├── exo‑ranker.html
├── planet_data.json
└── planet_data_enriched.json
Open exo‑ranker.html in any modern browser (Chrome, Firefox, Safari).
Interact:
Scatter tab: choose any two axes, click points for summaries
Rankings tab: live Top 10 by ESI
Notes

All processing scripts require Python 3.9+ and the packages in requirements.txt.
The OpenAI API key must be set in your environment (OPENAI_API_KEY) or in a .env file.
Once planet_data_enriched.json is generated, the site is fully static—no runtime API calls or keys needed.


## 9  Science‑Communication Impact

Quantitative ranking meets compelling storytelling:
Judges enjoy seeing rigorous, multidimensional habitability metrics
Plus engaging, natural‑language “planet cards” that spark curiosity
References

Akeson, R. L., et al. (2013). The NASA Exoplanet Archive: Data and Tools for Exoplanet Research. Publications of the Astronomical Society of the Pacific, 125(930), 989–999.
Exoplanet Archive: https://exoplanetarchive.ipac.caltech.edu
