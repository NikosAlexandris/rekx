from loguru import logger
logger.remove()
import re
from datetime import datetime
from rich import print
from .constants import VERBOSE_LEVEL_DEFAULT
verbosity_level = VERBOSE_LEVEL_DEFAULT


def filter_function(record):
    """Determine which logs to include based on the verbosity level."""
    # Assuming record["level"].name gives the log level like "INFO", "DEBUG", etc.
    # return verbose
    return record["level"].name == "INFO" if verbosity_level == 1 else True


logger.add("kerchunking_{time}.log", filter=filter_function)#, compression="tar.gz")


def print_log_messages(start_time, end_time, log_file_name):
    with open(log_file_name, 'r') as log_file:
        for line in log_file:
            match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*', line)
            if match:
                timestamp_str = match.group(1)
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                if start_time <= timestamp <= end_time:
                    print(line.strip())
