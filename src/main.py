from labjack import ljm
import questdb.ingress
import psycopg as pg
import logging
from dataclasses import dataclass
import os

# [TO-DO] set up better logger config
logger = logging.getLogger(__name__)

dburl=os.getenv("DBURL")
labjackURL='jackjack.lan'

# [DONE] finish this dataclass
@dataclass
class Instrument:
    InstrumentID: str
    InstrumentName: str
    CalibrationFunction: callable
    IsActive: bool
    Unit: str
    IsLabJack: bool
    LabJackPort: str

def setup() -> tuple[int]:
    #setup returns
    labjackHandle = 0
    instruments = []
    questdbIngestHandle = None

    # Setup logging
    #logging.basicConfig(filename=f'{__name__}.log', level=logging.DEBUG)
    logging.basicConfig(level=logging.DEBUG)
    logger.info("Started Logging")

    # Program needs to do a couple things
    
    # [DONE] Connect to QuestDB for queries
    # getInstruments(dbconfigs) -> list[Instruments]:
    with pg.connect(
            host=dburl, 
            port=8812, 
            user='admin', 
            password='quest',
            dbname='LiquidsTestStand', 
            autocommit=True) as connector:
        with connector.cursor(binary=True, row_factory=pg.rows.dict_row) as cursor:
            cursor.execute("SELECT version")
            version = cursor.fetchone()
            logging.info(f'Connected to QuestDB version: {version["version"]}')
    
    # [IN-PROGRESS] pull active instruments (labjack port + calibration eq + database stuff) from database
            cursor.execute("SELECT * FROM Instruments")
            instrumentTable = cursor.fetchall()
            for row in instrumentTable:
                exec("cf = " + row["CalibrationFunction"])
                instruments.append(
                        Instrument(
                            row["InstrumentID"],
                            row["InstrumentName"],
                            cf,
                            bool(row["IsActive"]),
                            row["Unit"],
                            bool(row["IsLabJack"]),
                            row["LabJackPort"]))


    # [TO-DO] connect to QuestDB for sending
    # we do want to use http here, not tcp, because for functionality is available for http
    # this uses the influx line protocol, not postgres
    try:
        questDBHandle = questdb.ingress.Sender(
            questdb.ingress.Protocol.Http, 
            dburl, 
            9000, 
            username='admin', 
            password='quest')
    except questdb.ingress.IngressError as error:
        logging.error(f"Error occured when connecting to questDB: {error}.")
        raise error
        

    # [DONE] connect to Labjack
    # getLabJackHandle() -> int:
    try:
        labjackHandle = ljm.openS("T7","ANY","ANY")
    except ljm.LJMError as error:
        logging.error(f"Error occured when connecting to LabJack: {error}.")
        raise error
    logging.info(f"Connected to LabJack on {ljm.getHandleInfo(labjackHandle)}.")

    # [IN-PROGRESS] set up counters 1 and 2 for flowmeters
    ljm.eWriteName(labjackHandle,"DIO0_EF_ENABLE",0)
    ljm.eWriteName(labjackHandle,"DIO0_EF_INDEX",8)
    ljm.eWriteName(labjackHandle,"DIO0_EF_ENABLE",1)
    
    ljm.eWriteName(labjackHandle,"DIO1_EF_ENABLE",0)
    ljm.eWriteName(labjackHandle,"DIO1_EF_INDEX",8)
    ljm.eWriteName(labjackHandle,"DIO1_EF_ENABLE",1)

    # enable below and jump DAC1 to DIO0 to test counter
    # ljm.eWriteName(labjackHandle,"DAC1_FREQUENCY_OUT_ENABLE",1)

    # global timer1
    # timer1 = enableTimer()
    # global timer2
    # timer1 = enableTimer()

    return instruments, labjackHandle, questDBHandle
    
# [IN-PROGRESS] Exit cleanly on error (+ give me logs of what's going on) 
def onexit(labjackHandle, questDBHandle):
    try:
        ljm.close(labjackHandle)
        questDBHandle.close()
    except ljm.LJMError as error:
        logging.error(f"Error occured when disconnecting from LabJack: {error}.")
        raise error
    except questdb.ingress.IngressError as error:
        logging.error(f"Error occured when connecting to questDB: {error}.")
        raise error

# [IN-PROGRESS] Perform data ingestion:
# - Get voltages of each active instrument
# - Run calibration function on voltage
# - Write (time,voltage,value) to each instrument table
# - Repeat until close
def ingestLoop(instruments,labJackHandle,questDBHandle):
    for instrument in instruments:
        
        uncalibratedValue = ljm.eReadName(labJackHandle, instrument.LabJackPort)
        calibratedValue = instrument.CalibrationFunction(uncalibratedValue)
        
        questDBHandle.row(
                'InstrumentValues',
                symbols={'InstrumentID': instrument.InstrumentID},
                columns={
                    'UncalibratedValue': uncalibatedValue,
                    'CalibratedValue': calibratedValue},
                at=questdb.ingress.TimestampNanos.now())
        questDBHandle.flust()

def main() -> None:
    instruments, labJackHandle, questDBHandle = setup()
    while(True):
        ingestLoop(instruments,labJackHandle,questDBHandle)
    onexit(labJackHandle,questDBHandle)
    return

if (__name__ == "__main__"):
    main()
