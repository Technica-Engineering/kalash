"""
META_START
---
id: X-DEV.Y-GROUP-Z-TEST
relatedUseCases:
  - PRODTEST-YYYY
workbenches:
  - ZZZZ
META_END
"""

from parameterized import parameterized
import prost  # noqa: F401
from kalash.run import TestCase, main, MetaLoader, get_ts


class TestTemplate(TestCase):  # IMPORTANT: Name of class should be changed here

    # Declaration of order of execution
    @parameterized.expand([(get_ts(__qualname__))])
    def test_validation(self, name):  # IMPORTANT: This whole method should never be changed
        """
        INTERACTION: DEFINITION OF WHAT IS DONE TO INTERACT WITH THE DUTS
        VALIDATION: DEFINITION OF WHAT VALIDATION CONSISTS ON
        TEST OK: DESCRIBE HOW THE TEST CONSIDERS ITSELF OK
        TEST NOK: DESCRIBE HOW THE TEST CONSIDERS ITSELF NOK

        Below the description of the test you can write any additional comments you need
        for your test case, as they will be automatically added to the report.
        """

        try:
            self.configuration()
            self.interaction()
            self.validation()
        finally:
            self.restoration()

    # First step: Configure the DUTs the way we need in order to execute the test
    def configuration(self):  # IMPORTANT: Name of methods never change
        """DEFINITION OF WHAT CONFIGURATION IS DONE TO THE DUTS"""

        """
        CODE SHOULD BE:
            CONFIGURATION_CODE_LINE
            print("LOG WHAT HAS BEEN DONE")
            FILE_FROM_PATH_OR_URL
            print("READ XYZ FILE")
        """

    # Second step: Interact with the DUTs as the test requires
    def interaction(self):  # IMPORTANT: Name of methods never change
        """DEFINITION OF WHAT IS DONE TO INTERACT WITH THE DUTS"""

        """
        CODE SHOULD BE:
            INTERACTION_CODE_LINE
            print("LOG WHAT HAS BEEN DONE")
        """

    # Third step: Validate data within the DUTs in order to evaluate if the test is OK or NOK
    def validation(self):  # IMPORTANT: Name of methods never change
        """DEFINITION OF WHAT VALIDATION CONSISTS ON"""

        # List of NOK messages to be shown as failed in the error output of the report
        message_nok_list = []

        """
        CODE SHOULD BE:
            print("STARTING TO DO VALIDATION XYZ")
            VALIDATION_CODE_BLOCK
            if VALIDATION OK
                message = LOG INFO VALIDATION OK
            else (VALIDATION NOK)
                message = LOG INFO VALIDATION NOK
                message_nok_list.append(message)
            print(message)
        """

        # Determines if the test was NOK or OK based on wheteher the list of
        # NOK messages has values or not
        self.assertListEqual(message_nok_list, [], message_nok_list)

    # Fourth step: Restore the DUTs to their default state
    def restoration(self):  # IMPORTANT: Name of methods never change
        """DEFINITION OF HOW WE RESTORE THE DUTS TO THEIR DEFAULT STATE"""

        """
        CODE SHOULD BE:
            RESTORING_CODE_LINE
            print("LOG WHAT HAS BEEN DONE")
        NOTE THAT YOU MUST CHECK BEFORE RESTORING IF THE DUT HAS BEEN CONNECTED
        """


# Executes the test and configures the report destination on local executions
if __name__ == '__main__':
    main(testLoader=MetaLoader(yaml_path='./yamls/.kalash.yaml'))
