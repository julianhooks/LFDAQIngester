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

class dbTest(unittest.TestCase):

    def runTest(self) -> None:
        # Set relevant environment variables for test
        os.environ["LFDAQ_DB_URL"] = "127.0.0.1"
        os.environ["LFDAQ_DB_INFLUX_PORT"] = "9000"
        os.environ["LFDAQ_DB_USERNAME"] = "admin"
        os.environ["LFDAQ_DB_PASSWORD"] = "quest"
        os.environ["LFDAQ_DB_AUTOFLUSH_INTERVAL_MS"] = "1000"
        os.environ["LFDAQ_DB_AUTOFLUSH_ROWS"] = "10"

        # Start test database
        dockerClient = docker.from_env()
        questDBInstance = dockerClient.containers.run("questdb/questdb", 
                                                      detach = True, 
                                                      ports={9000:9000,
                                                             9009:9009,
                                                             8812:8812,
                                                             9003:9003})

        # Give the container some time to set up before we test
        time.sleep(3)

        try:
            result = getQuestDBHandle() 
            self.assertIsInstance(result,questdb.ingress.Sender)
            with result as handle:
                dbLogs = str(questDBInstance.logs())
                self.assertTrue(("http-server connected" in dbLogs))

        finally:
            # Make sure to clean up unneeded environment variables 
            os.environ.pop("LFDAQ_DB_URL")
            os.environ.pop("LFDAQ_DB_INFLUX_PORT")
            os.environ.pop("LFDAQ_DB_USERNAME")
            os.environ.pop("LFDAQ_DB_PASSWORD")
            os.environ.pop("LFDAQ_DB_AUTOFLUSH_INTERVAL_MS")
            os.environ.pop("LFDAQ_DB_AUTOFLUSH_ROWS")

            # Cleanup test database
            questDBInstance.stop()

        return
    
if (__name__ == "__main__"):
    unittest.main()