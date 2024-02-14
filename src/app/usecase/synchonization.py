from pymongo.database import Database
from bson.json_util import dumps
from loguru import logger
import asyncio

from src.app.config.envs import URL_FARM
from src.app.service.devices import Devices
from src.app.service.farm import Farm


class Synchonization:
    def __init__(self, db: Database, max_register=1000):
        self.devices = Devices(db, max_register)
        self.farm = Farm(URL_FARM)
        self.max_register = max_register

    def synchronize_records(self):
        logger.info("Start synchronize records")
        resp = self.farm.check_farm_status()

        if resp.status_code != 200:
            logger.info(f"Farm is not active: {resp.status_code}")
            return f"Farm is not active: {resp.status_code}"

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

        sensors = self.devices.get_old_records()

        if len(sensors) == 0:
            return "No records to synchronize"

        logger.info(f"total old records: {len(sensors)}")

        asyncio.run(self.farm.request_list_to_farm(sensors[: self.max_register]))

        self.__change_sensors_by_status()

        return len(sensors)

    def __change_sensors_by_status(self):
        for sensor in self.farm.request_status.keys():
            logger.info(
                f"sensor: {sensor} and status: {self.farm.request_status[sensor].keys()}"
            )
            for status in self.farm.request_status[sensor].keys():
                ids = self.farm.request_status[sensor][status]
                if status == 500:
                    logger.info(
                        f"sensor: {sensor} and status: {status} and total ids: {len(ids)}"
                    )
                    continue
                if status in [200, 201]:
                    logger.info(
                        f"update sensor: {sensor} and status: {status} and total ids: {len(ids)}"
                    )
                    self.devices.update_sensors(sensor, ids)
                if status in [300]:
                    logger.info(
                        f"delete sensor: {sensor} and status: {status} and total ids: {len(ids)}"
                    )
                    self.devices.delete_sensors(sensor, ids)
