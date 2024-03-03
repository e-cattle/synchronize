from loguru import logger
from pymongo.database import Database
import asyncio

from src.app.service.memory_status import MemoryStatus
from src.app.service.devices import Devices
from src.app.service.farm import Farm
from src.app.config.envs import URL_FARM, GC_PRIORITIZE_DEL_COLLECTIONS


class GarbageCollectorUseCase:
    def __init__(self, db: Database, max_register=1000):
        self._devices = Devices(db, max_register, True)
        self._max_register = max_register
        self._memory_status = MemoryStatus()
        
    def execute(self, available_memory: int = 20, synchronized: bool = True):
        logger.info("Starting garbage collection")
        if self._memory_status.is_clear_memory(available_memory=available_memory):
            if not synchronized:
                synchronized = self.__synchronize_records()
            deleted = self.__clear_memory(synchronized)
            if not deleted:
                return self.execute(10, False)
    
    def __clear_memory(self, synchronized: bool = True):
        data_sensors = self._devices.get_old_records(synchronized, priority=GC_PRIORITIZE_DEL_COLLECTIONS)
        if len(data_sensors) > 0:
            records_to_delete = self.__get_map_list_ids(
                self._devices.sensors, data_sensors
            )
            if records_to_delete:
                for key in records_to_delete.keys():
                    logger.info(f"deleting sensor data: {key} and total ids: {len(records_to_delete[key])}")
                    self._devices.delete_sensors(key, records_to_delete[key])
                return True
        elif not synchronized:
            logger.info("No records to delete")
            return True
        return False

    def __get_map_list_ids(self, sensors: list, registers: list):
        data = {}
        logger.info(f"initiating deletion of sensors: {len(sensors)} and registers: {len(registers)}")
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

    def __synchronize_records(self):
        try:
            logger.info("Start synchronize records in garbage collector")
            synced = False
            farm = Farm(URL_FARM)
            sensors = self._devices.get_old_records()
            if len(sensors) == 0:
                logger.info("No records to synchronize in garbage collector")
                return synced
            
            loop = asyncio.get_event_loop()
            loop.run_until_complete(farm.request_list_to_farm(sensors[: self.max_register]))
            for sensor, values in self.farm.request_status.items():
                for status, ids in values.items():
                    if status in [200, 201]:
                        logger.info(f"update sensor: {sensor} and status: {status} and total ids: {len(ids)} in garbage collector")
                        self._devices.update_sensors(sensor, ids)
                        synced = True
        except Exception:
            logger.error("Error in synchronize records in garbage collector")
        return synced