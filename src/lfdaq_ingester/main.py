import logging
import os

# Import necessary functions
from questdb_handle import getQuestDBHandle
from ingester import setup, ingestLoop, onExit
from labjack_handle import getLabJack
from instrument import getInstruments

# Start logger
logger = logging.getLogger(__name__)

logFormatter = logging.Formatter('%(asctime)s   :%(levelname)s:%(name)s: %(message)s')

logFile = logging.FileHandler(f'{__name__}.log')
logFile.setLevel(logging.DEBUG)
logFile.setFormatter(logFormatter)
logger.addHandler(logFile)

logStream = logging.StreamHandler()
logStream.setLevel(logging.DEBUG)
logStream.setFormatter(logFormatter)
logger.addHandler(logStream)

logger.info("Started Logging")
    
def main() -> None:
    
    instruments = getInstruments()
    labJackHandle = getLabJack()
    
    setup(labJackHandle)

    with getQuestDBHandle() as questDBHandle:
        try:
            while(True):
                ingestLoop(instruments,labJackHandle,questDBHandle)
        finally:
            onExit(labJackHandle)
    return

if (__name__ == "__main__"):
    main()

