import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv

#get the API key
load_dotenv(".env")
API_KEY = os.getenv("WALKSCOREAPI_KEY")
print("WalkScore API Key: ", API_KEY)

#check if lat/lon are valid
def validateLatLong(lat, lon):
    try:
        lat, lon = float(lat), float(lon)
        return (-90 <= lat <= 90) and (-180 <= lon <= 180)
    except (ValueError, TypeError):
        return False

#clean address text
def cleanAddress(address):
    if pd.isna(address) or not isinstance(address, str):
        return ""
    return address.strip().replace("\n", " ").replace("\r", " ")

#get walkscore data
def getWalkScore(lat, lon, address, maxRetries=3):
    if not validateLatLong(lat, lon): #esnure lat/long validity
        return {"walkscore": None, "transit_score": None, "bike_score": None, "error": "invalid_coords"}

    address = cleanAddress(address)
    if not address:
        return {"walkscore": None, "transit_score": None, "bike_score": None, "error": "invalid_address"}

    url = "https://api.walkscore.com/score"
    params = {
        "format": "json",
        "lat": float(lat),
        "lon": float(lon),
        "address": address,
        "transit": 1,
        "bike": 1,
        "wsapikey": API_KEY,
    }

    #call API with retries
    for attempt in range(maxRetries):
        try:
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == 1: #success, return scores
                    return {
                        "walkscore": data.get("walkscore"),
                        "transit_score": data.get("transit", {}).get("score"),
                        "bike_score": data.get("bike", {}).get("score"),
                        "error": None,
                    }
                return {"walkscore": None, "transit_score": None, "bike_score": None, "error": f"status_{data.get('status')}"}
            elif response.status_code == 404:
                return {"walkscore": None, "transit_score": None, "bike_score": None, "error": "not_found"}
            elif response.status_code == 429:
                print("Rate limited, waiting 10s...")
                time.sleep(10)
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")

        time.sleep(2 ** attempt)  #exponential backoff

    return {"walkscore": None, "transit_score": None, "bike_score": None, "error": "max_retries_exceeded"}

#process entire file with checkpointing (bc it hangs w no checkpoints)
def processFile(filePath, outputPath, checkpointInterval=50):
    df = pd.read_csv(filePath)
    totalRows = len(df)

    checkpointFile = outputPath.replace(".csv", "_checkpoint.csv")
    startIndex = 0

    if os.path.exists(checkpointFile):
        print("Resuming from checkpoint...")
        checkpoint_df = pd.read_csv(checkpointFile)
        startIndex = len(checkpoint_df)
        df = checkpoint_df
    else:
        df["walkscore"] = None
        df["transit_score"] = None
        df["bike_score"] = None
        df["walkscore_error"] = None

    print(f"Processing {totalRows} rows (starting at {startIndex})...")

    for i in range(startIndex, totalRows):
        row = df.iloc[i]
        result = getWalkScore(row["latitude"], row["longitude"], row["address"])

        df.loc[i, "walkscore"] = result["walkscore"]
        df.loc[i, "transit_score"] = result["transit_score"]
        df.loc[i, "bike_score"] = result["bike_score"]
        df.loc[i, "walkscore_error"] = result["error"]

        if (i + 1) % checkpointInterval == 0:
            df.to_csv(checkpointFile, index=False)
            print(f"Checkpoint saved at row {i+1}/{totalRows}")

        time.sleep(1.5)  #avoid rate limit

    df.to_csv(outputPath, index=False)
    print(f"Saved final dataset to {outputPath}")

    if os.path.exists(checkpointFile):
        os.remove(checkpointFile)

    return df


if __name__ == "__main__":
    if not API_KEY:
        print("api key missing")
        exit(1)

    rawDir = "data/raw"
    dataFiles = ["chicago_il_raw.csv", "los_angeles_ca_raw.csv", "new_york_ny_raw.csv"]

    for file in dataFiles:
        filePath = os.path.join(rawDir, file)
        if not os.path.exists(filePath):
            print(f"File not found: {file}")
            continue

        print(f"\nProcessing {file}...")
        dfTest = pd.read_csv(filePath)
        if len(dfTest) > 0:
            sample = dfTest.iloc[0]
            print("Testing API with first row...")
            print(getWalkScore(sample["latitude"], sample["longitude"], sample["address"]))

        outFile = file.replace("_raw.csv", "_ws.csv")
        outPath = os.path.join("data/ws", outFile)
        os.makedirs("data/ws", exist_ok=True)

        processed = processFile(filePath, outPath)
        print(f"Summary for {file}: {processed['walkscore'].notna().sum()} / {len(processed)} successful\n")
