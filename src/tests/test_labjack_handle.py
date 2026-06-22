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

class LabJackTestFixture(unittest.TestCase):
    """

    """
    ljm_type_conversions = {
            ljm.constants.UINT16 : int,
            ljm.constants.UINT32 : int,
            ljm.constants.INT32 : int,
            ljm.constants.FLOAT32 : float,
            ljm.constants.BYTE : bytes,
            ljm.constants.STRING : str
        }

    def create_labjack_mockup(self):
        """
        Set up mock labjack functions
        """
        self.mock_labjack = unittest.mock.create_autospec(LabJackHandle)
        self.mock_labjack.get_value.return_value = 0
        # Check name called with is a valid name, if name is incorrect then raise correct error (LJM 1294)
        self.mock_labjack.get_value.side_effect = ljm.nameToAddress(self.mock_labjack.call_args.args[0])

    def check_labjack_set_value(name, value):
        """
        Check that the input type to a set_value call is type correct with the output call
        """
        address = ljm.nameToAddress(name)
        address_type_constant = ljm.addressToType(address)
        address_type = self.ljm_type_conversions[address_type_constant]
        assert type(value) is address_type
    
    def runTest(self):
        try:
            handle = getLabJack()
            self.assertIsNotNone(handle)
        except ljm.LJMError as error:
            self.assertEqual(error.errorCode,1227)
            pass

if (__name__ == "__main__"):
    unittest.main()
