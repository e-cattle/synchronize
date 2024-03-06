import os
from loguru import logger


class MemoryStatus:
    __free = 0
    __total = 0
    __used = 0

    def __init__(self):
        self.__memory_status()

    def __memory_status(self):
        st = os.statvfs('/home')
        self.__free = st.f_bavail * st.f_frsize
        self.__total = st.f_blocks * st.f_frsize
        self.__used = (st.f_blocks - st.f_bfree) * st.f_frsize
        self.__percent = self.__free / self.__total * 100

    def is_clear_memory(self, available_memory: int = 20):
        if self.__free == 0:
            return True
        logger.info(f"Memory available: {round(self.__percent,2)}%")
        return self.__percent < available_memory
    
    @property
    def percent(self):
        return self.__percent
