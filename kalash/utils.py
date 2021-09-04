import datetime


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
