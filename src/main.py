import logging
from dataclasses import dataclass
import os
from time import sleep
from typing import Annotated

from labjack import ljm
import questdb.ingress
import psycopg as pg

# Start logger
# [TO-DO] set up better logger config
logger = logging.getLogger(__name__)

logFormatter = logging.Formatter('%(asctime)s   :%(levelname)s:%(name)s: %(message)s')

logFile = logging.FileHandler(f'{__name__}.log')
logFile.setLevel(logging.DEBUG)
logFile.setFormatter(logFormatter)
logger.addHandler(logFile)

logStream = logging.StreamHandler()
logStream.setLevel(logging.DEBUG)
logStream.setFormatter(logFormatter)
logger.addHandler(logStream)

logger.info("Started Logging")

# Get environment variables
loopDelayms = int(os.getenv("LFDAQ_DB_LOOP_DELAY_MS"))
    
@dataclass
class Instrument:
    InstrumentID: Annotated[str,"QuestDB Symbol"]
    InstrumentName: str
    CalibrationFunction: Annotated[callable,"With functions included from calibration.py"]
    IsActive: bool
    Unit: str
    IsLabJack: bool
    LabJackPort: Annotated[str,"LabJack connection handle."]

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

def getLabJack() -> Annotated[int,"LabJack connection handle."]:
    try:
        labjackHandle = ljm.openS("T7","ANY","ANY")
    except ljm.LJMError as error:
        logger.error(f"Error occured when connecting to LabJack: {error}.")
        raise error
    logger.info(f"Connected to LabJack on {ljm.getHandleInfo(labjackHandle)}.")
    return labjackHandle

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

# [DONE] connect to QuestDB for sending
def getQuestDBHandle() -> questdb.ingress.Sender:
    # we do want to use http here, not tcp, because more functionality is available for http
    # this uses the influx line protocol, not postgres
    
    # [TO-DO] make these environment variables
    try:
        questDBHandle = questdb.ingress.Sender(
            questdb.ingress.Protocol.Http, 
            os.getenv("LFDAQ_DB_URL"), 
            int(os.getenv("LFDAQ_DB_INFLUX_PORT")), 
            username=os.getenv("LFDAQ_DB_USERNAME"), 
            password=os.getenv("LFDAQ_DB_PASSWORD"))
        logger.info(f"Connected to QuestDB influx port")
    except questdb.ingress.IngressError as error:
        logger.error(f"Error occured when connecting to questDB: {error}.")
        raise error
    
    # [IN-PROGRESS] set up auto-flushing settings for this handle
    questDBHandle.auto_flush = True
    questDBHandle.auto_flush_interval = int(os.getenv("LFDAQ_DB_AUTOFLUSH_INTERVAL_MS")) 
    questDBHandle.auto_flush_rows = int(os.getenv("LFDAQ_DB_AUTOFLUSH_ROWS")) 

    return questDBHandle

# [DONE] Perform data ingestion:
# - Get voltages of each active instrument
# - Run calibration function on voltage
# - Write (time,voltage,value) to each instrument table
# - Repeat until close
def ingestLoop(instruments: list[Instrument],
               labJackHandle: Annotated[int,"LabJack connection handle."],
               questDBHandle: questdb.ingress.Sender) -> None:

    for instrument in instruments:
        uncalibratedValue = ljm.eReadName(labJackHandle, instrument.LabJackPort)
        calibratedValue = instrument.CalibrationFunction(uncalibratedValue)
        questDBHandle.row(
                'InstrumentValues',
                symbols={'InstrumentID': instrument.InstrumentID},
                columns={
                    'UncalibratedValue': uncalibratedValue,
                    'CalibratedValue': calibratedValue},
                at=questdb.ingress.TimestampNanos.now())
    sleep(loopDelayms/1000.0)

# [IN-PROGRESS] Exit cleanly on error (+ give me logs of what's going on) 
def onexit(labjackHandle: Annotated[int,"LabJack connection handle."]) -> None:
    try:
        ljm.close(labjackHandle)
        logger.info("Closed QuestDB, closed LabJack")
    except ljm.LJMError as error:
        logger.error(f"Error occured when disconnecting from LabJack: {error}.")
        raise error

def main() -> None:
    
    instruments = getInstruments()
    labJackHandle = getLabJack()
    
    setup(labJackHandle)

    with getQuestDBHandle() as questDBHandle:
        try:
            while(True):
                ingestLoop(instruments,labJackHandle,questDBHandle)
        finally:
            onexit(labJackHandle)
    return

if (__name__ == "__main__"):
    main()

