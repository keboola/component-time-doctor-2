import logging
import csv
from datetime import datetime
import time

from keboola.http_client import HttpClient
from .endpoint_mapping import ENDPOINT_MAPPING
from requests.exceptions import HTTPError, JSONDecodeError
from keboola.csvwriter import ElasticDictWriter
import keboola.utils.date as dutils


class TimeDoctor2ClientError(Exception):
    pass


class TimeDoctor2Client:
    def __init__(self, email, password, company_id, _from, _to):
        self.email = email
        self.password = password
        self.company_id = company_id
        self.limit = 100
        self.dt_format = "%Y-%m-%dT%H:%M:%S"
        self._from = datetime.strptime(_from, self.dt_format)
        self._to = datetime.strptime(_to, self.dt_format)

        default_header = {
            'accept': 'application/json'
        }

        self.client = HttpClient("https://api2.timedoctor.com/", default_http_header=default_header)
        self.token = ""

        self.users = []
        self.login()

        if (self._from is None) or (self._to is None):
            raise TimeDoctor2ClientError("Parameters from and to cannot be empty.")
        self.intervals_from, self.intervals_to = self.create_intervals()

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

    def create_intervals(self):

        intervals = dutils.split_dates_to_chunks(self._from, self._to, intv=7, strformat=self.dt_format)
        intervals_from = []
        intervals_to = []
        for interval in intervals:
            intervals_from.append(interval['start_date'])
            intervals_to.append(interval['end_date'])
        return intervals_from, intervals_to

    def get_list_of_users(self, path) -> None:
        with open(path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.users.append(row["id"])

    def process_endpoint(self, endpoint, table_def):
        endpoint_mapping = ENDPOINT_MAPPING.get(endpoint)
        if "user" in endpoint_mapping.get("placeholders"):
            with ElasticDictWriter(table_def.full_path, []) as wr:
                for user in self.users:
                    for interval_from, interval_to in zip(self.intervals_from, self.intervals_to):
                        params = {
                            "token": self.token,
                            "user": user,
                            "company": self.company_id,
                            "from": interval_from,
                            "to": interval_to
                        }

                        try:
                            r = self.client.get_raw(endpoint_mapping.get("endpoint"), params=params)
                            r.raise_for_status()
                        except HTTPError as e:
                            if r.status_code == 429:
                                time.sleep(1)
                                r = self.client.get_raw(endpoint_mapping.get("endpoint"), params=params)
                            else:
                                logging.error(f"Got response with status code: {r.status_code}")
                                raise e

                        try:
                            data = r.json().get("data")[0]
                        except IndexError:
                            data = r.json().get("data")
                        except JSONDecodeError:
                            logging.error(data)
                            raise

                        if len(data) > 1:
                            try:
                                wr.writerows(data)
                            except Exception as e:
                                logging.error(data)
                                raise e
                        elif len(data) == 0:
                            pass
                        else:
                            wr.writerow(data[0])

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
                    r = self.client.get_raw(endpoint_mapping.get("endpoint"), params=params)
                    wr.writerows(r.json().get("data"))
                    page += self.limit
                    if r.json().get("paging").get("nItems") < self.limit:
                        has_more = False
                wr.writeheader()
