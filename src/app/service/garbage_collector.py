import os
from pymongo.database import Database
from loguru import logger

from src.app.service import list_oldest_records, delete_sensors


class GarbageCollector:
    __free = 0
    __total = 0
    __used = 0

    def __init__(self):
        self.__memory_status()

    def __memory_status(self):
        st = os.statvfs("/")
        self.__free = st.f_bavail * st.f_frsize
        self.__total = st.f_blocks * st.f_frsize
        self.__used = (st.f_blocks - st.f_bfree) * st.f_frsize

    def __is_clear_memory(self, available_memory: int = 20):
        return (self.__free / self.__total * 100) < available_memory

    def clear_memory(self, db: Database, synchronized: bool = True):
        if self.__is_clear_memory():
            keys, sensors = list_oldest_records(db, synchronized=synchronized)
            if len(keys) == 0 and synchronized == True:
                if self.__is_clear_memory(available_memory=10):
                    logger.info(
                        "no synchronized records were found, starting a new search..."
                    )
                    return self.clear_memory(db, False)
            if len(keys) > 0:
                for sensor in sensors:
                    logger.info(f"initiating deletion of sensor data: {sensor}")
                    result = list(
                        map(
                            lambda data: data["_id"],
                            list(filter(lambda x: x["type"] == sensor, keys)),
                        )
                    )
                    if len(result) > 0:
                        delete_sensors(db, device=sensor, ids=result)
            else:
                logger.info(f"There is no record to delete.")
