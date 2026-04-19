from labjack import ljm
import questdb
import psycopg as pg
import logging
from dataclasses import dataclass

serverAddress = 'http::addr=liquids.lan:9000;'

logger = logging.getLogger(__name__)

@dataclass
class Instruments:
    number: int

def main() -> None:
    logging.basicConfig(filename=f'{__name__}.log', level=logging.DEBUG)
    logger.info("Started Logging")
    # Program needs to do a couple things
    # [DONE] Connect to QuestDB for queries
    with pg.connect(
            host='liquids-ts', 
            port=8812, 
            user='admin', 
            password='quest', 
            dbname='LiquidsTestStand', 
            autocommit=True) as connector:
        with connector.cursor(binary=True) as cursor:
            cursor.execute("SELECT version")
            version = cursor.fetchone()
            logging.info(f'Connected to QuestDB version: {version[0]}')
    # [TO-DO] pull active instruments (labjack port + calibration eq + database stuff) from database
            cursor.execute("SELECT * FROM Instruments")
            instrumentTable = cursor.fetchall()
            logging.debug(instrumentTable)
            for row in instrumentTable:
                logging.debug(instrumentTable)

    
    # [DONE] connect to Labjack
    try:
        labjackHandle = ljm.openS("T7","ANY","ANY")
    except ljm.LJMError as error:
        logging.error(f"Error occured when connecting to LabJack: {error}.")
        raise error

    # [TO-DO] connect to QuestDB for sending
    # [TO-DO] Perform data ingestion:
    # - Get voltages of each active instrument
    # - Run calibration function on voltage
    # - Write (time,voltage,value) to each instrument table
    # - Repeat until close
    # [TO-DO] Exit cleanly on error (+ give me logs of what's going on) 
    ljm.close(labjackHandle)

    return

if (__name__ == "__main__"):
    main()
