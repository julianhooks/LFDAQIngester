"""
Holds the Ingester class, responsible for primary data collection loop.
"""
import logging
import os
from time import sleep

from labjack import ljm
import questdb.ingress

from lfdaq_ingester.instrument import InstrumentCreator
from lfdaq_ingester.labjack_handle import LabJackHandle
from lfdaq_ingester.questdb_handle import QuestDBHandle

logger = logging.getLogger(__name__)


class Ingester:
    """
    Handles connecting to QuestDB and the LabJack,
    running the primary read-write loop, and cleaning up.
    """

    def __init__(self, labjack_handle=None):
        """
        Initializes an Ingester object.
        Connects to a LabJack T7 and a QuestDB database.
        Once connected, run labjack setup.
        """
        try:
            self.instruments = InstrumentCreator().get_instruments()
        except Exception as error:
            raise error
        try:
            self.questdb_handle = QuestDBHandle()
        except Exception as error:
            raise error
        if labjack_handle is not None:
            self.labjack_handle = labjack_handle
        else:
            try:
                self.labjack_handle = LabJackHandle()
            except Exception as error:
                raise error
        self.setup()

    def __enter__(self):
        """
        Automatically connects to the QuetsDB influx port
        """
        try:
            self.questdb_handle.establish()
        except Exception as error:
            raise error

    def setup(self):
        """
        Get loop delay and set up labjack hardware counters
        """
        self.loop_delay_ms = int(os.getenv("LFDAQ_DB_LOOP_DELAY_MS"))

        # [IN-PROGRESS] set up counters 1 and 2 for flowmeters
        self.labjack_handle.set_value("DIO0_EF_ENABLE", 0)
        self.labjack_handle.set_value("DIO0_EF_INDEX", 8)
        self.labjack_handle.set_value("DIO0_EF_ENABLE", 1)
        logger.info("Enabled timer 0")

        self.labjack_handle.set_value("DIO1_EF_ENABLE", 0)
        self.labjack_handle.set_value("DIO1_EF_INDEX", 8)
        self.labjack_handle.set_value("DIO1_EF_ENABLE", 1)
        logger.info("Enabled timer 1")

        # enable below and jump DAC1 to DIO0 to test counter
        # self.labjack_handle.set_value("DAC1_FREQUENCY_OUT_ENABLE",1)

    def loop(self) -> None:
        """
        Runs the data collections, calibration, and writing loop.
        """
        while True:
            for instrument in self.instruments:
                uncalibrated_value = self.labjack_handle.get_value(instrument.LabJackPort)
                calibrated_value = instrument.CalibrationFunction(uncalibrated_value)
                self.questdb_handle.row(
                        'InstrumentValues',
                        symbols={'InstrumentID': instrument.InstrumentID},
                        columns={'Uncalibrated_value': uncalibrated_value,
                                 'CalibratedValue': calibrated_value},
                        at=questdb.ingress.TimestampNanos.now())
            sleep(self.loop_delay_ms/1000.0)

    def exit(self) -> None:
        """
        Close the influx port and close the labjack handle.
        """
        try:
            self.questdb_handle.close()
            self.labjack_handle.close()
            logger.info("Closed QuestDB, closed LabJack")
        except ljm.LJMError as error:
            logger.error(f"Error occured when disconnecting from LabJack: {error}.")
            raise error

    def __exit__(self, *exc_details):
        """
        Make sure things close when using in a with block.
        """
        self.exit()
