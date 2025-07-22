1 Data source

Item	Details
Primary catalogue	NASA Exoplanet Archive – “Confirmed Planets” table 
NASA Exoplanet Archive
Access method	HTTPS GET to the public API https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=SELECT+*+FROM+ps&format=json (or CSV for Python).
Snapshot date	Insert the date you downloaded planet_data.json
Rows kept	5 ,600+ confirmed planets; one synthetic Earth row added manually for benchmarking.
Rationale: the Confirmed Planets table is peer‑reviewed, constantly updated, and already harmonised in SI / cgs units. 
NASA Exoplanet Archive

2 Feature set

Category	Columns (code‑names)
Key similarity axes	pl_rade, pl_bmasse, pl_eqt, st_teff, st_rad, st_mass
Orbital geometry	pl_orbper, pl_orbsmax, pl_orbeccen, …
Energy budget	pl_insol (+ error cols)
Stellar atmosphere	st_met, st_logg, spectral type etc.
Photometry & distance	sy_dist, sy_vmag, sy_kmag, sy_gaiamag
(Any field you do not find useful can be hidden in the dropdown without touching the JSON.)

3 Pre‑processing
    1. Load JSON → JavaScript object (or pandas DataFrame).
    2. Remove rows with nulls in *all six* key‑feature columns.
    3. For numeric fields: cast to float, coerce errors to NaN, strip unit strings if any.
    4. Standardise host‑star quantities to Solar units; planet radius/mass already in Earth units.
    5. Add a synthetic “Earth” record (all canonical values =1) if you plan to include Earth on plots.
    6. k‑means++ (k=7 by elbow‑method) → assign `cluster` label for scatter colouring.

4 Earth Similarity Index (ESI)
Earth Similarity Index  (ESI)

ESI = 1 − √ [ (R_p − 1)²
            + (M_p − 1)²
            + ((T_eq − 255) / 255)²
            + ((T_* − 5772) / 5772)²
            + (R_* − 1)²
            + (M_* − 1)² ]

where
  R_p   = planet radius in Earth radii (R⊕)
  M_p   = planet mass in Earth masses (M⊕)
  T_eq  = planet equilibrium temperature in kelvin
  T_*   = host‑star effective temperature in kelvin
  R_*   = host‑star radius in solar radii (R☉)
  M_*   = host‑star mass in solar masses (M☉)

The index is clipped to the range 0 – 1 (1 ≡ identical to Earth).


5 Visual‑analytics suite

Tab	        Plot type	                        What it shows	                                                        Library
Scatter	    2‑D scatter coloured by cluster	    Comparative spread along any two numeric axes chosen from dropdown.	    Plotly scatter
Rankings	Horizontal bar chart	            Top‑10 planets by ESI (live‑recomputed).	                            Plotly bar

All tabs share the same in‑memory JSON, so switching is instantaneous.


7 Embedding & clustering (future section)

Embeddings: feed the 6‑D key‑feature matrix → UMAP (n_neighbors ≈ 15, min_dist = 0.1)
to create a 2‑D latent map preserving local similarity.
Clustering: DBSCAN on the UMAP space (eps ≈ 0.25) — better than k‑means because of arbitrary shapes.
GPT‑4o planet cards: prompt‑template with pl_name, discovery info and the six features to generate a 150‑word lay summary; cache to planet_data.json in an explanation field so the site remains 100 % static.

8 Limitations

The ESI treats all six axes with equal weight; a forthcoming iteration will introduce weights learned via principal‑component loadings or expert priors.
Equilibrium temperature assumes zero albedo and perfect redistribution — real surface temps may differ by ±100 K.
Host‑star metallicity and UV flux are ignored (important for habitability).

9 Reproducibility checklist

Download data – curl the API URL above → planets_raw.json.
Run prep_planets.py – cleans, adds Earth, writes planet_data.json.
Open exo‑ranker.html locally – no runtime server or keys needed.
Interact – switch tabs, hover for tooltips; site is fully client‑side.


Citation
Akeson, R. L., et al. “The NASA Exoplanet Archive: Data and Tools for Exoplanet Research.”  Publications of the Astronomical Society of the Pacific 125.930 (2013): 989‑999.
