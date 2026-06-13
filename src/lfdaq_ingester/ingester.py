import logging
import os
import unittest
from time import sleep
from typing import Annotated, Any

from labjack import ljm
import questdb.ingress

from lfdaq_ingester.instrument import Instrument
from lfdaq_ingester.instrument import InstrumentListGenerator
from lfdaq_ingester.labjack_handle import LabJackHandle

logger = logging.getLogger(__name__)

class Ingester:
    def __init__(self):
        self.labjack_handle = LabJackHandle() 
        self.questdb_handle = None
        self.instruments = InstrumentListGenerator()
        self.setup()

    def setup(self):
        self.loopDelayms = int(os.getenv("LFDAQ_DB_LOOP_DELAY_MS"))

        # [IN-PROGRESS] set up counters 1 and 2 for flowmeters
        self.labjack_handle.set_value("DIO0_EF_ENABLE",0)
        self.labjack_handle.set_value("DIO0_EF_INDEX",8)
        self.labjack_handle.set_value("DIO0_EF_ENABLE",1)
        logger.info("Enabled timer 0")
        
        self.labjack_handle.set_value("DIO1_EF_ENABLE",0)
        self.labjack_handle.set_value("DIO1_EF_INDEX",8)
        self.labjack_handle.set_value("DIO1_EF_ENABLE",1)
        logger.info("Enabled timer 1")

        # enable below and jump DAC1 to DIO0 to test counter
        # self.labjack_handle.set_value("DAC1_FREQUENCY_OUT_ENABLE",1)

    def loop(self) -> None:
        while True:
            for instrument in self.instruments:
                uncalibratedValue = self.labjack_handle.get_value(instrument.LabJackPort)
                calibratedValue = instrument.CalibrationFunction(uncalibratedValue)
                self.questdb_handle.row(
                        'InstrumentValues',
                        symbols={'InstrumentID': instrument.InstrumentID},
                        columns={'UncalibratedValue': uncalibratedValue,
                                 'CalibratedValue': calibratedValue},
                        at=questdb.ingress.TimestampNanos.now())
            sleep(self.loopDelayms/1000.0)

    def exit(self) -> None:
        try:
            self.labjack_handle.close()    
            logger.info("Closed QuestDB, closed LabJack")
        except ljm.LJMError as error:
            logger.error(f"Error occured when disconnecting from LabJack: {error}.")
            raise error

    def __enter__(self):
        pass 
    
    def __exit__(self, *exc_details):
        self.exit()

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
