#!/usr/bin/env python3

from src.app.usecase.synchonization import Synchonization
from src.app.usecase.garbage_collector import GarbageCollectorUseCase
from src.app.config import my_database 
from src.app.config.envs import MAX_RECORD_SYNC, URL_FARM, ID_FARM

from loguru import logger

def sync():
    if not URL_FARM or not ID_FARM:
        logger.error("URL_FARM or ID_FARM not found")
        return
    result = Synchonization(my_database, MAX_RECORD_SYNC).synchronize_records()
    logger.info(f"Finish synchronize records with result: {result}")

def gc():
    logger.info("Start garbage collector")
    GarbageCollectorUseCase(my_database, MAX_RECORD_SYNC).execute()
    logger.info("Finish garbage collector")

if __name__ == "__main__":
    sync()