import os
from loguru import logger


class MemoryStatus:
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

    def is_clear_memory(self, available_memory: int = 20):
        if self.__free == 0:
            return True
        logger.info(f"{self.__free / self.__total * 100}, {self.__free}, {self.__used}, {self.__total}")
        return (self.__free / self.__total * 100) < available_memory
