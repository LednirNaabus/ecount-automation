import logging

class EcountLogger:
    """
    Just a basic logger for the Ecount automation.
    """
    def __init__(self, name: str, filename: str, mode: str, level=logging.NOTSET):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level=level)

        if not self.logger.handlers:
            console_formatter = logging.Formatter("%(name)-12s: %(levelname)-8s %(message)s", datefmt="%Y-%m-%d")
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(console_formatter)

            file_handler = logging.FileHandler(filename=filename, mode=mode)
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %I:%M:%S %p")
            file_handler.setFormatter(file_formatter)

            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)

    def info(self, message):
        self.logger.info(message)

    def debug(self, message):
        self.logger.debug(message)

    def error(self, message):
        self.logger.error(message)

    def warning(self, message):
        self.logger.warning(message)