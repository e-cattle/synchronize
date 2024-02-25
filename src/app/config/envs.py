from os import getenv, listdir, path

from src.app.service.config import Config

conf = Config()

if getenv("SNAP_COMMON"):
    file_name = path.join(getenv("SNAP_COMMON"),"config.json")

    if path.exists(file_name):
        conf._file_name = file_name
        
conf.read_config()
values = {}

if getenv("SNAP_DATA"):
    folder = getenv("SNAP_DATA").split("/bigboxx-sync")[0]
    folder = f"{folder}/bigboxx-kernel/current/storage"

    if path.exists(folder):
        for file in listdir(folder):
            f = Config().read_files(f"{folder}/{file}")
            if f.get("value"):
                values[f.get("key")] = f.get("value")

conf.config["token"] = values.get("TOKEN")
conf.config["id_farm"] = values.get("FARM")

URL_DB = conf.config.get("url_db")
DATABASE = conf.config.get("db_name")

TOKEN = None
URL_FARM = None
ID_FARM = None
PORT_FARM = None

FIRST_SYNC = conf.config.get("first_sync")
SYNC_ACTIVE = conf.config.get("is_sync_active", False)
DEL_REC_AFTER_SYNC = conf.config.get("del_record_after_sync", False)

if conf.config.get("id_farm"):
    TOKEN = conf.config.get("token")
    URL_FARM = conf.config.get("url_farm")
    ID_FARM = int(conf.config.get("id_farm"))
    PORT_FARM = int(conf.config.get("port", 52000)) + ID_FARM


MAX_RECORD_SYNC = conf.config.get("max_record_sync", 1000)
PRIORITIZE_COLLECTIONS = list(conf.config.get("prioritize_sync_collections", []))


GC_AVAIL_MEM_SYNC = conf.config.get("available_memory_sync", 20)
GC_AVAIL_MEM_NOT_SYNC = conf.config.get("available_memory_not_sync", 10)
GC_TOTAL_REC_DEL = conf.config.get("total_records_to_delete", 1000)

GC_PRIORITIZE_DEL_COLLECTIONS = list(
    conf.config.get("prioritize_delete_collections", [])
)
