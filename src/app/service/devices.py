from pymongo.database import Database

from src.app.repository.devices import DevicesRepository


class Devices:
    def __init__(self, db: Database, max_register=1000, synchronized: bool = False):
        self.max_register = max_register
        self.synchronized = synchronized
        self.device_reporsitory = DevicesRepository(db)
        self.devices = []
        self.contracts = []

    def get_unsynchronized_contracts(self):
        self.contracts = []
        self.contracts = self.device_reporsitory.get_contracts(False)
        return self.contracts

    def get_unsynchronized_devices(self):
        self.devices = []
        self.devices = self.device_reporsitory.get_devices_to_sync(False)
        return self.devices

    def get_old_records(self, synchronized: bool = False, priority: list = []):
        self.sensors = []
        self.registers = []        

        self.devices = self.device_reporsitory.get_devices()
        if len(self.devices) == 0:
            return []

        for device in self.devices:
            self.sensors.extend(device["sensors"])

        sensors_with_values = self.device_reporsitory.get_sensors_with_values(
            self.sensors
        )
        total_sensors_with_values = len(sensors_with_values)
        if total_sensors_with_values == 0:
            return []

        priority_sensors = [sensor for sensor in sensors_with_values if sensor["type"] in priority]
        if len(priority_sensors) > 0:
            print(f"priority sensors: {len(priority_sensors)}")
            self.registers.extend(
                self.__get_sensors(priority_sensors, self.max_register*0.7, synchronized)
            )

        other_sensors = [sensor for sensor in sensors_with_values if sensor["type"] not in priority]
        if len(other_sensors) > 0:
            print(f"other sensors: {len(other_sensors)}")
            max_register = self.max_register - len(self.registers)
            self.registers.extend(
                self.__get_sensors(other_sensors, max_register, synchronized)
            )
        
        return self.registers
    
    def __get_sensors(self, sensors: list, max_register: int, synchronized: bool = False):
        start_page = 0
        total_sensors = len(sensors)
        max_register = max(total_sensors, max_register)
        target_register_count = int(max_register / total_sensors)
        registers = []
        
        while True:
            new_registers, sensors = self.device_reporsitory.get_values_from_sensors(
                sensors, start_page, target_register_count, synchronized
            )

            registers.extend(new_registers)
            total_register = len(registers)

            if len(sensors) == 0 or total_register >= max_register:
                break

            start_page += target_register_count
            if total_register < max_register * 0.9:
                register_count = int((max_register - total_register) / len(sensors))
                target_register_count = max(1, register_count)
        return registers

    def update_contracts_to_sync(self):
        ids = []

        for contract in self.contracts:
            ids.append(contract["_id"])

        self.device_reporsitory.update_sensors("contracts", ids)

    def update_devices_to_sync(self):
        ids = []

        for devices in self.devices:
            ids.append(devices["_id"])

        self.device_reporsitory.update_sensors("devices", ids)

    def update_sensors(self, collection: str, ids: list):
        self.device_reporsitory.update_sensors(collection, ids)

    def delete_sensors(self, collection: str, ids: list):
        self.device_reporsitory.delete_sensors(collection, ids)
