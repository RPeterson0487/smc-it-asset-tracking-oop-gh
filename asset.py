"""This module provides functionality for the old and new db tables."""

# Standard library imports.

# Third party imports.

# Local application/library specific imports.
import dataclasses


@dataclasses.dataclass
class Asset:
    """This class combines the old and new assets."""
    
    def output(self, limited: bool = True, print_fields: list = None):
        if self.table == "IT_Assets":
            current = True
        else:
            current = False
        
        if limited:
            if current:
                output_dictionary = {
                    "Serial Number": self.serial,
                    "Device Type": self.device_type,
                    "Model": self.model,
                    "Asset Number": self.asset_number,
                    "Fork Truck": self.fork_truck_reference,
                    "IP Address": self.ip_address,
                    "Notes": self.notes,
                }
                for field in output_dictionary:
                    if field == "Fork Truck" and self.device_type not in ("Fork Truck Computer", "Scanning Gun"):
                        continue
                    elif field == "IP Address" and self.device_type == "Scanning Gun":
                        continue
                    else:
                        print(f"{field}: {output_dictionary[field] if output_dictionary[field] is not None and output_dictionary[field] != '' else ''}")
            
            else:
                output_dictionary = {}
                if hasattr(self, "Serial"):
                    output_dictionary["Serial Number"] = self.Serial
                if hasattr(self, "Model"):
                    output_dictionary["Model"] = self.Model
                if hasattr(self, "Asset"):
                    output_dictionary["Asset Number"] = self.Asset
                if hasattr(self, "Fork_Truck_No"):
                    output_dictionary["Fork Truck"] = self.Fork_Truck_No
                if hasattr(self, "Ip_Address"):
                    output_dictionary["IP Address"] = self.Ip_Address
                if hasattr(self, "Current_User"):
                    output_dictionary["Notes"] = self.Current_User
                    
                for field in output_dictionary:
                    print(f"{field}: {output_dictionary[field] if output_dictionary[field] is not None and output_dictionary[field] != '' else ''}")
                        
            print(f"\nFound in table {self.table} under {self.column} as {getattr(self, self.column)}")
            
        else:
            output_dictionary = vars(self)
            for key, value in output_dictionary.items():
                if (not print_fields or key in print_fields) and key not in ("is_duplicate", "is_migrated", "is_verified", "table", "column"):
                    print(f"{key}: {value}")
        if not current:
            print("Migration Status: This device has not yet been migrated to the new tracking table.")
    
    
    def __eq__(self, other):
        if isinstance(other, Asset):
            return vars(self) == vars(other)
        return False