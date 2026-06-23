"""

"""
import logging
import os
import time
import unittest

import docker
import questdb.ingress

from lfdaq_ingester.questdb_handle import QuestDBHandle

logger = logging.getLogger(__name__)


class QuestDBHandleTestFixture(unittest.TestCase):
    """

    """

    def create_questdb_container(self):
        """

        """
        os.environ["LFDAQ_DB_URL"] = "127.0.0.1"
        os.environ["LFDAQ_DB_PG_PORT"] = "8812"
        os.environ["LFDAQ_DB_INFLUX_PORT"] = "9000"
        os.environ["LFDAQ_DB_USERNAME"] = "admin"
        os.environ["LFDAQ_DB_PASSWORD"] = "quest"
        os.environ["LFDAQ_DB_NAME"] = ""
        os.environ["LFDAQ_DB_AUTOFLUSH_INTERVAL_MS"] = "1000"
        os.environ["LFDAQ_DB_AUTOFLUSH_ROWS"] = "10"
        # Start test database docker container
        self.docker_client = docker.from_env()
        self.questdb_instance = self.docker_client.containers.run(
                "questdb/questdb",
                detach=True,
                ports={9000: 9000, 9009: 9009, 8812: 8812, 9003: 9003})
        # Give the container some time to set up before we test
        time.sleep(4)

    def remove_questdb_container(self):
        """

        """
        os.environ.pop("LFDAQ_DB_URL")
        os.environ.pop("LFDAQ_DB_INFLUX_PORT")
        os.environ.pop("LFDAQ_DB_PG_PORT")
        os.environ.pop("LFDAQ_DB_USERNAME")
        os.environ.pop("LFDAQ_DB_PASSWORD")
        os.environ.pop("LFDAQ_DB_NAME")
        os.environ.pop("LFDAQ_DB_AUTOFLUSH_INTERVAL_MS")
        os.environ.pop("LFDAQ_DB_AUTOFLUSH_ROWS")
        self.questdb_instance.stop()

    def setUp(self) -> None:
        self.create_questdb_container()

    def runTest(self) -> None:
        questdb_handle = QuestDBHandle()
        self.assertIsInstance(questdb_handle, questdb.ingress.Sender)
        with questdb_handle:
            dbLogs = str(self.questdb_instance.logs())
            self.assertTrue(("http-server connected" in dbLogs))

    def tearDown(self) -> None:
        self.remove_questdb_container()


if (__name__ == "__main__"):
    unittest.main()
