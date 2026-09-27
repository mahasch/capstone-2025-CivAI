import requests
from collections import Counter
import pickle
from pathlib import Path


class CrimeData:
    def __init__(self, postcode, borough):
        self.postcode = postcode
        self.borough = borough
        self.get_crime_data = self.get_crime_by_postcode()

    def get_crime_by_postcode(self):
        if not self.borough:
            return None

        crime_file = (
            Path(__file__).resolve().parents[1]
            / "pre_processing_data"
            / "crime_dataset"
            / "crime_by_borough.pkl"
        )
        if not crime_file.exists():
            return None

        with crime_file.open("rb") as f:
            crime_db = pickle.load(f)

        data = crime_db.get(self.borough)
        if data:
            return data
        else:
            return {"error": f"No crime data found for borough '{self.borough}'"}