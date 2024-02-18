from pymongo.database import Database
from dateutil import parser
from loguru import logger
from bson.errors import InvalidDocument, InvalidId


class DevicesRepository:
    def __init__(self, db: Database):
        self.__db = db
        self.synchronized = False
        self.devices = []
        self.first_device = {}

    def get_devices(self) -> list:
        self.devices = []
        self.devices = list(self.__db.get_collection("devices").find({}))
        return self.devices

    def get_devices_to_sync(self, synchronized: bool = True) -> list:
        conditions = [
            {"synchronized": {"$exists": False}},
            {"synchronized": synchronized},
        ]
        self.devices = []
        self.devices = list(
            self.__db.get_collection("devices").find({"$or": conditions})
        )
        return self.devices

    def get_contracts(self, synchronized: bool = True) -> list:
        self.contracts = []
        conditions = [
            {"synchronized": {"$exists": False}},
            {"synchronized": synchronized},
        ]
        self.contracts = list(
            self.__db.get_collection("contracts").find({"$or": conditions})
        )
        return self.contracts

    def get_sensors_with_values(self, sensors: dict):
        sensors_with_value = []
        for sensor in sensors:
            sensor_size = self.__db.command("collStats", sensor["type"])["size"]
            if sensor_size > 0:
                sensors_with_value.append(sensor)
        self.sensors_with_value = sensors_with_value
        return self.sensors_with_value

    def get_union_collections(
        self, sensors: dict, start_page, final_page, synchronized=False
    ):
        # https://stackoverflow.com/questions/72987582/mongodb-aggregation-sort-on-a-union-of-collections-very-slow

        conditions = [{"synchronized": {"$exists": False}}, {"synchronized": False}]
        pipelines = [
            {"$match": {"$or": conditions}},
            {"$sort": {"date": 1}},
            {"$limit": 1},
        ]

        for position in range(1, len(sensors)):
            pipeline = self.__get_model_pipeline(
                sensors[position]["type"], synchronized, start_page, final_page
            )
            pipelines.append(pipeline)

        resp = self.__db.get_collection(sensors[0]["type"]).aggregate(pipelines)
        for r in resp:
            print(r)
        # 8/9/17 9:14
        print("---------------------")

    def get_values_from_sensors(
        self, sensors_values, start_page, final_page, synchronized=False
    ):
        list_sensors = []
        new_sensors = []
        registers = []
        conditions = [
            {"synchronized": {"$exists": False}},
            {"synchronized": synchronized},
        ]
        for type_sensor in sensors_values:
            list_sensors.append(type_sensor["type"])
            data_sensor = list(
                self.__db.get_collection(type_sensor["type"])
                .find({"$or": conditions})
                .sort("date", 1)
                .skip(start_page)
                .limit(final_page)
            )
            registers += list(
                map(
                    lambda data: self.__update_data(data, type_sensor["type"]),
                    data_sensor,
                )
            )
            if len(data_sensor) == final_page:
                new_sensors.append(type_sensor)

        return registers, new_sensors

    def get_values_from_sensors_with_condictions(
        self, sensors_values, max_register, registers=[]
    ):
        list_sensors = []
        new_sensors = []
        conditions = [
            {"synchronized": {"$exists": False}},
            {"synchronized": self.synchronized},
        ]
        register_number_for_sensor = int(max_register / len(sensors_values))

        for type_sensor in sensors_values:
            list_sensors.append(type_sensor["type"])
            data_sensor = list(
                self.__db.get_collection(type_sensor["type"])
                .find({"$or": conditions})
                .sort("date", 1)
                .limit(register_number_for_sensor)
            )
            registers += list(
                map(
                    lambda data: self.__update_data(data, type_sensor["type"]),
                    data_sensor,
                )
            )
            if len(data_sensor) == register_number_for_sensor:
                new_sensors.append(type_sensor)

        total_register = len(registers)
        if total_register < max_register * 0.9:
            max_register = max_register - total_register
            return self.get_values_from_sensors(new_sensors, max_register, registers)
        return registers

    def update_sensors(
        self, device: str, ids: list, new_value: dict = {"$set": {"synchronized": True}}
    ) -> bool:
        try:
            self.__db.get_collection(device).update_many(
                {"_id": {"$in": ids}}, new_value
            )
            return True
        except InvalidId as inval_id:
            logger.error(str(inval_id))
        except InvalidDocument as inval_doc:
            logger.error(str(inval_doc))
        return False

    def delete_sensors(self, device: str, ids: list) -> bool:
        try:
            result = self.__db.get_collection(device).delete_many({"_id": {"$in": ids}})
            logger.info(f"deleted records: {result.raw_result['n']}")
            self.__db.command({"planCacheClear": device})
            return True
        except InvalidId as inval_id:
            logger.error(str(inval_id))
        except InvalidDocument as inval_doc:
            logger.error(str(inval_doc))
        return False

    def __update_data(self, data, type_sensor):
        date_update = data["date"]
        if type(date_update) == str:
            date_update = parser.parse(date_update)
        data.update({"type": type_sensor, "date": date_update})
        return data

    def __get_model_pipeline(self, sensor, synchronized, start_page, final_page):
        return {
            "$unionWith": {
                "coll": sensor,
                "pipeline": [
                    {
                        "$match": {
                            "$or": [
                                {"synchronized": {"$exists": False}},
                                {"synchronized": synchronized},
                            ]
                        }
                    },
                    {"$sort": {"date": -1}},
                    {"$skip": start_page},
                    {"$limit": final_page},
                ],
            },
        }