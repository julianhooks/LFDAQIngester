"""
instrument docstring
"""
import logging
from dataclasses import dataclass
import os
from typing import Annotated

import psycopg as pg

logger = logging.getLogger(__name__)

@dataclass
class Instrument:
    """
    dataclass docstring

    member variables break naming convention to align with the SQL column names.
    """
    InstrumentID: Annotated[str,"QuestDB Symbol"]
    InstrumentName: str
    CalibrationFunction: Annotated[callable,"With functions included from calibration.py"]
    IsActive: bool
    Unit: str
    IsLabJack: bool
    LabJackPort: Annotated[str,"LabJack connection handle."]

class InstrumentCreator:
    """
    instrument factory docstring
    """
    def get_instruments(self) -> list[Instrument]:
        """
        get instruments docstring
        """
        instruments = []
        function_namespace = {}
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
                instrument_table = cursor.fetchall()
                for row in instrument_table:
                    if (bool(row["IsLabJack"]) is False or bool(row["IsActive"]) is False):
                        continue
                    exec("cf = "+ row["CalibrationFunction"],function_namespace)
                    instruments.append(
                            Instrument(
                                row["InstrumentID"],
                                row["InstrumentName"],
                                function_namespace["cf"],
                                bool(row["IsActive"]),
                                row["Unit"],
                                bool(row["IsLabJack"]),
                                row["LabJackPort"]))
        return instruments
