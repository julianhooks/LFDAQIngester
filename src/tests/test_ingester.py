"""

"""
import logging
import os
import unittest

from labjack import ljm

from tests.test_instrument import InstrumentTestFixture
from tests.test_labjack_handle import LabJackTestFixture

from lfdaq_ingester.ingester import Ingester

logger = logging.getLogger(__name__)


@unittest.mock.patch("lfdaq_ingester.labjack_handle.LabJackHandle", autospec=True)
class ingesterTest(InstrumentTestFixture, LabJackTestFixture):

    def setUp(self):
        self.create_questdb_container()
        self.populate_questdb()
        os.environ["LFDAQ_DB_LOOP_DELAY_MS"] = "1000"

    def test_init(self, MockLabJackHandle):
        try:
            self.ingester = Ingester()
        except ljm.LJMError as error:
            self.assertEqual(error.errorCode, 1227)
            self.ingester = Ingester(labjack_handle=MockLabJackHandle)
        finally:
            self.ingester.labjack_handle.set_value.assert_called()

    def test_loop(self):
        pass

    def runTest(self):
        # Run test
        # setup() is not accessing false register names
        # - ljm.nameToAddress should return an error if name does not exist
        #   - Raises error 1294 on bad name
        # - ljm.addressToType could also be used to check inputs
        #   - This returns a number corresponding to an LJM type constant
        # - ljm.errorToString might also be useful in the future

        # Loop is calling calibration functions properly
        # Loop is calling eReadVoltages properly
        # Loop is writing to db properly
        # Loop is waiting properly

        # Set up ingester for testing
        self.test_init()

    def tearDown(self):
        self.remove_questdb_container()
        os.environ.pop("LFDAQ_DB_LOOP_DELAY_MS")


if (__name__ == "__main__"):
    unittest.main()
