"""
Wrapper class for ljm.labjack functions and set up.
"""
import logging

from labjack import ljm

logger = logging.getLogger(__name__)

class LabJackHandle:
    """
    wraps ljm.labjack functions and set up for a T7 pro
    """
    def __init__(self):
        """
        func
        """
        try:
            self.handle = ljm.openS("T7","ANY","ANY")
        except ljm.LJMError as error:
            logger.error(f"Error occured when connecting to LabJack: {error}.")
            raise error
        logger.info(f"Connected to LabJack on {ljm.getHandleInfo(self.handle)}.")

    def get_info(self):
        """
        func
        """
        ljm.getHandleInfo(self.handle)

    def set_value(self,name: str,value):
        """
        func
        """
        ljm.eWriteName(self.handle, name, value)

    def get_value(self,name):
        """
        func
        """
        return ljm.eReadName(self,name)

    def close(self):
        """
        func
        """
        ljm.close(self.handle)

    def __exit__(self, *exc_details):
        """
        func
        """
        self.close()
