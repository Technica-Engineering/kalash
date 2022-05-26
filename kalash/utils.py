__docformat__ = "google"

import datetime
import os
from typing import Union
from toolz import pipe


def get_ts(name='', format="%Y%m%d%H%M%S", sep='-'):
    """
    Attaches a formatted timestamp to a name passed
    as the first argument. Utility function used in test
    templates.

    Args:
        name (str): name to add `"-timestamp"` to
        format (str): `strftime` format string

    Returns:
        When called with e.g. `"Something"` at
        9 AM 2020.02.14, it will return a string like
        `"Something-20200214090000"`
    """
    return name + sep + datetime.datetime.now().strftime(format)


def _interpolate_workdir(ipt: str, workdir_tag: str) -> str:
    """Interpolates CWD variable. This variable is used to
    resolve paths within Kalash YAML relative to the current
    working directory. Equivalent to using the dotted file path.

    Args:
        ipt (str): input string to interpolate
        workdir_tag (str): the tag to look for indicating the workdir

    Returns: interpolated string
    """
    return os.path.normpath(
        ipt.replace(
            workdir_tag, os.getcwd()
        )
    )


def _interpolate_this_file(ipt: str, thisfile_tag: str, yaml_abspath: str) -> str:
    """Interpolates THIS_FILE variable. THIS_FILE is used to resolve
    paths within Kalash YAML relative to the YAML file itself.

    Args:
        ipt (str): input string to interpolate
        thisfile_tag (str): the tag to look for indicating current file
        yaml_abspath (str): path to the Kalash YAML file
                or the `.py` configuration file

    Returns: interpolated string
    """
    return os.path.normpath(
        ipt.replace(
            thisfile_tag,
            os.path.dirname(yaml_abspath)
        )
    )


def _interpolate_all(
    ipt: Union[str, None],
    thisfile_tag: str,
    workdir_tag: str,
    yaml_abspath: str
) -> Union[str, None]:
        """Interpolates all variable values using a toolz.pipe

        Args:
            ipt (str): input string to interpolate
            yaml_abspath (str): path to the Kalash YAML file
                or the `.py` configuration file

        Returns: interpolated string
        """
        if ipt:
            return pipe(
                _interpolate_this_file(ipt, thisfile_tag, yaml_abspath),
                lambda ipt: _interpolate_workdir(ipt, workdir_tag)
            )
        return ipt
