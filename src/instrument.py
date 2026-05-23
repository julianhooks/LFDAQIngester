import logging
from dataclasses import dataclass
import os
from typing import Annotated
import unittest
import docker
import time

import psycopg as pg

logger = logging.getLogger(__name__)

@dataclass
class Instrument:
    InstrumentID: Annotated[str,"QuestDB Symbol"]
    InstrumentName: str
    CalibrationFunction: Annotated[callable,"With functions included from calibration.py"]
    IsActive: bool
    Unit: str
    IsLabJack: bool
    LabJackPort: Annotated[str,"LabJack connection handle."]

def getInstruments() -> list[Instrument]:
    instruments = []
    functionNamespace = {}

    with pg.connect(
            host=os.getenv("LFDAQ_DB_URL"),
            port=int(os.getenv("LFDAQ_DB_PG_PORT")), 
            user=os.getenv("LFDAQ_DB_USERNAME"), 
            password=os.getenv("LFDAQ_DB_PASSWORD"),
            dbname=os.getenv("LFDAQ_DB_NAME"), 
            autocommit=True
            ) as connector:
        with connector.cursor(
            binary=True, 
            row_factory=pg.rows.dict_row
            ) as cursor:
            cursor.execute("SELECT version")
            version = cursor.fetchone()
            logger.info(f'Connected to QuestDB version: {version["version"]}')
           
            cursor.execute("SELECT * FROM Instruments")
            instrumentTable = cursor.fetchall()
          
            for row in instrumentTable:
                if (bool(row["IsLabJack"]) == False or bool(row["IsActive"]) == False):
                    continue
                exec("cf = "+ row["CalibrationFunction"],functionNamespace)
                instruments.append(
                        Instrument(
                            row["InstrumentID"],
                            row["InstrumentName"],
                            functionNamespace["cf"],
                            bool(row["IsActive"]),
                            row["Unit"],
                            bool(row["IsLabJack"]),
                            row["LabJackPort"]))
    return instruments

class InstrumentTests(unittest.TestCase):
    
    def runTest(self):
        # Set relevant environment variables for test
        os.environ["LFDAQ_DB_URL"] = "127.0.0.1"
        os.environ["LFDAQ_DB_PG_PORT"] = "8812"
        os.environ["LFDAQ_DB_INFLUX_PORT"] = "9000"
        os.environ["LFDAQ_DB_USERNAME"] = "admin"
        os.environ["LFDAQ_DB_PASSWORD"] = "quest"
        os.environ["LFDAQ_DB_NAME"] = ""
        
        # Start test database
        dockerClient = docker.from_env()
        questDBInstance = dockerClient.containers.run("questdb/questdb", 
                                                      detach = True, 
                                                      ports={9000:9000,
                                                             9009:9009,
                                                             8812:8812,
                                                             9003:9003})

        # Give the container some time to set up before we test
        time.sleep(10)
        
        # Add test data for good instrument
        testInstrument = Instrument(
            "TEST",
            "Testing",
            lambda x: x,
            True,
            "Count",
            True,
            "AIN0"
        )

        # Should add test data for a not-good instrument
        
        try:
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
                        [testInstrument.InstrumentID,
                         testInstrument.InstrumentName,
                         "lambda x: x",
                         testInstrument.Unit,
                         testInstrument.IsActive,
                         testInstrument.IsLabJack,
                         testInstrument.LabJackPort])

                instrumentList = getInstruments()
                # These tests don't work but the above process does
                self.assertIsNotNone(instrumentList)
                self.assertEqual(instrumentList[0],testInstrument)
                # This is failing because the two lambda functions are in different namespaces
            
        finally:
            os.environ.pop("LFDAQ_DB_URL")
            os.environ.pop("LFDAQ_DB_INFLUX_PORT")
            os.environ.pop("LFDAQ_DB_PG_PORT")
            os.environ.pop("LFDAQ_DB_USERNAME")
            os.environ.pop("LFDAQ_DB_PASSWORD")
            os.environ.pop("LFDAQ_DB_NAME")
            
            questDBInstance.stop()

        return
    
if (__name__ == "__main__"):
    unittest.main()