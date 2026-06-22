import logging
import os
import time
import unittest

from dataclasses import dataclass
from typing import Annotated

import docker
import psycopg as pg

from tests.test_questdb_handle import QuestDBHandleTestFixture

from lfdaq_ingester.instrument import *

logger = logging.getLogger(__name__)

class InstrumentTestFixture(unittest.TestCase):
    """

    """
    def populate_questdb(self):
        """
        Set up instrument table and test insturment in database

        When an instrument loading util is developed, 
        most of the below code should be replaced with 
        calls to that module
        """
        # We need an active questdb container to procede
        if self.questdb_instance is None:
            raise AttributeError(questdb_instance,self) 

        test_instrument = Instrument(
            "TEST",
            "Testing",
            lambda x: x,
            True,
            "Count",
            True,
            "AIN0"
        )
        # Should add test data for a not-good instruments to check error handling
        
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
                    """)
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
                    [test_instrument.InstrumentID,
                     test_instrument.InstrumentName,
                     "lambda x: x",
                     test_instrument.Unit,
                     test_instrument.IsActive,
                     test_instrument.IsLabJack,
                     test_instrument.LabJackPort])

    def setUp(self) -> None:
        super().setUp()
        self.populate_questdb()

    def runTest(self) -> None:
        instrumentList = getInstruments()
        self.assertEqual(instrumentList[0].InstrumentID,testInstrument.InstrumentID)
        self.assertEqual(instrumentList[0].InstrumentName,testInstrument.InstrumentName)
        self.assertEqual(instrumentList[0].Unit,testInstrument.Unit)
        self.assertEqual(instrumentList[0].IsActive,testInstrument.IsActive)
        self.assertEqual(instrumentList[0].IsLabJack,testInstrument.IsLabJack)
        self.assertEqual(instrumentList[0].LabJackPort,testInstrument.LabJackPort)
        self.assertEqual(instrumentList[0].CalibrationFunction(1),testInstrument.CalibrationFunction(1))

    def tearDown(self) -> None:
        super().tearDown()
    
if (__name__ == "__main__"):
    unittest.main()
