"""This module provides functionality for the old and new db tables."""

# Standard library imports.

# Third party imports.

# Local application/library specific imports.
import dataclasses


@dataclasses.dataclass
class AssetNew:
    """This class is for the assets in the new table."""
    
    # Attributes
    asset_number: int
    asset_reference: str
    device_type: str
    ip_address: str
    serial: str
    manufacturer: str
    model: str
    entity: str
    building: str
    department: str
    fork_truck_number: str
    map_reference: str
    device_name: str
    operating_system: str
    user_name: str
    integrated_lights_out: str
    status: str
    deployment_date: str                                    #DATE
    linux_printer_reference: str
    kiwi_printer_reference: str
    purchase_date: str                                      #DATE
    purchase_price: float
    pearson_kelly_id: str
    contract_reference: str
    contract_expiration_date: str                           #DATE
    contract_amount: float
    notes: str
    last_seen: str                                          #DATE
    is_verified: int
    table: str
    column: str
    
    def output(self, limited: bool = True):
        if limited:
            output_dictionary = {
                "Serial Number": self.serial,
                "Device Type": self.device_type,
                "Model": self.model,
                "Asset Number": self.asset_number,
                "Fork Truck": self.fork_truck_number,
                "IP Address": self.ip_address,
                "Notes": self.notes,
            }
            for field in output_dictionary:
                if field == "Fork Truck" and (self.device_type != "Fork Truck Computer" or self.device_type != "Scanning Gun"):
                    continue
                else:
                    print(f"{field}: {output_dictionary[field] if output_dictionary[field] is not None and output_dictionary[field] != '' else ''}")
            print(f"Found in table {self.table} under {self.column} as {getattr(self, self.column)}")
        else:
            AssetFunction.output_full(self)
            
            
            # print(f"Serial Number: {AssetFunction._check_result_value(asset_dictionary.get(('serial' if current else 'Serial'), 'key missing'))}")
            # if current:
            #     print(f"Device Type: {AssetFunction._check_result_value(asset_dictionary.get('device_type', 'key missing'))}")
            # print(f"Model: {AssetFunction._check_result_value(asset_dictionary.get(('model' if current else 'Model'), 'key missing'))}")
            # print(f"Asset Number: {AssetFunction._check_result_value(asset_dictionary.get(('asset_number' if current else 'Asset'), 'key missing'))}")
            # if current and asset_dictionary["device_type"] == "Fork Truck":
            #     print(f"Fork Truck: {AssetFunction._check_result_value(asset_dictionary.get('fork_truck_number', 'key missing'))}")
            # elif not current and asset_dictionary["table"] == "IT_Assets_FT":
            #     print(f"Fork Truck: {AssetFunction._check_result_value(asset_dictionary.get('Fork_Truck_No', 'key missing'))}")
            # if asset_dictionary["table"] != "IT_Assets_SG":
            #     print(f"IP Address: {AssetFunction._check_result_value(asset_dictionary.get(('ip_address' if current else 'Ip_Address'), 'key missing'))}")
            # print(f"Notes: {AssetFunction._check_result_value(asset_dictionary.get(('notes' if current else 'Current_User'), 'key missing'))}")
            # print(f"Found in table {asset_dictionary['table']} under {asset_dictionary['column']} as {asset_dictionary.get(asset_dictionary['column'], 'Error')}.")
            # if not current:
            #     print("Migration Status: This device has not yet been migrated to the new tracking table.")


@dataclasses.dataclass
class AssetOld:
    """This class is for the assets in the old table."""
    
    # Attributes (most are created at object instantiation)
    Asset: int
    Serial: str
    Model: str
    is_migrated: int
    is_duplicate: int
    table: str
    column: str
    
    # Blank variables for use in output.
    Fork_Truck_No: str = None
    Ip_Address: str = None
    Current_User: str = None  # This is the "notes" field.
    
    def output_limited(self, limited: bool = True):
        pass


class AssetFunction:
    """This class provides shared methods for the two asset classes."""
    
    def output_full():
        pass