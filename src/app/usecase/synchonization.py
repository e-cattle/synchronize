from pymongo.database import Database
from bson.json_util import dumps
from loguru import logger
import asyncio

from src.app.config.envs import (
    URL_FARM,
    ID_FARM,
    SYNC_ACTIVE,
    DEL_REC_AFTER_SYNC,
    PRIORITIZE_COLLECTIONS,
)
from src.app.service.devices import Devices
from src.app.service.farm import Farm


class Synchonization:
    def __init__(self, db: Database, max_register=1000):
        if ID_FARM:
            self.devices = Devices(db, max_register)
            self.farm = Farm(URL_FARM)
            self.max_register = max_register

    def synchronize_records(self):
        if not self.__are_variables_valid():
            return "Variables are not valid"

        logger.info("Start synchronize records")
        if not self.__check_farm_status():
            return "Farm is not active"

        contracts = self.devices.get_unsynchronized_contracts()

        if len(contracts) > 0:
            logger.info(f"Update contracts: {len(contracts)}")
            data = {
                "type": "contracts",
                "data": dumps(contracts),
                "mac": "02:42:ac:1b:00:05",
            }
            resp = self.farm.save_contracts(data)
            logger.info(resp.text)
            if resp.status_code > 201:
                return "Error in farm"
            self.devices.update_contracts_to_sync()
            return "Update contracts"

        devices = self.devices.get_unsynchronized_devices()
        if len(devices) > 0:
            logger.info(f"Update devices: {len(devices)}")
            data = {
                "type": "devices",
                "data": dumps(devices),
                "mac": "02:42:ac:1b:00:05",
            }
            resp = self.farm.save_devices(data)
            if resp.status_code > 201:
                return "Error in farm"
            self.devices.update_devices_to_sync()
            return "Update devices"

        sensors = self.devices.get_old_records(priority=PRIORITIZE_COLLECTIONS)
        if len(sensors) == 0:
            return "No records to synchronize"

        logger.info(f"total old records: {len(sensors)}")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self.farm.request_list_to_farm(sensors[: self.max_register])
        )

        self.__change_sensors_by_status()

        return len(sensors)

    def __are_variables_valid(self):
        if not SYNC_ACTIVE:
            logger.info("Synchronization is not active")
            return False
        if not URL_FARM:
            logger.info("Farm URL is not defined")
            return False
        if not ID_FARM:
            logger.info("Farm ID is not defined")
            return False
        return True

    def __check_farm_status(self):
        resp = self.farm.check_farm_status()
        if resp.status_code != 200:
            logger.info(f"Farm is not active: {resp.status_code}")
            return False
        return True

    def __change_sensors_by_status(self):
        for sensor, values in self.farm.request_status.items():
            for status, ids in values.items():
                if status == 500:
                    logger.info(
                        f"sensor: {sensor} and status: {status} and total ids: {len(ids)}"
                    )
                elif DEL_REC_AFTER_SYNC or status == 300:
                    logger.info(
                        f"delete sensor: {sensor} and status: {status} and total ids: {len(ids)}"
                    )
                    self.devices.delete_sensors(sensor, ids)

                elif status in [200, 201]:
                    logger.info(
                        f"update sensor: {sensor} and status: {status} and total ids: {len(ids)}"
                    )
                    self.devices.update_sensors(sensor, ids)
