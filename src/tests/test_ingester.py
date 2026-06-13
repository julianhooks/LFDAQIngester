import logging
import os
import unittest
from time import sleep
from typing import Annotated, Any

from labjack import ljm
import questdb.ingress

from lfdaq_ingester.instrument import Instrument
from lfdaq_ingester.ingester import *

logger = logging.getLogger(__name__)

class ingesterTest(unittest.TestCase):

    def runTest(self):
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
        
        # Set relevant environment variable

        # Set up instrument list
        instruments = []

        # Set up false labjack functions

        def falseEReadName(handle: Any,name: Any) -> float:
            # Do nothing here or check inputs
            return
        
        ljm.eReadName = falseEReadName

        # Set up false Sender object

        class FalseSender(questdb.ingress.Sender):
            
            def row(
                    table_name: str,
                    *,
                    symbols: dict[str, str] | None = None,
                    columns: dict[str, Any] | None = None,
                    at) -> questdb.ingress.Sender:
                # Do nothing here or check inputs
                return self

        dbHandle = FalseSender() 
        
        # Run test
        try:
            ingestLoop()
        except Exception as e:
            pass 
        
        # Teardown as necessary

        return


if (__name__ == "__main__"):
    unittest.main()
