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
NEST_AUTHORIZATION = 'authorization'
NEST_TIME_RANGE = 'time-range'
KEY_INCREMENT = 'increment'

# list of mandatory parameters => if some is missing,
# component will fail with readable message on initialization.
REQUIRED_PARAMETERS = [NEST_AUTHORIZATION, NEST_TIME_RANGE]
# KEY_EMAIL, KEY_PASSWORD, KEY_COMPANY_ID, KEY_ENDPOINTS
# set up nested parameters here
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
        self.email = params.get(NEST_AUTHORIZATION).get(KEY_EMAIL)
        self.password = params.get(NEST_AUTHORIZATION).get(KEY_PASSWORD)
        self.company_id = params.get(NEST_AUTHORIZATION).get(KEY_COMPANY_ID)
        _from = params.get(NEST_TIME_RANGE).get(KEY_FROM)
        _to = params.get(NEST_TIME_RANGE).get(KEY_TO)
        self.now = datetime.now()
        self.dt_format = "%Y-%m-%dT%H:%M:%S"
        self._from, self._to = self.make_ts_from_ts_string(_from, _to)
        self.increment = params.get(KEY_INCREMENT)
        if not self.increment:
            self.increment = False

        endpoints = params.get(KEY_ENDPOINTS)
        self.endpoints = []
        for endpoint in endpoints:
            if endpoint in ENDPOINTS:
                if endpoints.get(endpoint):
                    self.endpoints.append(endpoint)
            else:
                raise UserException(f"Endpoint {endpoint} is not supported.")
        self.endpoints.sort()
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
                                                     primary_key=ENDPOINT_MAPPING[endpoint]["pks"],
                                                     incremental=self.increment)
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
