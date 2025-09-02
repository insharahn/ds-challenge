import pandas as pd
import numpy as np

inputFile = "data/zillow_walkscore_census.csv"
outputFile = "data/zillow_walkscore_census_clean.csv"

#load dataset
df = pd.read_csv(inputFile)

# --- CLEANING ---
#drop exact duplicates
df = df.drop_duplicates(subset=["url"]) #using unique url to identify duplicates

df["zip_code"] = df["zip_code"].astype(str).str.zfill(5) #zip code valid

#convert numeric fields (NaN if something weird shows up)
numericColumns = [
    "price", "bedrooms", "bathrooms", "square_feet",
    "walkscore", "transit_score", "bike_score",
    "median_income", "population",
    "white_pop", "black_pop", "asian_pop", "hispanic_pop"
]
for col in numericColumns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

#listing_date to datetime
df["listing_date"] = pd.to_datetime(df["listing_date"], errors="coerce")

#standardize text fields
df["city"] = df["city"].str.title().str.strip()
df["state"] = df["state"].str.upper().str.strip()

# --- MISSING DATA ---
df = df.dropna(subset=["price", "zip_code"]) #drop rows with no price or zip code

# --- GET RID OF OUTLIERS ---
df = df[(df["price"] > 100) & (df["price"] < 5_000_000)]
df = df[(df["square_feet"].isna()) | ((df["square_feet"] > 100) & (df["square_feet"] < 20_000))]
df = df[(df["bedrooms"].isna()) | (df["bedrooms"] < 15)]
df = df[(df["bathrooms"].isna()) | (df["bathrooms"] < 15)]

# --- ENRICHMENT ---
#competition density = number of listings in same zip code
competition = df.groupby("zip_code").size().reset_index(name="competition_density")
df = df.merge(competition, on="zip_code", how="left")

# --- FEATURE ENGINEERING ---
#populagtion density proxy = population / competition_density (demand pressure).
df["population_density_proxy"] = df["population"] / df["competition_density"]

#diversity index = sum of squared population shares (from race columns).
raceColumns = ["white_pop", "black_pop", "asian_pop", "hispanic_pop"]
for col in raceColumns:
    df[col] = df[col].fillna(0)

def calculateDiversity(row):
    if row["population"] > 0:
        shares = [(row[col] / row["population"]) for col in raceColumns if row["population"] > 0]
        return 1 - sum([s**2 for s in shares])
    return np.nan

df["diversity_index"] = df.apply(calculateDiversity, axis=1)

#affordability index = median_income / price
df["affordability_index"] = df["median_income"] / df["price"]

#save clean dataset
df.to_csv(outputFile, index=False)

print("Preview:")
print(df.head())
