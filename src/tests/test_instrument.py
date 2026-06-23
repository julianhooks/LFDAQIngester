"""

"""
import logging
import os
import unittest

import psycopg as pg

from tests.test_questdb_handle import QuestDBHandleTestFixture

from lfdaq_ingester.instrument import Instrument, InstrumentCreator

logger = logging.getLogger(__name__)


class InstrumentTestFixture(QuestDBHandleTestFixture):
    """

    """
    test_instrument = Instrument(
        "TEST",
        "Testing",
        lambda x: x,
        True,
        "Count",
        True,
        "AIN0"
    )

    def populate_questdb(self):
        """
        Set up instrument table and test insturment in database

        When an instrument loading util is developed,
        most of the below code should be replaced with
        calls to that module
        """
        # We need an active questdb container to procede
        if self.questdb_instance is None:
            raise AttributeError(self.questdb_instance, self)

        # Should add test data for a bad instrument to check error handling

        with pg.connect(
                host=os.getenv("LFDAQ_DB_URL"),
                port=int(os.getenv("LFDAQ_DB_PG_PORT")),
                user=os.getenv("LFDAQ_DB_USERNAME"),
                password=os.getenv("LFDAQ_DB_PASSWORD"),
                dbname=os.getenv("LFDAQ_DB_NAME"),
                autocommit=True
                ) as connector:
            # Create instrument table and add test data
            with connector.cursor(binary=True) as cursor:
                cursor.execute(
                    """
                    CREATE TABLE Instruments (
                      "InstrumentID" SYMBOL,
                      "InstrumentName" VARCHAR,
                      "CalibrationFunction" VARCHAR,
                      "Unit" VARCHAR,
                      "IsActive" BOOLEAN,
                      "IsLabJack" BOOLEAN,
                      "LabJackPort" VARCHAR
                    )
                    """
                    )
                cursor.execute(
                    """
                    INSERT INTO Instruments (
                      InstrumentID,
                      InstrumentName,
                      CalibrationFunction,
                      Unit,
                      IsActive,
                      IsLabJack,
                      LabJackPort )
                    VALUES (
                      %s,
                      %s,
                      %s,
                      %s,
                      %s,
                      %s,
                      %s )
                    """,
                    [self.test_instrument.InstrumentID,
                     self.test_instrument.InstrumentName,
                     "lambda x: x",
                     self.test_instrument.Unit,
                     self.test_instrument.IsActive,
                     self.test_instrument.IsLabJack,
                     self.test_instrument.LabJackPort])

    def setUp(self) -> None:
        super().setUp()
        self.populate_questdb()

    def runTest(self) -> None:
        instrumentList = InstrumentCreator().get_instruments()
        self.assertEqual(instrumentList[0].InstrumentID,
                         self.test_instrument.InstrumentID)
        self.assertEqual(instrumentList[0].InstrumentName,
                         self.test_instrument.InstrumentName)
        self.assertEqual(instrumentList[0].Unit,
                         self.test_instrument.Unit)
        self.assertEqual(instrumentList[0].IsActive,
                         self.test_instrument.IsActive)
        self.assertEqual(instrumentList[0].IsLabJack,
                         self.test_instrument.IsLabJack)
        self.assertEqual(instrumentList[0].LabJackPort,
                         self.test_instrument.LabJackPort)
        self.assertEqual(instrumentList[0].CalibrationFunction(1),
                         self.test_instrument.CalibrationFunction(1))

    def tearDown(self) -> None:
        super().tearDown()


if (__name__ == "__main__"):
    unittest.main()
