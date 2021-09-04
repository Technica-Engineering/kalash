import os
from typing import Callable, List
import unittest

from .config import Collector, CliConfig, CollectorArtifact, OneOrList, PathOrIdForWhatIf, TestPath, Trigger


def make_test_loader(trigger: Trigger) -> Callable[
    [OneOrList[TestPath],Collector], CollectorArtifact
]:
    """Creates a test loader function based on a
    provided `Trigger` instance.

    Args:
        trigger (Trigger): `Trigger` instance
    """
    
    def test_loader(
        paths: OneOrList[TestPath],
        callback: Collector
    ) -> CollectorArtifact:
        """
        Main loader function that iterates over directories and
        grabs tests. If the path leads to a single Python file,
        only that file is executed, otherwise the directory
        is searched for Python files that are all treated as
        potential candidate files containing tests.

        Args:
            paths (OneOrList[TestPath]): one or more paths to tests
                or directories of tests
            callback (Collector): callback that adds tests to suite
                based on a test template definition
        
        Returns:
            A `CollectorArtifact`
        """

        def _handle_one_test(
            root: str,
            file: str,
            suite: unittest.TestSuite,
            identifiers: PathOrIdForWhatIf
        ):
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                merger_suite, merger_identifiers = callback(full_path, trigger)
                if merger_suite:
                    for test in merger_suite:
                        # iteration necessary, otherwhise we end up with nested
                        # `TestSuites` which we don't want here
                        suite.addTest(test)
                    identifiers.extend(merger_identifiers)
            return suite, identifiers

        suite = unittest.TestSuite()
        identifiers: PathOrIdForWhatIf = []
        
        if type(paths) is str:
            # wrap paths in a list if the test conf contains just a single path
            paths = [paths]
        
        for path in paths:
            if path.endswith(".py"):
                # if it's a path to a single test, just run it
                merger_suite, merger_identifiers = callback(path, trigger)
                for test in merger_suite:
                    suite.addTest(test)
                identifiers.extend(merger_identifiers)
            else:
                try:
                    if not trigger.cli_config.no_recurse:
                        # default into recursive test grabbing
                        for root, dirs, files in os.walk(path):
                            for file in files:
                                suite, identifiers = \
                                    _handle_one_test(root, file, suite, identifiers)
                    else:
                        for file in os.listdir(path):
                            suite, identifiers = \
                                _handle_one_test(path, file, suite, identifiers)
                except NotADirectoryError:
                    raise NotADirectoryError("The path must be a valid folder or .py file")
        return suite, identifiers

    return test_loader
