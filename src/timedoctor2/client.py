import logging
import csv

from keboola.http_client import HttpClient
from .endpoint_mapping import ENDPOINT_MAPPING
from requests.exceptions import HTTPError
from keboola.csvwriter import ElasticDictWriter


class TimeDoctor2ClientError(Exception):
    pass


class TimeDoctor2Client:
    def __init__(self, email, password, company_id, mode, _from, _to):
        self.email = email
        self.password = password
        self.company_id = company_id
        self.mode = mode
        self.limit = 10
        self._from = _from
        self._to = _to

        self.client = HttpClient("https://api2.timedoctor.com/")
        self.token = ""
        self.users = []
        self.login()
        self.get_list_of_users()

    def login(self) -> None:
        """
        Stores auth token in self.token.
        """
        payload = {
            "email": self.email,
            "password": self.password,
            "permissions": "read"
        }
        r = self.client.post_raw("/api/1.0/login", json=payload)
        try:
            r.raise_for_status()
        except HTTPError as e:
            raise TimeDoctor2ClientError("Invalid API credentials") from e
        self.token = r.json().get("data").get("token")
        self.authorization()

    def authorization(self):
        """
        Checks if user has access to companies specified in company_ids param.
        """
        params = {
            "token": self.token
        }
        r = self.client.get_raw("/api/1.0/authorization", params=params)

        try:
            r.raise_for_status()
        except HTTPError as e:
            raise TimeDoctor2ClientError(f"Unable to call authorization endpoint for user {self.email}") from e

        available_companies = r.json().get("data").get("companies")
        companies = [company.get("id") for company in available_companies]

        if self.company_id in companies:
            logging.info(f"User {self.email} has been successfully authorized for company with id {self.company_id}.")
        else:
            raise TimeDoctor2ClientError(f"User {self.email} cannot access company with id {self.company_id}.")

    def do_increment(self):
        pass

    def do_sync(self):
        pass

    def get_list_of_users(self) -> None:
        with open("/Users/dominik/projects/kds-team.ex-time-doctor-2/data/out/tables/users.csv") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.users.append(row["id"])

    def process_endpoint(self, endpoint, table_def):
        endpoint_mapping = ENDPOINT_MAPPING.get(endpoint)

        if "user" in endpoint_mapping.get("placeholders"):
            with ElasticDictWriter(table_def.full_path, []) as wr:
                for user in self.users:
                    params = {
                        "token": self.token,
                        "limit": self.limit,
                        "user": user,
                        "company": self.company_id,
                        "from": self._from if self._from else None,
                        "to": self._to if self._to else None
                    }

                    r = self.client.get_raw(endpoint_mapping.get('endpoint'), params=params)

                    try:
                        data = r.json().get("data")[0]
                    except IndexError:
                        data = r.json().get("data")

                    try:
                        if len(data) > 1:
                            wr.writerows(data)
                        elif len(data) == 0:
                            pass
                        else:
                            wr.writerow(data[0])
                    except:
                        print(data)
                        exit()
                wr.writeheader()
        else:
            has_more = True
            page = 0
            with ElasticDictWriter(table_def.full_path, []) as wr:
                while has_more:
                    params = {
                        "token": self.token,
                        "company": self.company_id,
                        "page": page,
                        "limit": self.limit
                    }
                    r = self.client.get_raw(ENDPOINT_MAPPING.get('users').get('endpoint'), params=params)
                    wr.writerows(r.json().get("data"))
                    page += 1
                    if r.json().get("paging").get("nItems") < self.limit:
                        has_more = False
                wr.writeheader()

    def get_users(self, table_def):
        has_more = True
        page = 0
        with ElasticDictWriter(table_def.full_path, []) as wr:
            while has_more:
                params = {
                    "token": self.token,
                    "company": self.company_id,
                    "page": page,
                    "limit": self.limit
                }
                r = self.client.get_raw(ENDPOINT_MAPPING.get('users').get('endpoint'), params=params)
                wr.writerows(r.json().get("data"))
                page += 1
                if r.json().get("paging").get("nItems") < self.limit:
                    has_more = False
            wr.writeheader()
