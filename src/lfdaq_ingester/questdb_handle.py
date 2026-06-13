import logging
import os
import unittest
import time

import docker
from labjack import ljm
import questdb.ingress

logger = logging.getLogger(__name__)

class QuestDBHandle(questdb.ingress.Sender):
    def __init__(self):
        super().__init__(
            questdb.ingress.Protocol.Http, 
            os.getenv("LFDAQ_DB_URL"), 
            int(os.getenv("LFDAQ_DB_INFLUX_PORT")), 
            username=os.getenv("LFDAQ_DB_USERNAME"), 
            password=os.getenv("LFDAQ_DB_PASSWORD"),
            auto_flush=True,
            auto_flush_interval= int(os.getenv("LFDAQ_DB_AUTOFLUSH_INTERVAL_MS")),
            auto_flush_rows=int(os.getenv("LFDAQ_DB_AUTOFLUSH_ROWS")))
        logger.info(f"Connected to QuestDB influx port")
