from os import getenv, listdir, path

from src.app.service.config import Config

conf = Config()

file_name = path.join(getenv("SNAP_COMMON"),"config.json")

if path.exists(file_name):
    print("Using config.json from snap_common")
    conf._file_name = file_name
    
conf.read_config()

if getenv("SNAP_DATA"):
    folder = getenv("SNAP_DATA").split("/bigboxx-sync")[0]
    folder = f"{folder}/bigboxx-kernel/current/storage"

values = {}

for file in listdir(folder):
    f = Config().read_files(f"{folder}/{file}")
    if f.get("value"):
        values[f.get("key")] = f.get("value")

conf.config["token"] = values.get("TOKEN")
conf.config["id_farm"] = values.get("FARM")
# conf.write_config(conf.config)

URL_DB = conf.config.get("url_db")
DATABASE = conf.config.get("db_name")


if conf.config.get("id_farm"):
    TOKEN = conf.config.get("token")
    URL_FARM = conf.config.get("url_farm")
    ID_FARM = int(conf.config.get("id_farm"))
    PORT_FARM = int(conf.config.get("port", 52000)) + ID_FARM

    FIRST_SYNC = conf.config.get("first_sync")
    IS_SYNC = conf.config.get("is_to_sync", False)

    if not (URL_DB and DATABASE and TOKEN and URL_FARM and ID_FARM):
        print(
            f"""\
            URL_DB: {URL_DB is not None},
            DATABASE: {DATABASE is not None},
            TOKEN: {TOKEN is not None},
            URL_FARM: {URL_FARM is not None},
            ID_FARM: {ID_FARM is not None}\
            """
        )


MAX_RECORD_SYNC = conf.config.get("max_record_sync", 1000)
