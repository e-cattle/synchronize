from loguru import logger
from pymongo.database import Database

from src.app.service.memory_status import MemoryStatus
from src.app.service.devices import Devices


class GarbageCollectorUseCase:
    def __init__(self, db: Database, max_register=1000):
        self._devices = Devices(db, max_register, True)
        self._max_register = max_register
        self._memory_status = MemoryStatus()

    def execute(self, available_memory: int = 20, synchronized: bool = True):
        logger.info("Starting garbage collection")
        if self._memory_status.is_clear_memory(available_memory=10):
            data_sensors = self._devices.get_old_records()
            if len(data_sensors) > 0:
                records_to_delete = self.__get_map_list_ids(
                    self._devices.sensors, data_sensors
                )
                if records_to_delete:
                    for key in records_to_delete.keys():
                        self._devices.delete_sensors(key, records_to_delete[key])

        elif self._memory_status.is_clear_memory(available_memory=available_memory):
            data_sensors = self._devices.get_old_records()
            if len(data_sensors) > 0:
                records_to_delete = self.__get_map_list_ids(
                    self._devices.sensors, data_sensors
                )
                if records_to_delete:
                    for key in records_to_delete.keys():
                        self._devices.delete_sensors(key, records_to_delete[key])
            else:
                return self.execute(10, False)

    def __get_map_list_ids(self, sensors: list, registers: list):
        data = {}
        logger.info(f"initiating deletion of sensor data: {sensors}")
        for sensor in sensors:
            ids = list(
                map(
                    lambda data: data["_id"],
                    list(filter(lambda x: x["type"] == sensor["type"], registers)),
                )
            )
            if len(ids) > 0:
                data[sensor["type"]] = ids
        return data
