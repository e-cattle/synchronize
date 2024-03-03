#!/usr/bin/env python3

from src.app.usecase.synchonization import Synchonization
from src.app.usecase.garbage_collector import GarbageCollectorUseCase
from src.app.config import my_database 
from src.app.config.envs import MAX_RECORD_SYNC, GC_TOTAL_REC_DEL

from loguru import logger

def sync():
    result = Synchonization(my_database, MAX_RECORD_SYNC).synchronize_records()
    logger.info(f"Finish synchronize records with result: {result}")

def gc():
    GarbageCollectorUseCase(my_database, GC_TOTAL_REC_DEL).execute()
    logger.info("Finish garbage collector")

if __name__ == "__main__":
    sync()