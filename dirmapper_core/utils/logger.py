import logging
import threading
import time
import traceback
from typing import Type, TYPE_CHECKING

# Only runs for type checking and avoids circular imports in runtime; does not affect runtime
if TYPE_CHECKING:
    from dirmapper_core.ignore.path_ignorer import PathIgnorer

def setup_logger(name, level="INFO", verbose:bool = False):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(level)

    # Create formatter
    if verbose:
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    else:
        formatter = logging.Formatter('%(levelname)s - %(message)s')

    # Add formatter to ch
    ch.setFormatter(formatter)

    # Add ch to logger
    if not logger.handlers:
        logger.addHandler(ch)

    return logger

logger = setup_logger(__name__)

def log_exception(file_name:str, exc: Exception, stacktrace: bool = False) -> None:
    """
    Log an exception with the file name and optionally the stack trace.

    Args:
        file_name (str): The name of the file where the exception occurred.
        exc (Exception): The exception that occurred.
        stacktrace (bool): Whether to include the stack trace in the log message.
    """
    logger.error("%s: %s", file_name, exc)
    if stacktrace:
        logger.error("Stack Trace:", exc_info=True)

def log_ignored_paths(ignorer: Type["PathIgnorer"]) -> None:
    """
    Log the ignored paths from the PathIgnorer object.
    
    Args:
        ignorer (PathIgnorer): The PathIgnorer object to log ignored paths from.
    """
    root_counts = ignorer.get_root_ignored_counts()
    root_directories = ignorer.get_root_directories()
    for root_dir in root_directories:
        logger.info(f"Ignoring {root_counts[root_dir]} paths in root ignored folder '{root_dir}'")

def log_periodically(custom_message: str, time_interval: int, include_time: bool = True) -> None:
    """
    Function to log a custom message at regular intervals with threads. 
    The function will log the message every time_interval seconds until stop_logging is set. 
    Threads are used to allow the main program to continue running while logging occurs.

    Args:
        custom_message (str): The message to log.
        time_interval (int): The time interval in seconds between each log.
        include_time (bool): Whether to include the time elapsed in the log message
    """
    start_time = time.time()
    while not stop_logging.is_set():
        elapsed_time = int(time.time() - start_time)
        if include_time:
            logger.info(f"{custom_message} [{elapsed_time} sec]")
        else:
            logger.info(custom_message)
        time.sleep(time_interval)

stop_logging = threading.Event()
logging_thread = threading.Thread(target=log_periodically)
