'''
Template Component main class.

'''
import logging
from datetime import datetime

from keboola.component.base import ComponentBase
from keboola.component.exceptions import UserException
from timedoctor2.client import TimeDoctor2Client, TimeDoctor2ClientError
from timedoctor2.endpoint_mapping import ENDPOINT_MAPPING
from keboola.utils import parse_datetime_interval

# configuration variables
KEY_EMAIL = 'email'
KEY_PASSWORD = '#password'
KEY_COMPANY_ID = "company_id"
KEY_ENDPOINTS = "endpoints"
KEY_FROM = 'from'
KEY_TO = 'to'
KEY_USE_RELATIVE_RANGE = 'use_relative_range'
KEY_RELATIVE_RANGE = 'relative_range'

# list of mandatory parameters => if some is missing,
# component will fail with readable message on initialization.
REQUIRED_PARAMETERS = [KEY_EMAIL, KEY_PASSWORD, KEY_COMPANY_ID, KEY_ENDPOINTS, KEY_USE_RELATIVE_RANGE]
ENDPOINTS = list(ENDPOINT_MAPPING.keys())


class Component(ComponentBase):
    """
        Extends base class for general Python components. Initializes the CommonInterface
        and performs configuration validation.

        For easier debugging the data folder is picked up by default from `../data` path,
        relative to working directory.

        If `debug` parameter is present in the `config.json`, the default logger is set to verbose DEBUG mode.
    """

    def __init__(self):
        super().__init__()
        self.validate_configuration_parameters(REQUIRED_PARAMETERS)
        params = self.configuration.parameters
        self.email = params.get(KEY_EMAIL)
        self.password = params.get(KEY_PASSWORD)
        self.company_id = params.get(KEY_COMPANY_ID)
        self.now = datetime.now()
        self.use_relative_range = params.get(KEY_USE_RELATIVE_RANGE)
        self.relative_range = params.get(KEY_RELATIVE_RANGE)
        # endpoints = params.get(KEY_ENDPOINTS)
        # endpoints.sort()
        # self.endpoints = endpoints
        self.dt_format = "%Y-%m-%dT%H:%M:%S"
        _from = params.get(KEY_FROM)
        _to = params.get(KEY_TO)
        self._from, self._to = self.make_ts_from_ts_string(_from, _to)

        endpoints = params.get("endpoints")
        self.endpoints = []
        for endpoint in endpoints:
            if endpoint in ENDPOINTS:
                if endpoints.get(endpoint):
                    self.endpoints.append(endpoint)
            else:
                raise UserException(f"Endpoint {endpoint} is not supported.")
        logging.info(f"Component will process following endpoints: {self.endpoints}")

    def run(self):
        """
        Main execution code
        """
        logging.info(f"Component will use custom time window to fetch data from {self._from} to {self._to}")

        try:
            client = TimeDoctor2Client(email=self.email, password=self.password, company_id=self.company_id,
                                       _from=self._from, _to=self._to)
        except TimeDoctor2ClientError as e:
            raise UserException(f"Cannot initialize TimeDoctor 2 client, error: {e}") from e

        for endpoint in self.endpoints:
            logging.info(f"Processing endpoint: {endpoint}")
            table = self.create_out_table_definition(ENDPOINT_MAPPING[endpoint]["table_name"],
                                                     primary_key=ENDPOINT_MAPPING[endpoint]["pks"], incremental=True)
            client.process_endpoint(endpoint, table)
            self.write_manifest(table)
            if endpoint == '_users':
                client.get_list_of_users(table.full_path)

    def make_ts_from_ts_string(self, _from, _to):
        _from = _from if _from != "" else "now"
        _to = _to if _to != "" else "now"
        print(_from, _to)
        start_date, end_date = parse_datetime_interval(_from, _to, self.dt_format)
        return start_date, end_date

    def get_relative_date(self):
        start_date, end_date = parse_datetime_interval(self.relative_range,
                                                       self.now.strftime(self.dt_format), self.dt_format)
        return start_date


"""
        Main entrypoint
"""
if __name__ == "__main__":
    try:
        comp = Component()
        # this triggers the run method by default and is controlled by the configuration.action parameter
        comp.execute_action()
    except UserException as exc:
        logging.exception(exc)
        exit(1)
    except Exception as exc:
        logging.exception(exc)
        exit(2)
