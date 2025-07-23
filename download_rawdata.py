import pandas as pd
import requests

url = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
query = """
SELECT pl_name, pl_eqt, pl_rade, pl_masse, st_teff, st_rad, st_mass, st_dist, disc_year
FROM pscomppars
WHERE pl_eqt IS NOT NULL AND pl_rade IS NOT NULL
"""

params = {
    "query": query,
    "format": "csv"
}

r = requests.get(url, params=params)
with open("planets.csv", "wb") as f:
    f.write(r.content)
