'''
Template Component main class.

'''
import csv
import logging
from datetime import datetime

from keboola.component.base import ComponentBase
from keboola.component.exceptions import UserException
from timedoctor2.client import TimeDoctor2Client, TimeDoctor2ClientError
from timedoctor2.endpoint_mapping import ENDPOINT_MAPPING

# configuration variables
KEY_EMAIL = 'email'
KEY_PASSWORD = '#password'
KEY_COMPANY_ID = "company_id"
KEY_ENDPOINTS = "endpoints"
KEY_MODE = 'mode'
KEY_FROM = 'from'
KEY_TO = 'to'

# list of mandatory parameters => if some is missing,
# component will fail with readable message on initialization.
REQUIRED_PARAMETERS = [KEY_EMAIL, KEY_PASSWORD, KEY_COMPANY_ID, KEY_ENDPOINTS, KEY_MODE]


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
        self.endpoints = params.get(KEY_ENDPOINTS)
        self.mode = params.get(KEY_MODE)
        self._from = params.get(KEY_FROM)
        self._to = params.get(KEY_TO)

    def run(self):
        """
        Main execution code
        """
        try:
            client = TimeDoctor2Client(email=self.email, password=self.password, company_id=self.company_id,
                                       mode=self.mode, _from=self._from, _to=self._to)
        except TimeDoctor2ClientError as e:
            raise UserException(f"Cannot initialize TimeDoctor 2 client, error: {e}") from e

        for endpoint in self.endpoints:
            logging.info(f"Processing endpoint: {endpoint}")
            table = self.create_out_table_definition(ENDPOINT_MAPPING[endpoint]["table_name"],
                                                     primary_key=['id'], incremental=True)
            client.process_endpoint(endpoint, table)

        exit()

        table = self.create_out_table_definition("users.csv", primary_key=['id'], incremental=True)
        client.get_users(table)
        self.write_manifest(table)

        # get last state data/in/state.json from previous run
        previous_state = self.get_state_file()
        logging.info(previous_state.get('some_state_parameter'))

        # Save table manifest (output.csv.manifest) from the tabledefinition
        self.write_manifest(table)

        # Write new state - will be available next run
        self.write_state_file({"some_state_parameter": "value"})

        # ####### EXAMPLE TO REMOVE END


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
