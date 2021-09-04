import os
import re
import datetime

from xml.etree import ElementTree as ET


def is_test_result(xml_attribute):
    """
    Produces a lambda that checks a list of attributes 
    in an XML `testcase` section against the one specified 
    when filling the closure.

    Args:
        xml_attribute (str): attribute of the section searched for

    Returns:
        function that takes a list of attributes as a parameter
    """
    return lambda attr_list: xml_attribute in attr_list


is_test_fail = is_test_result('failure')
is_test_error = is_test_result('error')
is_test_fail_or_error = lambda x: is_test_result('failure')(x) or is_test_result('error')(x)
# when passed there is just stdout and stderr section but no error or failure:
is_test_pass = lambda attr_list: not is_test_fail_or_error(attr_list)


def filter_for_result(check_lr_tag_function):
    """
    Last result filtering function.

    Args:
        check_lr_tag_function (function): a lambda returning a boolean value
            depending on whether a specific XML attribute is present in a `testcase`
            section of the XML report

    Returns:
        A closure function bound to specific "OK"/"NOK" `lastResult`
    """

    def process_xml_tree(path_to_xml):
        """
        Processes a single XML report and returns `testcase` section
        if the report isn't spawned from `unittest._ErrorHolder`.

        Args:
            path_to_xml (str): path to a valid XMLRunner report

        Returns:
            List of XML Elements (xml.etree.ElementTree.Element)
            or an empty list when `_ErrorHolder` is encountered
        """
        if str(path_to_xml).endswith('.xml'):
            xml_tree = ET.parse(path_to_xml)
            xml_tree_root = xml_tree.getroot()
            if re.search(r'_ErrorHolder', xml_tree_root.attrib['name']):
                # parsing unittest._ErrorHolder cases is not supported
                return list()
            else:
                return xml_tree_root.findall('testcase')

    def closure(single_test_path, reports_path):
        """
        Last result filtering closure.

        Args:
            single_test_path (str): path to a test being currently processed
                by the callback in `kalash`'s test loader 
                (see: `metaparser.apply_filters()`)
            reports_path (str): path to the reports folder

        Returns:
            Array of booleans as used in `metaparser.apply_filters()`
        """
        results = dict()
        for root, dirs, files in os.walk(os.path.abspath(reports_path)):
            for name in files:
                single_report_path = os.path.join(root, name)
                # extract all `testcase` sections from the XML:
                test_cases = process_xml_tree(single_report_path)
                if test_cases:
                    for tc in test_cases:
                        # record all underlying tags in XML tree
                        result_tags = [child.tag for child in tc]
                        file_path = tc.attrib['file']              # record file path
                        # check the result tag in the report (whether it is the one you want when filtering)
                        # and if the file path is corresponding to the current test file:
                        if (os.path.abspath(file_path) == os.path.abspath(single_test_path)):
                            results[single_report_path] = \
                                datetime.datetime.strptime(
                                    tc.attrib['timestamp'], "%Y-%m-%dT%H:%M:%S")
        try:
            last_report_path = [k for k, _ in sorted(results.items(), key=lambda x: x[1])][-1]
            test_cases_that_pass_predicate = []
            test_cases = process_xml_tree(last_report_path)
            if test_cases:
                for tc in test_cases:
                    result_tags = [child.tag for child in tc]
                    test_cases_that_pass_predicate.append(check_lr_tag_function(result_tags))
        except (KeyError, IndexError):
            # when key error or IndexError encountered it means that the folder contains no reports yet
            test_cases_that_pass_predicate = [False]

        return test_cases_that_pass_predicate

    return closure
