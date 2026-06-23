import logging
import unittest

from lfdaq_ingester.ingester import Ingester

logger = logging.getLogger(__name__)


class ingesterTest(unittest.TestCase):

    def setUp(self):
        # Creates questdb instance for test
        super().setUp()

    def runTest(self):
        # Run test
        # setup() is not accessing false register names
        # - ljm.nameToAddress should return an error if name does not exist
        #   - Raises error 1294 on bad name
        # - ljm.addressToType could also be used to check inputs
        #   - This returns a number corresponding to an LJM constant for the ctype
        # - ljm.errorToString might also be useful in the future

        # Loop is calling calibration functions properly
        # Loop is calling eReadVoltages properly
        # Loop is writing to db properly
        # Loop is waiting properly

        # Set up ingester for testing
        self.ingester = Ingester()

        try:
            self.ingester.questdb_handle.establish()
        except Exception as error:
            raise error
        finally:
            self.ingester.exit()

    def tearDown(self):
        super().tearDown()


if (__name__ == "__main__"):
    unittest.main()
