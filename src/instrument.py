import logging
from dataclasses import dataclass
import os
from typing import Annotated

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
    # Connect to QuestDB for queries
    
    instruments = []
    functionNamespace = {}

    # [TO-DO] make these setups parameters .env variables 
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
           
            # Pull all instruments (labjack port + calibration eq + database stuff) from database
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