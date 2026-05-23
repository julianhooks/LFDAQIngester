import logging
import os
import unittest
from time import sleep
from typing import Annotated

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
        # loop is calling calibration functions properly
        # loop is calling ereadvoltages properly
        # loop is writing to db properly
        # loop is waiting properly
        return


if (__name__ == "__main__"):
    unittest.main()