import aiohttp, asyncio, requests
from pymongo.database import Database
from bson.json_util import dumps
from aiohttp.client import ClientSession
from loguru import logger


from src.app.config.envs import FIRST_SYNC, URL_FARM
from src.app.service import list_oldest_records, update_sensors
from src.app.service.devices import get_devices


class Synchonization:
    __headers = {
        "auth": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjb2RlRmFybSI6MSwiaWF0IjoxNjE5NzI0MTYwLCJleHAiOjE3Nzc1MTIxNjB9.6Sg4ozy9v_CPzYiB1KxjyNtw3wz5LmKR6TPafa3XWwg"
    }
    __values = 0

    async def request_to_farm(
        self, db: Database, session: ClientSession, url: str, device: dict
    ):
        type_sensor = device["type"]
        # print(deviceu
        del device["type"]
        data = {"type": type_sensor, "data": dumps(device)}
        async with session.post(url, json=data, headers=self.__headers) as resp:
            status = resp.status
            if status in [200, 201]:
                update_sensors(db, type_sensor, [device.get("_id")])
                self.__values += 1
            elif status == 301:
                ...  # delete_sensors(db, device.get('type'), [device.get('_id')])
            else:
                ...  # logger.info("Error internal Value")
            return device

    async def request_list_to_farm(self, db: Database, url: str, list_device: list):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for device in list_device:
                tasks.append(
                    asyncio.ensure_future(
                        self.request_to_farm(db, session, url, device)
                    )
                )
            await asyncio.gather(*tasks)

    def synchronize_records(self, db: Database, url_sync: str = URL_FARM):
        try:
            response = requests.get(url_sync, headers=self.__headers)
            if response.status_code == 200:
                if FIRST_SYNC:
                    device = get_devices(db)
                    data = {"type": "device", "data": dumps(device)}
                    response = requests.post(
                        url_sync, json=data, headers=self.__headers
                    )
                else:
                    registers, list_sensors = list_oldest_records(db=db)
                    asyncio.run(self.request_list_to_farm(db, url_sync, registers))
        except Exception as err:
            logger.error(f"error communicating with the farm: {err}")
        print(self.__values)
        # interversoes, botao para suspender,
        # demon para rodar a cada 10 segundos
        # tela do cloud com um botao
        # snap commons
        #   isSync if (True)
        #   verificar JWT if ()
        #   verificar o ID if ()
        #   teste / status get(e-cattle/farm/123) -> if (200) OK
        #    pegar a collection dos dados - > list  OK
        # marcar os dados como enviados -> Ok
