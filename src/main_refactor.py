"""
Contains logger set up and main loop code.
"""
import logging

# Import necessary functions
from lfdaq_ingester.ingester import Ingester 

# Start logger
logger = logging.getLogger(__name__)

log_formatter = logging.Formatter('%(asctime)s   :%(levelname)s:%(name)s: %(message)s')

log_file = logging.FileHandler(f'{__name__}.log')
log_file.setLevel(logging.DEBUG)
log_file.setFormatter(log_formatter)
logger.addHandler(log_file)

log_stream = logging.StreamHandler()
log_stream.setLevel(logging.DEBUG)
log_stream.setFormatter(log_formatter)
logger.addHandler(log_stream)
logger.info("Started Logging")
def main() -> None:
    """
    Runs the main lfdaq_ingester loop.
    """
    with Ingester() as daq_ingester:
        try:
            daq_ingester.loop()
        except Error as error:
            raise error

if __name__ == "__main__":
    main()
