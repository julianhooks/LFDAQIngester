import logging
import os
import unittest

from time import sleep
from typing import Annotated, Any

from labjack import ljm

import questdb.ingress

from lfdaq_ingester.ingester import Ingester
from utils import LFDAQTestFixture

logger = logging.getLogger(__name__)

class ingesterTest(LFDAQTestFixture):
    def setUp(self):
        # Creates questdb instance for test
        super().setUp()
        # Set up ingester for testing
        self.ingester = Ingester()
        # Set up instrument lists for querying

        # Set up mock labjack functions

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

        try:
            self.ingester.questdb_handle.establish() 
        except Exception as error:
            raise error 


    def tearDown(self):
        self.ingester.exit() 
        super().tearDown()


if (__name__ == "__main__"):
    unittest.main()
