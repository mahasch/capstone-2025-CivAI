import requests
from collections import Counter
import pickle


class CrimeData:
    def __init__(self, postcode, borough):
        self.postcode = postcode
        self.borough = borough
        self.get_crime_data = self.get_crime_by_postcode()

    def get_crime_by_postcode(self):
        with open(r"backend\agent\crime\crime_by_borough.pkl", "rb") as f:
            crime_db = pickle.load(f) 
        if not self.borough:
            return None

        data = crime_db.get(self.borough)
        if data:
            return data
        else:
            return {"error": f"No crime data found for borough '{self.borough}'"}