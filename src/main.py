"""
Contains logger set up and main loop code.
"""
import logging

# Import necessary functions
from lfdaq_ingester.questdb_handle import getQuestDBHandle
from lfdaq_ingester.ingester import setup, ingestLoop, onExit
from lfdaq_ingester.labjack_handle import getLabJack
from lfdaq_ingester.instrument import getInstruments

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
    instruments = getInstruments()
    lj_handle = getLabJack()
    setup(lj_handle)
    with getQuestDBHandle() as db_handle:
        try:
            while True:
                ingestLoop(instruments,lj_handle,db_handle)
        finally:
            onExit(lj_handle)

if __name__ == "__main__":
    main()
