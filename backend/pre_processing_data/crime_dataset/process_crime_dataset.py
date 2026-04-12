import pandas as pd

# ---------------------------
# List of London boroughs
# ---------------------------
london_boroughs = [
    "Barking and Dagenham",
    "Barnet",
    "Bexley",
    "Brent",
    "Bromley",
    "Camden",
    "Croydon",
    "Ealing",
    "Enfield",
    "Greenwich",
    "Hackney",
    "Hammersmith and Fulham",
    "Haringey",
    "Harrow",
    "Havering",
    "Hillingdon",
    "Hounslow",
    "Islington",
    "Kensington and Chelsea",
    "Kingston upon Thames",
    "Lambeth",
    "Lewisham",
    "Merton",
    "Newham",
    "Redbridge",
    "Richmond upon Thames",
    "Southwark",
    "Sutton",
    "Tower Hamlets",
    "Waltham Forest",
    "Wandsworth",
    "Westminster",
    "City of London"
]

# ---------------------------
# Load LSOA -> Borough lookup
# ---------------------------
file_path_lookup = "C:\\Users\\mahas\\Downloads\\capstone\\backend\\pre_processing_data\\crime_dataset\\lsoa_borough.csv"

postcode_df = pd.read_csv(file_path_lookup, dtype=str, encoding="latin1")

# Keep only relevant columns
postcode_df = postcode_df[["lsoa11cd", "ladnm"]]
postcode_df.columns = ["LSOA", "Borough"]

# Clean whitespace
postcode_df["LSOA"] = postcode_df["LSOA"].str.strip()
postcode_df["Borough"] = postcode_df["Borough"].str.strip()

# Filter to London boroughs
postcode_df = postcode_df[postcode_df["Borough"].isin(london_boroughs)]

# Build lookup dictionary
lsoa_to_borough = postcode_df.drop_duplicates("LSOA").set_index("LSOA")["Borough"].to_dict()

print(f"Number of LSOAs in London lookup: {len(lsoa_to_borough)}")
print(postcode_df.head())

# ---------------------------
# Load crime data
# ---------------------------
file_path_crime = "C:\\Users\\mahas\\Downloads\\capstone\\backend\\pre_processing_data\\crime_dataset\\crime_2025.csv"
crime_df = pd.read_csv(file_path_crime, dtype=str, encoding="latin1")

# Keep only relevant columns
crime_df = crime_df[["Month", "LSOA code", "Crime type"]]
crime_df.columns = ["Month", "LSOA", "Crime"]

# Clean whitespace
crime_df["LSOA"] = crime_df["LSOA"].str.strip()

# ---------------------------
# Map LSOA -> Borough
# ---------------------------
crime_df["Borough"] = crime_df["LSOA"].map(lsoa_to_borough)

# Drop rows where mapping failed (non-London)
crime_df = crime_df[crime_df["Borough"].notna()]

# ---------------------------
# Save processed CSV
# ---------------------------
# output_path = "C:\\Users\\mahas\\Downloads\\capstone\\backend\\pre_processing_data\\crime_dataset\\processed_crime_2025.csv"
# crime_df.to_csv(output_path, index=False)

# ---------------------------
# Sanity check
# ---------------------------
print("Top 10 boroughs by crime count:")
print(crime_df["Borough"].value_counts().head(10))

print(f"Total boroughs present: {crime_df['Borough'].nunique()}")

borough_pop = {
    "Barking and Dagenham": 210000, "Barnet": 390000, "Bexley": 250000,
    "Brent": 330000, "Bromley": 330000, "Camden": 260000, "Croydon": 385000,
    "Ealing": 350000, "Enfield": 340000, "Greenwich": 295000, "Hackney": 290000,
    "Hammersmith and Fulham": 185000, "Haringey": 280000, "Harrow": 250000,
    "Havering": 260000, "Hillingdon": 310000, "Hounslow": 290000, "Islington": 240000,
    "Kensington and Chelsea": 155000, "Kingston upon Thames": 180000, "Lambeth": 320000,
    "Lewisham": 310000, "Merton": 210000, "Newham": 360000, "Redbridge": 310000,
    "Richmond upon Thames": 195000, "Southwark": 320000, "Sutton": 205000,
    "Tower Hamlets": 325000, "Waltham Forest": 280000, "Wandsworth": 325000,
    "Westminster": 255000, "City of London": 9000
}
import pickle
from datetime import datetime
crime_counts = (
    crime_df.groupby(["Borough", "Crime"])
    .size()
    .unstack(fill_value=0)
)

crime_counts = crime_df.groupby(["Borough", "Crime"]).size().unstack(fill_value=0)
crime_counts["Total"] = crime_counts.sum(axis=1)

# ---------------------------
# 7. Compute crime rate per 1,000 population
# ---------------------------
crime_rate = crime_counts.copy()
for borough in crime_rate.index:
    pop = borough_pop.get(borough, 100000)
    crime_rate.loc[borough] = crime_rate.loc[borough] / pop * 1000
    
# ---------------------------
# 8. Compute rank per category (highest crime = rank 1)
# ---------------------------
crime_rank = crime_rate.rank(ascending=False, method='min').astype(int)

# ---------------------------
# 9. Assemble CrystalRoof-style dictionary
# ---------------------------
data_date = "2025-10"  # Example month
refreshed_date = datetime.today().strftime("%Y-%m-%d")

crystalroof_data = {}
for borough in crime_rate.index:
    crystalroof_data[borough] = {
        "data": {
            "rate": crime_rate.loc[borough].to_dict(),
            "rank": crime_rank.loc[borough].to_dict()
        },
        "dataDate": data_date,
        "refreshedDate": refreshed_date
    }
print(crystalroof_data)  
output_pickle = r"C:\Users\mahas\Downloads\capstone\backend\pre_processing_data\crime_dataset\crime_by_borough.pkl"
with open(output_pickle, "wb") as f:
    pickle.dump(crystalroof_data, f)

print(f"Pickle file saved: {output_pickle}")

print("Top 10 boroughs by total crime rate:")
print(crime_rate["Total"].sort_values(ascending=False).head(10))