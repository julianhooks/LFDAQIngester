import logging
import unittest
from typing import Annotated

from labjack import ljm

logger = logging.getLogger(__name__)

class LabJackHandle:
    def __init__(self):
        try:
            self.handle = ljm.openS("T7","ANY","ANY")
        except ljm.LJMError as error:
            logger.error(f"Error occured when connecting to LabJack: {error}.")
            raise error
        logger.info(f"Connected to LabJack on {ljm.getHandleInfo(self.handle)}.")
        return self.handle
    
    def get_info(self):
        ljm.getHandleInfo(self.handle)

    def set_value(self,name: str,value):
        ljm.eWriteName(self.handle, name, value)

    def get_value(self,name):
        return ljm.eReadName(self,name)

    def close(self):
        ljm.close(self.handle)

    def __exit__(self):
        self.close()

def getLabJack() -> Annotated[int,"LabJack connection handle."]:
    try:
        labjackHandle = ljm.openS("T7","ANY","ANY")
    except ljm.LJMError as error:
        logger.error(f"Error occured when connecting to LabJack: {error}.")
        raise error
    logger.info(f"Connected to LabJack on {ljm.getHandleInfo(labjackHandle)}.")
    return labjackHandle
