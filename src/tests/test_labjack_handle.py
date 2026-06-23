"""

"""
import logging
import os
import unittest
import unittest.mock

from labjack import ljm

from lfdaq_ingester.labjack_handle import LabJackHandle

logger = logging.getLogger(__name__)


class LabJackTestFixture(unittest.TestCase):
    """

    """
    ljm_type_conversions = {
            ljm.constants.UINT16: int,
            ljm.constants.UINT32: int,
            ljm.constants.INT32: int,
            ljm.constants.FLOAT32: float,
            ljm.constants.BYTE: bytes,
            ljm.constants.STRING: str
        }

    def create_labjack_mockup(self):
        """
        Set up mock labjack functions
        """
        os.environ["LFDAQ_DB_LOOP_DELAY_MS"] = "1000"

        self.mock_labjack = unittest.mock.create_autospec(LabJackHandle)
        # Check different edge case numbers
        # (Vmin, Vmax, UINT16 max, INT32 min/max, and UINT32 max)
        self.mock_labjack.get_value.return_value = [1, 0, -1,
                                                    10, -10,
                                                    65536,
                                                    2147483647, -2147483648,
                                                    4294967296]

    def destroy_labjack_mockup(self):
        os.environ.pop("LFDAQ_DB_LOOP_DELAY_MS")

    def verify_labjack_type(self, name, value):
        """
        Check that the input type to a set_value call
        is type correct with the output call
        """
        address = ljm.nameToAddress(name)
        address_type_constant = ljm.addressToType(address)
        address_type = self.ljm_type_conversions[address_type_constant]
        assert type(value) is address_type

    def setUp(self) -> None:
        self.create_labjack_mockup()

    def runTest(self):
        try:
            handle = LabJackHandle()
        except ljm.LJMError as error:
            self.assertEqual(error.errorCode, 1227)
            handle = self.mock_labjack
            pass

    def tearDown(self) -> None:
        self.destroy_labjack_mockup()


if (__name__ == "__main__"):
    unittest.main()
