import logging
import unittest
from typing import Annotated

from labjack import ljm

logger = logging.getLogger(__name__)

def getLabJack() -> Annotated[int,"LabJack connection handle."]:
    try:
        labjackHandle = ljm.openS("T7","ANY","ANY")
    except ljm.LJMError as error:
        logger.error(f"Error occured when connecting to LabJack: {error}.")
        raise error
    logger.info(f"Connected to LabJack on {ljm.getHandleInfo(labjackHandle)}.")
    return labjackHandle

class LabJackTests(unittest.TestCase):
    
    def runTest(self):
        try:
            handle = getLabJack()
            self.assertIsNotNone(handle)
        except ljm.LJMError as error:
            self.assertEqual(error.errorCode,1227)
            pass

if (__name__ == "__main__"):
    unittest.main()