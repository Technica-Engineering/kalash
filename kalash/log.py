import os
import sys
import logging
from typing import List, Optional, Set, Union, Callable

from .utils import get_ts
from .config import CliConfig, Meta, OneOrList

PathType = Union[os.PathLike, str]

_LOGGERS: Set[logging.Logger] = set()

HANDLERS: List[Callable[..., logging.Handler]] = [lambda n: logging.FileHandler(n)]


def _get_logger_from_state(logger_name: str) -> Optional[logging.Logger]:
    loggers = list(filter(lambda l: l.name == logger_name, _LOGGERS))
    if len(loggers) > 0:
        return loggers[0]
    else:
        return None


def _create_tree_if_not_exists(path: PathType) -> None:
    if not os.path.exists(path):
        os.makedirs(path)


def _make_log_tree_from_id(
    id: str,
    class_name: str,
    meta: Meta,
    groupby: Optional[str] = None
):
    """Creates log tree structure representation based on the
    test template keys. By default it does not group
    the logs at all. Any key from the metadata tag
    can be used to group by.

    Args:
        id (str): test ID from the metadata tag
        class_name (str): test class name
        groupby (Optional[str]): what property to group log
            directories by

    Returns:
        A `str` path to the target directory where logs will
            be stored.
    """
    dir_name = id + '_' + class_name
    log_name = get_ts(sep='') + '_' + dir_name
    full_path = ""
    if groupby:
        _group_dir_name: OneOrList[str] = getattr(meta, groupby)
        group_dir_name: Optional[str] = ""
        if type(_group_dir_name) is list:
            group_dir_name = "_".join(_group_dir_name)
        elif type(_group_dir_name) is str:
            group_dir_name = _group_dir_name
        else:
            group_dir_name = None
        group_dir_name = group_dir_name if group_dir_name else "unknown_group"
        full_path = os.path.join(dir_name, group_dir_name, log_name)
    else:
        full_path = os.path.join(dir_name, log_name)
    return full_path


def _make_trunk(
    log_name: PathType,
    log_base_path: Optional[PathType] = None
):
    """Creates a trunk directory structure
    for the logs if it does not exist, returns
    the path to a concrete log file.
    """
    if log_base_path:
        log_path = os.path.join(
            log_base_path,
            log_name
        )

    else:
        log_path = os.path.join(
            '.',
            log_name
        )

    # create the trunk part (don't touch the log file name)
    _create_tree_if_not_exists(os.path.dirname(log_path))

    # return the full path with `.log` to the caller
    return log_path + '.log'


def _make_tree(
    id: str,
    class_name: str,
    meta: Meta,
    log_base_path: Optional[PathType] = None,
    groupby: str = None
):
    """Combines `_make_trunk_` with `_make_log_tree_from_id`."""
    return _make_trunk(
        _make_log_tree_from_id(id, class_name, meta, groupby=groupby),
        log_base_path
    )


def _register_logger(
    logger_name: str,
    log_handlers: List[logging.Handler],
    log_level: int,
    log_format: logging.Formatter
) -> Optional[logging.Logger]:
    """
    Creates and registers logger instances.
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)

    for log_handler in log_handlers:
        log_handler.setFormatter(log_format)
        logger.addHandler(log_handler)

    if logger.name not in [l.name for l in _LOGGERS]:  # noqa: E741
        _LOGGERS.add(logger)
        return logger
    # return `None` if logger already existed!
    return None


def register_logger(
    logger_name: str,
    log_file_path: str,
    config: CliConfig
) -> Optional[logging.Logger]:
    """
    Creates and registers logger instances.
    Declares default path handlers and if `no_log_echo`
    is `False` (default) a STDOUT handler will be added
    so all log calls will be echoed to the calling console.

    Args:
        logger_name (str): class name that becomes the unique
            name of the logger. If you have two classes with
            the same name, then the same logger will be used
        log_file_path (str): path to the associated log file
            where logger calls will be written
        config (CliConfig): a `CliConfig` instance representing
            the configuration that the application user
            provided via the CLI

    Return:
        `logging.Logger` instance if a new logger instance
            has been created. `None` if the logger instance
            already existed for this particular `logger_name`
    """
    handlers = [f(log_file_path) for f in HANDLERS]
    if not config.no_log_echo:
        # extend with a console handler piping to STDOUT
        # (`logging` uses STDERR by default)
        handlers += [logging.StreamHandler(sys.stdout)]
    return _register_logger(
        logger_name,
        handlers,
        config.log_level,
        logging.Formatter(config.log_format)
    )


def get(
    id: str,
    class_name: str,
    meta: Meta,
    config: CliConfig
) -> logging.Logger:
    """Creates or returns an existing `logging.Logger` instance
    associated with a particular `class_name`.

    Args:
        id (str): unique ID of the test
        class_name (str): name of the test class
        config (CliConfig): a `CliConfig` instance representing
            the configuration that the application user
            provided via the CLI

    Returns:
        Associated `logging.Logger` instance
    """
    path = _make_tree(id, class_name, meta, config.log_dir, config.group_by)

    l = _get_logger_from_state(class_name)  # noqa: E741

    if not l:
        new_logger = register_logger(class_name, path, config)
        if not new_logger:
            raise ValueError(f"Logger not registered correctly! {class_name}")
        else:
            return new_logger
    else:
        return l


def close(logger: Union[str, logging.Logger]):
    """
    Closes open file handles used by an associated `logger`,
    removes the handlers and removes loggers from
    the managed set.

    Args:
        logger (logging.Logger): the `logging.Logger` instance
            to close

    Returns: `None`
    """
    if type(logger) is str:
        l = _get_logger_from_state(logger)  # noqa: E741
    elif type(logger) is logging.Logger:
        l = logger  # noqa: E741
    else:
        raise NameError(
            f'{logger} is not a logger, nor a logger name! '
            'Make sure you use a string or logger instance '
            'with this method.'
        )
    if l:
        for h in l.handlers:
            h.close()
            l.removeHandler(h)
        try:
            _LOGGERS.remove(l)
        except KeyError:
            pass


def close_all():
    """
    Forces all loggers to perform a managed `shutdown`.
    Should always be called by the method/function
    running the Kalash tests.
    """
    logging.shutdown()
