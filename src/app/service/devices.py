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

    def get_old_records(self):
        self.sensors = []
        self.registers = []
        start_page = 0

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
        self.max_register = max(total_sensors_with_values, self.max_register)
        register_number_for_sensor = int(self.max_register / total_sensors_with_values)
        
        while True:
            (
                new_registers,
                sensors_with_values,
            ) = self.device_reporsitory.get_values_from_sensors(
                sensors_with_values, start_page, register_number_for_sensor
            )

            self.registers.extend(new_registers)

            total_register = len(self.registers)

            if len(sensors_with_values) == 0 or total_register >= self.max_register:
                break

            start_page += register_number_for_sensor
            if total_register < self.max_register * 0.9:
                register_number_for_sensor = max(
                    1,
                    int(
                        (self.max_register - total_register) / len(sensors_with_values)
                    ),
                )
        return self.registers

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
