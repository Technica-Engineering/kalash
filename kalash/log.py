import os
import sys
import logging
from typing import List, Optional, Set, Union, Callable
from dataclasses import dataclass

from .utils import get_ts
from .config import CliConfig, Spec

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
    groupby: Optional[str]=None
):
    """Creates log tree structure representation based on the
    test template keys. By default it does not group
    the logs at all. Any key from the metadata tag
    can be used to group by.
    
    Args:
        
    """
    # LATER: improved grouping based on arbitrary keys from the meta tag
    dir_name = id + '_' + class_name
    # PRODTEST_1234_test_something_TestSomething_0_cancombo
    log_name = get_ts(sep='') + '_' + dir_name
    # 00000000_PRODTEST_1234_test_something_TestSomething_0_cancombo
    return os.path.join(dir_name, log_name)


def _make_trunk(
    log_name: PathType,
    log_base_path: Optional[PathType]=None
):
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
    log_base_path: Optional[PathType]=None,
    groupby: str=None
):
    return _make_trunk(
        _make_log_tree_from_id(id, class_name, groupby=groupby),
        log_base_path
    )


def _register_logger(
    logger_name: str,
    log_handlers: List[logging.Handler],
    log_level: int,
    log_format: logging.Formatter
) -> Optional[logging.Logger]:

    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)

    for log_handler in log_handlers:
        log_handler.setFormatter(log_format)
        logger.addHandler(log_handler)

    if logger.name not in [l.name for l in _LOGGERS]:
        _LOGGERS.add(logger)
        return logger
    # return `None` if logger already existed!
    return None


def register_logger(
    logger_name: str,
    log_file_path: str,
    config: CliConfig
) -> Optional[logging.Logger]:
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
    config: CliConfig
) -> logging.Logger:
    path = _make_tree(id, class_name, config.log_dir, config.group_by)

    l = _get_logger_from_state(class_name)
    
    if not l:
        new_logger = register_logger(class_name, path, config)
        if not new_logger:
            raise ValueError(f"Logger not registered correctly! {class_name}")
        else:
            return new_logger
    else:
        return l


def close(logger: Union[str, logging.Logger]):
    if type(logger) is str:
        l = _get_logger_from_state(logger)
    elif type(logger) is logging.Logger:
        l = logger
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
    logging.shutdown()
