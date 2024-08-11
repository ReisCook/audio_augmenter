import os
import logging
from datetime import datetime

class Logger:
    def __init__(self, verbosity_level, log_dir):
        self.verbosity_level = int(verbosity_level)
        self.log_dir = log_dir

        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        log_file = os.path.join(self.log_dir, f"synthesis_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

        logging.basicConfig(
            level=self._get_log_level(),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

        self.logger = logging.getLogger(__name__)

    def _get_log_level(self):
        if self.verbosity_level == 0:
            return logging.WARNING
        elif self.verbosity_level == 1:
            return logging.INFO
        else:
            return logging.DEBUG

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)