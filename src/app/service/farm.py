from bson.json_util import dumps
from aiohttp.client import ClientSession
from requests import Response, post, get
from asyncio import gather, ensure_future

from src.app.config.envs import TOKEN, URL_FARM, ID_FARM, PORT_FARM


class Farm:
    def __init__(self, url=URL_FARM, id_farm=ID_FARM, token=TOKEN):
        self.__headers = {"authorization": f"Bearer {token}"}
        self.url = url.replace("$PORT", str(PORT_FARM))
        self.id_farm = id_farm
        self.request_status = {}

    def check_farm_status(self):
        try:
            response = get(f"{self.url}", headers=self.__headers)
        except Exception as err:
            response = Response()
            response.status_code = 500
            response.error = str(err)
        return response

    def save_contracts(self, data):
        try:
            response = post(
                f"{self.url}/cloud/contracts", json=data, headers=self.__headers
            )
        except Exception as err:
            response = Response()
            response.status_code = 500
            response.error = str(err)
        return response

    def save_devices(self, data):
        try:
            response = post(
                f"{self.url}/cloud/devices", json=data, headers=self.__headers
            )
        except Exception as err:
            response = Response()
            response.status_code = 500
            response.error = str(err)
        return response

    def request_to_farms_sync(self, data):
        try:
            response = post(
                f"{self.url}/cloud/sensors", json=data, headers=self.__headers
            )
        except Exception as err:
            response = Response()
            response.status_code = 500
            response.error = str(err)
        return response

    async def request_to_farm_async(self, session: ClientSession, device: dict):
        type_sensor = device["type"]
        del device["type"]
        data = {"type": type_sensor, "data": dumps(device), "mac": "18:FE:34:D3:0E:3D"}
        async with session.post(
            f"{self.url}/cloud/sensors", json=data, headers=self.__headers
        ) as resp:
            status = resp.status
            self.group_request(status, type_sensor, device.get("_id"))
            return device

    async def request_list_to_farm(self, sensors: list):
        async with ClientSession() as session:
            tasks = []
            for sensor in sensors:
                tasks.append(
                    ensure_future(self.request_to_farm_async(session, sensor))
                )
            await gather(*tasks)
        return True

    def group_request(self, status, type_sensor, id):
        if not self.request_status.get(type_sensor):
            self.request_status[type_sensor] = {status: [id]}
        elif self.request_status[type_sensor].get(status):
            self.request_status[type_sensor][status].append(id)
        else:
            self.request_status[type_sensor].update({status: [id]})
