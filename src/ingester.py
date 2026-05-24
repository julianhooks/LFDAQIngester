import logging
import os
import unittest
from time import sleep
from typing import Annotated, Any

from labjack import ljm
import questdb.ingress

from instrument import Instrument

logger = logging.getLogger(__name__)

def setup(labJackHandle: Annotated[int,"LabJack connection handle."]) -> None:
    # [IN-PROGRESS] set up counters 1 and 2 for flowmeters
    ljm.eWriteName(labJackHandle,"DIO0_EF_ENABLE",0)
    ljm.eWriteName(labJackHandle,"DIO0_EF_INDEX",8)
    ljm.eWriteName(labJackHandle,"DIO0_EF_ENABLE",1)
    logger.info("Enabled timer 0")
    
    ljm.eWriteName(labJackHandle,"DIO1_EF_ENABLE",0)
    ljm.eWriteName(labJackHandle,"DIO1_EF_INDEX",8)
    ljm.eWriteName(labJackHandle,"DIO1_EF_ENABLE",1)
    logger.info("Enabled timer 1")

    # enable below and jump DAC1 to DIO0 to test counter
    # ljm.eWriteName(labJackHandle,"DAC1_FREQUENCY_OUT_ENABLE",1)

# Perform data ingestion:
# - Get voltages of each active instrument
# - Run calibration function on voltage
# - Write (time,voltage,value) to each instrument table
# - Repeat until close
def ingestLoop(instruments: list[Instrument],
               labJackHandle: Annotated[int,"LabJack connection handle."],
               questDBHandle: questdb.ingress.Sender) -> None:

    loopDelayms = int(os.getenv("LFDAQ_DB_LOOP_DELAY_MS"))
    
    for instrument in instruments:
        uncalibratedValue = ljm.eReadName(labJackHandle, instrument.LabJackPort)
        calibratedValue = instrument.CalibrationFunction(uncalibratedValue)
        questDBHandle.row(
                'InstrumentValues',
                symbols={'InstrumentID': instrument.InstrumentID},
                columns={'UncalibratedValue': uncalibratedValue,
                         'CalibratedValue': calibratedValue},
                at=questdb.ingress.TimestampNanos.now())
    sleep(loopDelayms/1000.0)

# [IN-PROGRESS] Exit cleanly on error (+ give me logs of what's going on) 
def onExit(labjackHandle: Annotated[int,"LabJack connection handle."]) -> None:
    try:
        ljm.close(labjackHandle)
        logger.info("Closed QuestDB, closed LabJack")
    except ljm.LJMError as error:
        logger.error(f"Error occured when disconnecting from LabJack: {error}.")
        raise error

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
        instruments = [Instrument(

        )]

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