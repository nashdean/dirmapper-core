import logging
import threading
import time
import traceback
from typing import Type
from dirmapper_core.ignore.path_ignorer import PathIgnorer

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger(__name__)

def log_exception(file_name:str, exc: Exception, stacktrace: bool = False) -> None:
    logger.error("%s: %s", file_name, exc)
    if stacktrace:
        logger.error("Stack Trace:", exc_info=True)

def log_ignored_paths(ignorer: Type[PathIgnorer]) -> None:
    root_counts = ignorer.get_root_ignored_counts()
    root_directories = ignorer.get_root_directories()
    for root_dir in root_directories:
        logger.info(f"Ignoring {root_counts[root_dir]} paths in root ignored folder '{root_dir}'")

def log_periodically(custom_message: str, time_interval: int, include_time: bool = True) -> None:
    """
    Function to log a custom message at regular intervals with threads.

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
