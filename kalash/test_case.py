from typing import List, Optional
import unittest
import logging

from .config import CliConfig, Config, Trigger
from .log import get, close


class TestCase(unittest.TestCase):
    """
    Lightweight `unittest.TestCase` wrapper.

    When declaring your own tests you're supposed to
    inherit from this class and treat it pretty much
    the same as a good old-fashioned `unittest.TestCase`.

    For example:

    ```python
    \"\"\"
    META_START
    id: test_something_12345
    META_END
    \"\"\"
    
    from kalash.run import main, TestCase, MetaLoader


    class TestSomething(TestCase):
        test_something(self):
            self.assertTrue(True)
    

    if __name__ == '__main__'
        main(testLoader=MetaLoader())
    ```
    
    Args:
        methodName (str): test method
        id (str): test ID from the metadata tag
        trigger (Trigger): `Trigger` instance 
    """

    def __init__(
        self,
        methodName: str,
        id: str,
        trigger: Optional[Trigger]
    ) -> None:
        super().__init__(methodName=methodName)
        cli_config = trigger.cli_config if trigger else CliConfig()
        self._id = id
        self.log_base_path = cli_config.log_dir if cli_config else None
        self.groupby = cli_config.group_by if cli_config else None
        self.no_log_echo = cli_config.no_log_echo if cli_config else None
        self.trigger = trigger

        # inject logger:
        if cli_config:
            if not cli_config.no_log:
                self.logger = get(
                    id,
                    self.__class__.__name__,
                    cli_config
                )
            else:
                # create dummy non-functional logger on the spot when
                # running with `log=False`
                self.logger = logging.getLogger(self.__class__.__name__)
                # close and clear all handlers that sb could have opened
                # by accident
                for h in self.logger.handlers:
                    h.close()
                self.logger.handlers = []
    
    def allow_when(self, allowed_parameters_config_property: str, parameter_on_test_case: str):
        """When running with a custom configuration class, you can use this
        method to tell your test case to not be skipped on some runtime filter.
        This is useful mostly when using Kalash with `parameterized`. 
        
        Consider the following example:
        ```python
        class TestAdvancedFiltering1(TestCase):
            @parameterized.expand(['lincombo', 'cancombo'])
            def test_1(self, name):
                self.allow_when('run_only_with', name)
                print(f"Running for {name}")
        ```

        If at runtime the config object contains a `run_only_with=['cancombo']`
        value, the test will only be triggered for `cancombo`.

        Args:
            allowed_parameters_config_property (str): property name on the
                `config` section of the `Trigger` instance containing the
                skip/allow (must be a `List`).
            parameter_on_test_case (str): parameter value to find in the
                allowed list, coming from the test case
        """
        if self.trigger:
            run_with: Optional[List[str]] = self.trigger.config.get(allowed_parameters_config_property)
            if run_with:
                if parameter_on_test_case in run_with:
                    return
                else:
                    import inspect
                    caller = inspect.stack()[1].function
                    self.skipTest(f"{parameter_on_test_case} made test function {caller} skip")

    def __del__(self):
        if hasattr(self, 'logger'):
            close(self.logger)
