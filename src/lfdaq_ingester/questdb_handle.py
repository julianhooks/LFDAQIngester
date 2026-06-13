import logging
import os
import unittest
import time

import docker
from labjack import ljm
import questdb.ingress

logger = logging.getLogger(__name__)

def getQuestDBHandle() -> questdb.ingress.Sender:
    # we do want to use http here, not tcp, because more functionality is available for http
    # this uses the influx line protocol, not postgres
    
    try:
        questDBHandle = questdb.ingress.Sender(
            questdb.ingress.Protocol.Http, 
            os.getenv("LFDAQ_DB_URL"), 
            int(os.getenv("LFDAQ_DB_INFLUX_PORT")), 
            username=os.getenv("LFDAQ_DB_USERNAME"), 
            password=os.getenv("LFDAQ_DB_PASSWORD"),
            auto_flush=True,
            auto_flush_interval= int(os.getenv("LFDAQ_DB_AUTOFLUSH_INTERVAL_MS")),
            auto_flush_rows=int(os.getenv("LFDAQ_DB_AUTOFLUSH_ROWS")))
        logger.info(f"Connected to QuestDB influx port")
    except questdb.ingress.IngressError as error:
        logger.error(f"Error occured when connecting to questDB: {error}.")
        raise error
    
    return questDBHandle
