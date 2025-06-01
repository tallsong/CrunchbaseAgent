import os
import requests
import logging
import json
# Configure logging to include line number
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s'
)
class CrunchBase():
    def __init__(self, ):
    
        self.base_url = "https://www.crunchbase.com/"
        self.crunchbase_email = os.getenv("CRUNCHBASE_EMAIL")
        self.crunchbase_password = os.getenv("CRUNCHBASE_PASSWORD")
        self.session = requests.Session()
        if self.login():
            logging.info("Logged in successfully to CrunchBase.")
            
            
        else:
            logging.error("Login failed.")
            raise Exception("Login to CrunchBase failed. Check your credentials.")

    def get_company(self, company_name: str):
        url = f"{self.base_url}organizations/{company_name}?user_key={self.api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def search_companies(self, Keyword: str):
        url = f"{self.base_url}v4/data/searches/organization.companies"
        params = {
                "source":"custom_advanced_search"
            }

        playload = {
            "field_ids": [
                "identifier",
                "categories",
                "location_identifiers",
                "short_description",
                "rank_org_company"
            ],
            "order": [
                {
                    "field_id": "rank_org_company",
                    "sort": "asc"
                }
            ],
            "query": [
                {
                    "type": "predicate",
                    "field_id": "description",
                    "operator_id": "contains",
                    "values": [
                        Keyword
                    ],
                    "include_nulls": False
                }
            ],
            "field_aggregators": [],
            "collection_id": "organization.companies",
            "limit": 15
        }        

        response = requests.post(url, json=playload, params=params)
        if response.status_code == 200:
            logging.info("Search successful.")
            return response.json()
        else:
            logging.error(f"Search failed with status code: {response.status_code}")
            logging.error(f"Response: {response.text}")
            # save respnse html to a file for debugging
            with open("error_response.html", "w") as f:
                f.write(response.text)
            return None

    def login(self):
        url = f"{self.base_url}v4/cb/sessions"
        session = self.session
        session.headers.update({"Content-Type": "application/json"})
        session.headers.update({"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"})
        # check if local cookies file exists
        if os.path.exists("cookies.json"):
            with open("cookies.json", "r") as f:
                cookies_dict = json.load(f)
                for cooike_name, cookie_value in cookies_dict.items():
                    self.session.cookies.set(cooike_name, cookie_value)
                logging.info("Loaded cookies from cookies.json")
                return True
        
        payload = {
            'email': self.crunchbase_email,
            'password': self.crunchbase_password
        }
        response = session.post(url, json=payload)
        if response.status_code == 200 :
            logging.info("Login successful.")
            return True
        elif response.status_code == 201:
            logging.info("Login successful, account created.")
            
            cookies_dict = session.cookies.get_dict()
            cookies_json = json.dumps(cookies_dict, indent=4)
            

            # Optionally save to a file
            with open("cookies.json", "w") as f:
                f.write(cookies_json)
                logging.info("Cookies saved to cookies.json")

            return True
        
        else:
        
            if response.status_code == 401:
                logging.error("Unauthorized: Check your email and password.")
            elif response.status_code == 403:
                logging.error("Forbidden: Access denied.")
            else:
                logging.error(f"Unexpected error: {response.status_code}")
            # Handle other status codes as needed
       
            logging.error(f"Response: {response.text}")
            return False
        
        
        
 
 
def main():
    crunchbase = CrunchBase()
    
    data = crunchbase.search_companies("coninbase")
    if(data):
        logging.info(f"Search results: {data.json()}")
 
if __name__ == "__main__":
    main()       
        
        
        

