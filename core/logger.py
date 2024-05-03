import logging
from logging.handlers import RotatingFileHandler
import os
import copy
import shutil
from pprint import pformat
#from core.config import settings

pid = os.getpid()

max_bytes = 10_000_000


class ColoredFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        self.COLORS = {
            'WARNING': '\033[33m',  # Yellow
            'INFO': '\033[32m',    # Green
            'DEBUG': '\033[34m',   # Blue
            'CRITICAL': '\033[35m', # Magenta
            'ERROR': '\033[31m'    # Red
        }
        self.RESET = '\033[0m' # Reset to default
        super().__init__(*args, **kwargs)

    def format(self, record):
        colored_record = copy.copy(record)
        levelname = colored_record.levelname
        seq = self.COLORS.get(levelname, self.RESET)
        colored_levelname = f'{seq}{levelname:<8}{self.RESET}'
        colored_record.levelname = colored_levelname
        return super().format(colored_record)


def init_logger(name, log_file, level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter(f'%(asctime)s - %(levelname)-8s {pid} --- [%(filename)+15s:%(lineno)3d] | %(message)s')
    fh = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=5)
    fh.setFormatter(formatter)

    # Create a handler for writing to stdout
    cmd_formatter = ColoredFormatter(f'%(asctime)s - %(levelname)-8s {pid} --- [%(filename)+15s:%(lineno)3d] | %(message)s')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(cmd_formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(fh)
    return logger


main_logger = init_logger("main_logger", "./scraper.log")





# terminal_width = shutil.get_terminal_size().columns
# title = "CONFIGURATION"
# print(f"{'='*((terminal_width - len(title) - 1) // 2)} {title} {'='*((terminal_width - len(title) - 1) // 2)}")  # noqua
# main_logger.info(pformat(settings.model_dump()))
# print(f"{'='*terminal_width}")