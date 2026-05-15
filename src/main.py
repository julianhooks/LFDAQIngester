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
logging.basicConfig(level=logging.DEBUG)
logger.info("Started Logging")

# Get environment variables
dburl=os.getenv("DBURL")
labjackURL='jackjack.lan'
loopDelayms =int(os.getenv("LOOPDELAY"))
    
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
    
    ljm.eWriteName(labJackHandle,"DIO1_EF_ENABLE",0)
    ljm.eWriteName(labJackHandle,"DIO1_EF_INDEX",8)
    ljm.eWriteName(labJackHandle,"DIO1_EF_ENABLE",1)

    # enable below and jump DAC1 to DIO0 to test counter
    # ljm.eWriteName(labJackHandle,"DAC1_FREQUENCY_OUT_ENABLE",1)

def getLabJack(labjackURL: Annotated[str,"URL"]) -> Annotated[int,"LabJack connection handle."]:
    try:
        labjackHandle = ljm.openS("T7","ANY","ANY")
    except ljm.LJMError as error:
        logging.error(f"Error occured when connecting to LabJack: {error}.")
        raise error
    logging.info(f"Connected to LabJack on {ljm.getHandleInfo(labjackHandle)}.")
    return labjackHandle

def getInstruments(dbURL: Annotated[str,"URL"]) -> list[Instrument]:
    # Connect to QuestDB for queries
    
    instruments = []
    functionNamespace = {}

    # [TO-DO] make these env variables 
    with pg.connect(
            host=dbURL,
            port=8812, 
            user='admin', 
            password='quest',
            dbname='LiquidsTestStand', 
            autocommit=True
            ) as connector:
        with connector.cursor(
            binary=True, 
            row_factory=pg.rows.dict_row
            ) as cursor:
            cursor.execute("SELECT version")
            version = cursor.fetchone()
            logging.info(f'Connected to QuestDB version: {version["version"]}')
           
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
def getQuestDBHandle(dbURL: Annotated[str,"URL"]) -> questdb.ingress.Sender:
    # we do want to use http here, not tcp, because more functionality is available for http
    # this uses the influx line protocol, not postgres
    
    # [TO-DO] make these environment variables
    try:
        questDBHandle = questdb.ingress.Sender(
            questdb.ingress.Protocol.Http, 
            dbURL, 
            9000, 
            username='admin', 
            password='quest')
        logging.info(f"Connected to QuestDB influx port")
    except questdb.ingress.IngressError as error:
        logging.error(f"Error occured when connecting to questDB: {error}.")
        raise error
    
    # [TO-DO] set up auto-flushing settings for this handle

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
    questDBHandle.flush()
    sleep(loopDelayms/1000.0)

# [IN-PROGRESS] Exit cleanly on error (+ give me logs of what's going on) 
def onexit(labjackHandle: Annotated[int,"LabJack connection handle."], questDBHandle: questdb.ingress.Sender) -> None:
    try:
        ljm.close(labjackHandle)
        logging.info("Closed QuestDB, closed LabJack")
    except ljm.LJMError as error:
        logging.error(f"Error occured when disconnecting from LabJack: {error}.")
        raise error

def main() -> None:
    
    labJackHandle = getLabJack(labjackURL)
    instruments = getInstruments(dburl)
    
    setup(labJackHandle)

    with getQuestDBHandle(dburl) as questDBHandle:
        try:
            while(True):
                ingestLoop(instruments,labJackHandle,questDBHandle)
        finally:
            onexit(labJackHandle,questDBHandle)
    return

if (__name__ == "__main__"):
    main()

