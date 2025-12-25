import requests
import pandas as pd
import glob
import os
import time
from dotenv import load_dotenv

#constants
INPUT_DIR = "data/ws"
OUTPUT_FILE = "data/zillow_walkscore_census.csv"
CENSUS_YEAR = "2021" #bc of acs 5 year data most recent available

#api key
load_dotenv(".env")
API_KEY = os.getenv("CENSUSDATAAPI_KEY")
print("Census Data API Key: ", API_KEY)

#variables to fetch 
variables = {
    "median_income": "B19013_001E", 
    "population": "B01003_001E",     
    "white_pop": "B02001_002E",      
    "black_pop": "B02001_003E",      
    "asian_pop": "B02001_005E",     
    "hispanic_pop": "B03003_003E"   
}

def testCensusApi(): #test census api connection
    url = f"https://api.census.gov/data/{CENSUS_YEAR}/acs/acs5"
    params = {
        "get": "B19013_001E", #just median income
        "for": "state:06", #california
        "key": API_KEY.strip()
    }
    try:
        response = requests.get(url, params=params, timeout=10)   
        if response.status_code == 200: #success
            try:
                data = response.json()
                return True
            except ValueError:
                return False
        else:
            return False
            
    except Exception as e:
        return False

def fetchBatchData(zipCodes, batchSize=50): #multiple zip codes with batching
    varString = ",".join(variables.values())
    baseURL = f"https://api.census.gov/data/{CENSUS_YEAR}/acs/acs5"
    allData = []
    
    #process in batches
    totalBatches = (len(zipCodes) + batchSize - 1) // batchSize
    
    for batchNumber in range(0, len(zipCodes), batchSize):
        batchZips = zipCodes[batchNumber:batchNumber + batchSize]
        batchIndex = batchNumber // batchSize + 1
                
        for zipIndex, zipCode in enumerate(batchZips):
            zipCode = str(zipCode).zfill(5) #clean zip code
            
            print(f"[{batchIndex}/{totalBatches}] Processing ZIP {zipIndex+1}/{len(batchZips)}: {zipCode}")   
            params = {
                "get": varString,
                "for": f"zip code tabulation area:{zipCode}",
                "key": API_KEY.strip()
            }
            
            print(f"Making request to Census API...")
            try:
                response = requests.get(baseURL, params=params, timeout=15)
                print(f"Response received: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"Success - parsing JSON...")
                    try:
                        data = response.json()
                        print(f"JSON parsed successfully, {len(data)} rows")
                        
                        #check if we got valid data
                        if len(data) > 1:
                            row = data[1] #first row
                            record = {"zip_code": zipCode}
                            
                            #map variables to values
                            for i, varName in enumerate(variables.keys()):
                                try:
                                    value = row[i]
                                    #convert to numeric, handle nulls
                                    record[varName] = float(value) if value not in [None, '', 'null', '-999999999'] else None
                                except (ValueError, IndexError):
                                    record[varName] = None
                            
                            allData.append(record)
                        else:
                            print(f"{zipCode}: No data in response")
                            #still add record with nulls
                            record = {"zip_code": zipCode}
                            for varName in variables.keys():
                                record[varName] = None
                            allData.append(record)
                            
                    except ValueError as e:
                        print(f"JSON parse error - {str(e)}")
                        
                elif response.status_code == 400:
                    print(f"HTTP 400 - Bad request (likely invalid ZIP)")
                    
                elif response.status_code == 404:
                    print(f"HTTP 404 - ZIP not found in Census data")
                    
                else:
                    print(f"{zipCode}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"{zipCode}: Unexpected error - {str(e)[:100]}")
            
            #rate limiting :p
            print(f"Sleeping 0.5 seconds...")
            time.sleep(0.5)
               
        #longer pause between batches
        if batchIndex < totalBatches:
            print(f"Records collected so far: {len(allData)}")
            time.sleep(2)
    
    return pd.DataFrame(allData)

def validateZips(zipCodes): #validate and clean zip codes
    valid = []
    
    for zipCode in zipCodes:
        zipString = str(zipCode).strip() #cast to string and trim
        cleanZip = ''.join(c for c in zipString if c.isdigit()) #remove non-digits
        
        if len(cleanZip) == 5: #5 digits, valid
            valid.append(cleanZip)
        elif len(cleanZip) == 4:
            valid.append(cleanZip.zfill(5)) #give it a 0 in the start
        else:
            print(f"Invalid ZIP code: {zipCode}")
    
    return valid

def main():
    
    #test API first
    if not testCensusApi():
        print("census api didnt work")
        return
    
    #load the _ws files
    filePattern = os.path.join(INPUT_DIR, "*.csv")
    allFiles = glob.glob(filePattern)
            
    #load and combine all files
    dfs = []
    for file in allFiles:
        df = pd.read_csv(file)
        dfs.append(df)
        
    if not dfs:
        print("No files successfully loaded")
        return
    
    combinedDatFrames = pd.concat(dfs, ignore_index=True) #combine all dataframes
    
    if 'zip_code' not in combinedDatFrames.columns:
        print("No 'zip_code' column found in data")
        return
    
    #fet unique ZIP codes
    uniqueZips = combinedDatFrames['zip_code'].dropna().unique()
    validZips = validateZips(uniqueZips)
            
    #fetch Census data
    censusDataFrames = fetchBatchData(validZips)
    
    #merge with original data - zip_code columns are same type
    combinedDatFrames['zip_code'] = combinedDatFrames['zip_code'].astype(str).str.zfill(5)
    censusDataFrames['zip_code'] = censusDataFrames['zip_code'].astype(str).str.zfill(5)
    
    merged = combinedDatFrames.merge(censusDataFrames, on='zip_code', how='left')
    
    # create output directory and save
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    merged.to_csv(OUTPUT_FILE, index=False)

if __name__ == "__main__":
    main()