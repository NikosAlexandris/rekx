from loguru import logger
logger.remove()
# logger.add("kerchunking_{time}.log")#, compression="tar.gz")
import re
from datetime import datetime
from rich import print


def print_log_messages(start_time, end_time, log_file_name):
    with open(log_file_name, 'r') as log_file:
        for line in log_file:
            match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*', line)
            if match:
                timestamp_str = match.group(1)
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                if start_time <= timestamp <= end_time:
                    print(line.strip())
