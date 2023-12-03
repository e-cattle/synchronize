#!/usr/bin/env python3

from src.app.usecase.synchonization import Synchonization
from src.app.config import my_database 
from src.app.config.envs import MAX_RECORD_SYNC

from loguru import logger

def main():
    result = Synchonization(my_database, MAX_RECORD_SYNC).synchronize_records()
    logger.info(f"Finish synchronize records with result: {result}")

if __name__ == "__main__":
    main()