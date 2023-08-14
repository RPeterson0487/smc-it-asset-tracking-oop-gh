"""This module provides various menus and menu operations."""

# Standard library imports.
from datetime import datetime
from typing import Literal, Union
import os
import re

# Third party imports.

# Local application/library specific imports.
import database_manager as database


class MenuScreens:
    """Initializes Main Menu and runs program."""
    
    SEPARATOR = ("-" * os.get_terminal_size().columns)

    def __init__(self):
        """Displays the main menu and asks for input."""
        
        # Menu options that call methods when selected.
        self._menu_options = {
            "1": self.asset_search,
            "2": self.asset_edit,
            "3": self.asset_new,
            "0": self.quit_program,
        }
        
        # Program starting method.
        self.main_menu()


    def main_menu(self):
        """Display the main menu and wait for user input."""
        
        Utility.clear_screen()
        while True:
            
            print(f"==[ MAIN MENU ]{'=' * (os.get_terminal_size().columns - 15)}\n")
            print("1)  Search for asset")
            print("2)  Edit existing asset")
            print("3)  Create new asset")
            print("0)  Quit program")
            print(self.SEPARATOR)
            
            main_menu_select = MenuFunction(self, "n/a", "Enter menu option: ", list(self._menu_options.keys()), ["n/a"])
            menu_action = self._menu_options.get(main_menu_select.menu_input)
            menu_action()
    

    def asset_search(
        self,
        type_search: Literal["basic", "edit"] = "basic",
        output: Literal["limited", "full", "none"] = "limited",
        search_fields: list = [],
        search_term: str = None,
        use_like: bool = True
    ):
        option_number = 0
        
        if type_search == "basic":
            Utility.clear_screen()
        while True:
            migrated_count = 0
            duplicate_count = 0
            result_list = []
            
            # Set up menu and intial search prompt.
            if search_term or search_term == "":
                search_prompt = None
            elif type_search == "edit":
                search_prompt = "Search for asset to edit: "
            else:
                print(f"==[ BASIC SEARCH ]{'=' * (os.get_terminal_size().columns - 18)}")
                search_prompt = "Search for asset: "
                
            # Search for asset.
            if search_term or search_term == "":
                asset_search_term = search_term
            else:
                asset_search_term = MenuFunction(self, self.main_menu, search_prompt).menu_input
            if asset_search_term is None:
                if type_search == "edit":
                    self.asset_edit()
                else:
                    continue
            else:
                if search_fields and use_like:
                    asset_search_results = maria.search_tables(asset_search_term, search_fields)
                elif search_fields and not use_like:
                    asset_search_results = maria.search_tables(asset_search_term, search_fields, False)
                elif not search_fields and not use_like:
                    asset_search_results = maria.search_tables(asset_search_term, None, False)
                else:
                    asset_search_results = maria.search_tables(asset_search_term)
            
            # Set up output of search results.
            if asset_search_results != "Empty Search":
                for result in asset_search_results:
                    if result.table != "IT_Assets" and result.is_migrated == 1:
                        migrated_count += 1
                    elif result.table != "IT_Assets" and result.is_duplicate == 1:
                        duplicate_count += 1
                    else:
                        result_list.append(result)
                    
            # Output search results.
            if output != "none":
                for entry in result_list:
                    device_fields = self._set_device_fields(entry)
                    print()
                    if type_search == "edit" and len(result_list) >= 2:
                        option_number += 1
                        print(f"Option {option_number})\n")
                    if type_search != "edit" or (type_search == "edit" and len(result_list) >= 2):
                        if output == "full":
                            entry.output(False, device_fields)
                        elif output == "limited":
                            entry.output()
                        print(self.SEPARATOR)
            
            # Print results summary and / or return results if applicable.
            if output != "none" and asset_search_results:
                if migrated_count or duplicate_count:
                    print(f"Showing {len(result_list)} of {len(asset_search_results)} result{'' if (asset_search_results) == 1 else 's'}.")
                else:
                    print(f"Found {len(result_list)} result{'' if (asset_search_results) == 1 else 's'}.")
                if type_search != "edit":
                    if migrated_count:
                        print(f"{migrated_count} entr{'y' if duplicate_count == 1 else 'ies'} marked migrated hidden.")
                    if duplicate_count:
                        print(f"{duplicate_count} entr{'y' if duplicate_count == 1 else 'ies'} marked duplicate hidden.")
                    print()
            if type_search == "edit":
                return result_list


    def asset_edit(self):
        Utility.clear_screen()
        while True:
            print(f"==[ EDIT ASSET ]{'=' * (os.get_terminal_size().columns - 16)}")
            search_asset = self.asset_search("edit")
            if not search_asset:
                continue
            elif len(search_asset) == 1:
                select_asset = "1"
            else:
                select_asset = MenuFunction(self, self.asset_edit, "Select asset to edit: ", [str(i) for i in range(1, len(search_asset) + 1)]).menu_input
                if select_asset is None:
                    continue
            asset_id = self._edit_screen(self._process_duplicates_migrations(search_asset[int(select_asset) - 1]))
            if asset_id:
                Utility.clear_screen()
                print(f"==[ EDIT ASSET ]{'=' * (os.get_terminal_size().columns - 16)}\n")
                print(f"Asset ID {asset_id} has been updated in the database.")
                input("Press enter to continue.")
                Utility.clear_screen()
                continue
            print("An error has occured, please check the database.")
    
    
    def asset_new(self):
        initial_setup = {}
        Utility.clear_screen()
        while True:
            print(f"==[ NEW ASSET ]{'=' * (os.get_terminal_size().columns - 15)}")
            initial_serial = MenuFunction(self, self.main_menu, "Enter full serial: ").menu_input
            if initial_serial is None:
                continue
            else:
                asset_exists = self.asset_search("edit", "none", ["Serial", "serial"], initial_serial, False)
            
            if asset_exists:
                Utility.clear_screen()
                print(f"==[ NEW ASSET ]{'=' * (os.get_terminal_size().columns - 15)}\n")
                print("This asset already exists, please go to the edit screen.")
                input("Press enter to continue.")
                Utility.clear_screen()
                continue
            else:
                initial_type = self._edit_locked_list("device_type")
                # MenuFunction(self, self.asset_new, "Enter device type: ", ["n/a"], ["back", "cancel", "quit"]).menu_input
                if initial_type is None:
                    continue
                device_fields = self._set_device_fields(initial_type)
                
                for field in device_fields:
                    if field == "serial":
                        initial_setup[field] = initial_serial
                    elif field == "device_type":
                        initial_setup[field] = initial_type
                    else:
                        initial_setup[field] = None
                initial_setup["column"] = "new"
                    
                new_asset = maria.new_object(initial_setup)
                new_id = self._edit_screen(new_asset, False)
                Utility.clear_screen()
                print(f"==[ NEW ASSET ]{'=' * (os.get_terminal_size().columns - 15)}\n")
                print("New asset has been saved to the database.")
                print("Please take note of the new Asset ID below.\n")
                print(f"Asset ID: {new_id}\n")
                input("Press enter to continue.")
                Utility.clear_screen()
                continue
    
    
    def _process_duplicates_migrations(self, asset_object: object):
        migrated = False
        option_number = 0
        duplicate_list = []
        migrated_ouput = []
        
        # Check if the asset selected for edit is from the old or new table.
        if asset_object.table == "IT_Assets":
            current = True
            serial = asset_object.serial
        else:
            current = False
            serial = asset_object.Serial
        
        # Check the asset for duplicate entries by serial number.
        search_duplicates = self.asset_search("edit", "none", ["Serial", "serial"], serial, False)
        
        # If there are no duplicates, return the asset if from the new table.
        # If from the old table, send it on to be migrated.
        if len(search_duplicates) == 1:
            if current:
                return search_duplicates[0]
            else:
                self._migrate_asset(search_duplicates[0])
        
        # If no asset is returned at all (i.e., the serial number is missing)
        #   return or migrate the original asset.
        elif len(search_duplicates) == 0:
            if current:
                return asset_object
            else:
                self._migrate_asset(asset_object)
                
        # If there are duplicates, check if any of them are from the new table.
        else:
            for duplicate in search_duplicates:
                if duplicate.table == "IT_Assets":
                    migrated = True
                    break
            
            # If there are duplicates from the new table, mark any from the
            #   old table to be marked as migrated and removed from options
            #   to keep.    
            for asset in search_duplicates:
                if migrated:
                    if asset.table == "IT_Assets":
                        migrated_ouput.append(asset)
            
            # Select list of options to show depending on if there is an asset
            #   from the new table.
            if migrated:
                output_list = migrated_ouput
            else:
                output_list = search_duplicates
            
            # Clear the screen and show the options of which asset to
            #   keep active.
            Utility.clear_screen()
            while True:
                print(f"==[ Mark Duplicates ]{'=' * (os.get_terminal_size().columns - 21)}")
                if len(output_list) == 1:
                    select_duplicate = "1"
                else:
                    for entry in output_list:
                        device_fields = self._set_device_fields(entry)
                        print()
                        option_number += 1
                        print(f"Option {option_number})\n")
                        entry.output(False, device_fields)
                        print(self.SEPARATOR)
                
                # Get user input on which asset to keep.
                if not select_duplicate:
                    select_duplicate = MenuFunction(self, self.asset_edit, "Select duplicate to keep: ", [str(i) for i in range(1, len(output_list) + 1)]).menu_input
                if select_duplicate is None:
                    continue
                
                # Set any other duplicates to be marked as duplicate.
                else:
                    for duplicate in search_duplicates:
                        if duplicate != output_list[int(select_duplicate) - 1]:
                            duplicate_list.append(duplicate)
                
                # Mark assets from old tables as duplicated. Duplicates from
                #   new tables will show a message and a list.
                duplicate_message = False
                for asset in duplicate_list:
                    if asset.table != "IT_Assets":
                        setattr(asset, "is_duplicate", 1)
                        maria.save_object(asset)
                    else:
                        if not duplicate_message:
                            duplicate_message = True
                            
                            Utility.clear_screen()
                            print(f"==[ Mark Duplicates ]{'=' * (os.get_terminal_size().columns - 21)}")
                            print(f"{'!' * os.get_terminal_size().columns}")
                            print("Please send a message to the IT department with the following information.")
                            print("Copy / Paste if possible.\n\n")
                            print("Duplicate(s) detected in the new IT Assets table:\n")
                        print(f"Asset Number: {asset.asset_number}")
                        print(f"Serial Number: {asset.serial}")
                        print(self.SEPARATOR)
                if duplicate_message:
                    print(f"\n{'!' * os.get_terminal_size().columns}")
                    input("Press enter to continue.")
                
                # If selected asset is from old table, send it to be migrated.
                #  Otherwise, return it.
                if output_list[int(select_duplicate) - 1].table == "IT_Assets":
                    return output_list[int(select_duplicate) - 1]
                else:
                    self._migrate_asset(search_duplicates[int(select_duplicate) - 1])
    
    
    def _migrate_asset(self, old_asset: object):
        new_setup = {}
        new_asset_reference = {}
        asset_reference_list = []
        new_linux_reference = {}
        linux_reference_list = []
        unconvertable_datatype = {}
        device_type_mapping = {
            "IT_Assets_DT": "Desktop", "IT_Assets_FT": "Fork Truck Computer",
            "IT_Assets_LT": "Laptop", "IT_Assets_PR": "Printer",
            "IT_Assets_SG": "Scanning Gun", "IT_Assets_SV": "Server",
            "IT_Assets_SW": "Switch", "IT_Assets_TB": "Tablet",
            "IT_Assets_TC": "Thin Client"
        }
        attribute_mapping = {
            "Asset": "asset_reference", "AssetOld": "asset_reference",
            "Building": "building", "Contract_Number": "contract_reference",
            "Current_User": "notes", "Location": "department",
            "Department": "department", "Fork_Truck_No":"fork_truck_reference",
            "ilo": "integrated_lights_out", "Ip_Address": "ip_address",
            "Kiwi_No": "kiwi_printer_reference", "Last_Seen": "last_seen",
            "Linux_Hostname": "linux_printer_reference",
            "Linux_No": "linux_printer_reference",
            "linuxdata": "linux_printer_reference",
            "manufacturer": "manufacturer", "Model": "model",
            "Name": "device_name", "OS": "operating_system",
            "Purchase_Date": "purchase_date",
            "Purchase_Price": "purchase_price", "Serial": "serial"
        }
        datatype_mapping = {
            "last_seen": datetime.date,
            "purchase_date": datetime.date,
            "purchase_price": float,
        }
        
        for old_device, new_device in device_type_mapping.items():
            if old_asset.table == old_device:
                new_device_type = new_device
                break
        
        new_fields = self._set_device_fields(new_device_type)
        
        if hasattr(old_asset, "Asset") and self._check_device_fields(new_fields, "asset_reference"):
            asset_reference_list.append(str(old_asset.Asset))
        if hasattr(old_asset, "AssetOld") and self._check_device_fields(new_fields, "asset_reference") and old_asset.AssetOld not in asset_reference_list:
            asset_reference_list.append(old_asset.AssetOld)
        if asset_reference_list:
            new_asset_reference = " --- ".join(item for item in asset_reference_list if item)
        
        if hasattr(old_asset, "Linux_Hostname") and self._check_device_fields(new_fields, "linux_printer_reference"):
            linux_reference_list.append(old_asset.Linux_Hostname)
        if hasattr(old_asset, "Linux_No") and self._check_device_fields(new_fields, "linux_printer_reference"):
            linux_reference_list.append(old_asset.Linux_No)
        if hasattr(old_asset, "linuxdata") and self._check_device_fields(new_fields, "linux_printer_reference"):
            linux_reference_list.append(old_asset.linuxdata)
        if linux_reference_list:
            new_linux_reference = " --- ".join(item for item in linux_reference_list if item)
        
        for new_attribute in new_fields:
            if new_attribute in attribute_mapping.values():
                old_attribute = None
                for key, value in attribute_mapping.items():
                    if value == new_attribute:
                        old_attribute = key
                        break
                if old_attribute in ("Asset", "AssetOld"):
                    new_value = new_asset_reference
                elif old_attribute in ("Linux_Hostname", "Linux_No", "linuxdata"):
                    new_value = new_linux_reference
                else:
                    new_value = getattr(old_asset, old_attribute, None)
                new_setup[new_attribute] = new_value
            else:
                new_setup[new_attribute] = None
        new_setup["device_type"] = new_device_type
        new_setup["column"] = "migrate"
        
        for key, value in new_setup.items():
            if key in datatype_mapping and value:
                try:
                    if key == "last_seen" and isinstance(value, datetime):
                        new_setup[key] = value.date()
                    elif key == "purchase_date":
                        new_setup[key] = datetime.strptime(value, "%m/%d/%Y").date()
                    elif key == "purchase_price":
                        pattern = r'^\$?(\d{1,3},?)*\d+(\.\d+)?$'
                        if re.match(pattern, value.strip()):
                            float_string = value.strip().replace("$", "").replace(",", "")
                            float_number = float(float_string)
                            float_round = round(float_number, 2)
                            new_setup[key] = float_round
                        else:
                            unconvertable_datatype[key] = value
                            new_setup[key] = None
                except(ValueError, TypeError) as error:
                    unconvertable_datatype[key] = value
                    new_setup[key] = None
        
        Utility.clear_screen()
        print("The following information will be lost, please take note:\n")
        for field, entry in unconvertable_datatype.items():
            print(f"{field.capitalize()}: {entry}")
        input("\nPress enter to continue.")
        
        asset_id = self._edit_screen(maria.new_object(new_setup), False)
        if asset_id:
            old_asset.is_migrated = 1
            maria.save_object(old_asset)
            
            Utility.clear_screen()
            print(f"==[ MIGRATING ASSET ]{'=' * (os.get_terminal_size().columns - 21)}\n")
            print(f"Asset {old_asset.Asset} has been migrated from {old_asset.table}.")
            print("Please take note of the new Asset ID below.\n")
            print(f"Asset ID: {asset_id}\n")
            input("Press enter to continue.")
            Utility.clear_screen()
            
        else:
            input("Please check database for possible errors.")
        self.asset_edit()
    
    
    def _set_device_fields(self, asset: Union[object, str]):
        fields_dictionary = {}
        display_fields = []
        if asset not in ("device_type", "status"):
            fields_dictionary["Common"] = maria.field_control["Common"]
        if isinstance(asset, str):
            asset_type = asset
        elif isinstance(asset, object) and hasattr(asset, "table") and asset.table == "IT_Assets":
            asset_type = asset.device_type
        else:
            return None
        fields_dictionary[asset_type] = maria.field_control[asset_type]
        
        if asset in ("device_type", "status"):
            display_fields = fields_dictionary[asset_type]
        else:
            for field in maria.insert_key_list:
                if self._check_device_fields(fields_dictionary, field):
                    display_fields.append(field)
        return display_fields
    
    
    def _check_device_fields(self, device_fields: Union[dict, list], field: str):
        if isinstance(device_fields, dict):
            for field_list in device_fields.values():
                if field in field_list:
                    return True
        else:
            if field in device_fields:
                return True
        return False
    
    
    def _edit_screen(self, asset: object, short: bool = False):
        while True:
            fields = []
            ignore_keys = ["is_verified", "table", "column"]
            locked_fields = ["asset_number", "serial", "device_type", "last_seen"]
            locked_list_fields = ("device_type", "status")
            required_fields = ["manufacturer", "model", "entity", "building", "department"]
            date_fields = ("deployment_date", "purchase_date", "contract_expiration_date")
            float_fields = ("purchase_price","contract_amount")
            int_fields = ()
            list_fields = ("asset_reference", "notes")
            option_number = 0
            
            Utility.clear_screen()
            
            if not hasattr(asset, "serial"):
                locked_fields.remove("serial")
                required_fields.append("serial")
            
            if asset.column == "new":
                print(f"==[ NEW ASSET ]{'=' * (os.get_terminal_size().columns - 15)}\n")
                ignore_keys.append("asset_number")
                back_command = self.asset_new
            elif asset.column == "migrate":
                print(f"==[ MIGRATING ASSET ]{'=' * (os.get_terminal_size().columns - 21)}\n")
                ignore_keys.append("asset_number")
                back_command = self.asset_new
            else:
                print(f"==[ EDIT ASSET ]{'=' * (os.get_terminal_size().columns - 16)}\n")
                back_command = self.asset_edit
                
            output_dictionary = vars(asset)
            device_fields = self._set_device_fields(asset)
            
            items = list(output_dictionary.items())
            for _, (key, value) in enumerate(items):
                if not self._check_device_fields(device_fields, key):
                    continue
                if key not in ignore_keys:
                    if key in required_fields:
                        postfix = "(REQUIRED)"
                    elif key in locked_fields :
                        postfix = "(LOCKED)"
                    else:
                        postfix = ""
                    
                    if key in date_fields:
                        value = self._convert_date(str(value))
                    option_number += 1
                    if value is not None and value != "":
                        print(f"{option_number})  {key.capitalize()}: {value} {postfix}")
                    else:
                        print(f"{option_number})  {key.capitalize()}: {'_' * 10} {postfix}")
                    fields.append(key)
            print(f"{self.SEPARATOR}")
            
            if short:
                break
            
            print("save: Save changes to database.")
            print("WARNING: The below commands will discard any changes!")
            select_field = MenuFunction(self, back_command, "Enter command or select field to edit: ", [str(i) for i in range(1, len(fields) + 1)] + ["save"], ["back", "cancel", "quit"]).menu_input
            
            if select_field is None:
                continue
            elif select_field.lower().strip() == "save":
                saved_asset = self._edit_save(asset, required_fields)
                if saved_asset:
                    return saved_asset
                else:
                    input("Nothing has been changed in the database. Press enter to continue.")
            else:
                if fields[int(select_field) - 1] in date_fields:
                    self._edit_date_field(asset, fields[int(select_field) - 1])
                elif fields[int(select_field) - 1] in list_fields:
                    self._edit_list_field(asset, fields[int(select_field) - 1])
                elif fields[int(select_field) - 1] in float_fields:
                    self._edit_number_field(asset, fields[int(select_field) - 1], float)
                elif fields[int(select_field) - 1] in int_fields:
                    self._edit_number_field(asset, fields[int(select_field) - 1], int)
                elif fields[int(select_field) - 1] in locked_fields and asset.column:
                    self._edit_locked_field(asset, fields[int(select_field) - 1])
                elif fields[int(select_field) - 1] in locked_list_fields:
                    self._edit_locked_list(fields[int(select_field) - 1], asset)
                else:
                    self._edit_field(asset, fields[int(select_field) - 1])


    def _edit_date_field(self, editing_asset: object, attribute):
        sql_date = str(getattr(editing_asset, attribute))
        if sql_date is None or sql_date == "None" or sql_date == "":
            display_date = "empty"
        else:
            display_date = self._convert_date(sql_date)
        
        self._edit_screen(editing_asset, True)
        print("back: Go back to previous screen.\n")
        print(f"{attribute.capitalize()} current date: {display_date}\n")
        
        while True:
            print("Warning: Current date will be overwritten")
            new_date = MenuFunction(self, self._edit_screen, "Enter new date (MM/DD/YYYY): ", ["n/a"], ["n/a"], editing_asset).menu_input
            if new_date is None:
                continue
            elif new_date == "back":
                break
            else:
                valid_date = self._convert_date(new_date)
                if not valid_date:
                    print("\nInvalid date format, please try again.")
                    continue
                else:
                    setattr(editing_asset, attribute, valid_date)
                    break
    
    
    def _convert_date(self, date: str):
        try:
            date_object = datetime.strptime(date, "%Y-%m-%d")
            formatted_date = date_object.strftime("%m/%d/%Y")
        except ValueError:
            try:
                date_object = datetime.strptime(date, "%m/%d/%Y")
                formatted_date = date_object.strftime("%Y-%m-%d")
            except ValueError:
                return None
        return formatted_date
    
    
    def _edit_list_field(self, editing_asset: object, attribute):
        go_back = False
        sql_entries = str(getattr(editing_asset, attribute))
        if sql_entries is None or sql_entries == "None" or sql_entries == "":
            entries_list = []
        else:
            entries_list = [item.strip() for item in sql_entries.split("---")]
        
        while True:
            if go_back:
                break
            else:
                self._output_list_entries(editing_asset, attribute, entries_list)
            while True:
                option_list = [str(i) for i in range(1, len(entries_list) + 2)]
                option_list.append("back")
                print("back: Go back to previous screen.\n")
                select_entry = MenuFunction(self, self._edit_screen, "Enter command or select entry to add or edit: ", option_list, ["n/a"], editing_asset).menu_input
                if select_entry == "back":
                    go_back = True
                    break
                self._output_list_entries(editing_asset, attribute, entries_list)
                
                if int(select_entry) == (len(entries_list) + 1):
                    print("back: Go back to previous screen.\n")
                    print("New entry\n")
                    prompt = "Enter command or new entry: "
                else:
                    print("back: Go back to previous screen.    delete: Delete this entry\n")
                    print(f"Current entry: {entries_list[int(select_entry) - 1]}\n")
                    print("Warning: Current entry will be overwritten")
                    prompt = "Enter command or new entry: "
                edit_entry = MenuFunction(self, "n/a", prompt, ["n/a"], ["n/a"]).menu_input
                if edit_entry.lower().strip() == "back":
                    break
                elif edit_entry.lower().strip() == "delete":
                    if len(entries_list) == 0:
                        break
                    else:
                        entries_list.pop(int(select_entry) - 1)
                else:
                    if int(select_entry) == (len(entries_list) + 1):
                        if len(" --- ".join(entries_list)) + len(edit_entry) >= 225:
                            print("There are too many notes, please edit or delete existing notes.")
                            input("Press enter to continue.")
                            break
                        entries_list.append(edit_entry)
                    else:
                        entries_list[int(select_entry) - 1] = edit_entry
                setattr(editing_asset, attribute, (" --- ".join(entries_list)))
                break


    def _output_list_entries(self, asset: object, display_attribute, entries: list):
        option_number = 0
        
        self._edit_screen(asset, True)
        print(f"{display_attribute.capitalize()} current entries:\n")
        
        for entry in entries:
            option_number += 1
            print(f"{option_number})  {entry}")
        option_number += 1
        print(f"{option_number})  <Add new entry>")
        print(self.SEPARATOR)
    
    
    def _edit_locked_list(self, asset_field: Literal["device_type", "status"], editing_asset: object = None):
        options = self._set_device_fields(asset_field)
        
        while True:
            if editing_asset:
                self._edit_screen(editing_asset, True)
            else:
                Utility.clear_screen()
                if asset_field == "device_type":
                    print(f"==[ DEVICE TYPE ]{'=' * (os.get_terminal_size().columns - 17)}\n")
                else:
                    print(f"==[ DEVICE STATUS ]{'=' * (os.get_terminal_size().columns - 19)}\n")
                    
            if asset_field == "device_type":
                option_prompt = "Select device type: "
            else:
                option_prompt = "Select device status: "
            
            if editing_asset:
                if getattr(editing_asset, asset_field) is not None:
                    print(f"{asset_field.capitalize()} current setting: {getattr(editing_asset, asset_field)}\n")
                else:
                    print(f"{asset_field.capitalize()} has not been set.\n")
            option_number = 0
            for items in options:
                option_number += 1
                print(f"{option_number})  {items}")
            option_list = [str(i) for i in range(1, len(options) + 1)]
            option_list.append("back")
            print(self.SEPARATOR)
            print("back: Go back to previous screen.\n")
            
            select_option = MenuFunction(self, "n/a", option_prompt, option_list, ["n/a"]).menu_input
            if select_option.lower().strip() == "back":
                Utility.clear_screen()
                break
            else:
                if editing_asset:
                    setattr(editing_asset, asset_field, options[int(select_option) - 1])
                    break
                else:
                    return options[int(select_option) - 1]
                
        
    def _edit_number_field(self, editing_asset: object, attribute, data_type: Union[float, int]):
        sql_number = getattr(editing_asset, attribute)
        
        if sql_number is None or sql_number == "None" or sql_number == "":
            sql_number = "empty"
        elif data_type is float:
            sql_number = float(format(sql_number, ".2f"))
        else:
            sql_number = int(sql_number)
        
        self._edit_screen(editing_asset, True)
        print("back: Go back to previous screen.\n")
        print(f"Current {attribute.capitalize()}: {sql_number}\n")
        
        while True:
            print("Warning: Current data will be overwritten")
            new_number = MenuFunction(self, self._edit_screen, "Enter new data: ", ["n/a"], ["n/a"], editing_asset).menu_input
            if new_number == "back":
                break
            try:
                new_number = float(new_number)
            except ValueError as error:
                print(f"\n{error}\n")
                print("Invalid input, please try again.\n")
                continue
            if data_type is float:
                new_number = float(format(new_number, ".2f"))
            else:
                new_number = int(new_number)
            setattr(editing_asset, attribute, new_number)
            break
        
    
    def _edit_field(self, editing_asset: object, attribute):
        sql_data = getattr(editing_asset, attribute)
        if sql_data is None or sql_data == "None" or sql_data == "":
            sql_data = "empty"
        self._edit_screen(editing_asset, True)
        print("back: Go back to previous screen.\n")
        print(f"{attribute.capitalize()} current data: {sql_data}\n")
        
        while True:
            print("Warning: Current data will be overwritten")
            new_data = MenuFunction(self, self._edit_screen, "Enter new data: ", ["n/a"], ["n/a"], editing_asset).menu_input
            if new_data is None:
                continue
            elif new_data == "back":
                break
            elif len(new_data) >= 255:
                print("Entry is too long, please shorten to under 255 characters.")
                continue
            else:
                setattr(editing_asset, attribute, new_data)
                break
    
    
    def _edit_locked_field(self, editing_asset: object, attribute):
        self._edit_screen(editing_asset, True)
        if attribute == "last_seen":
            print('This will update when using the "save" command.')
            input("Press enter to continue.")
        elif editing_asset.column == "new":
            print(f"{attribute.capitalize()} cannot be edited from this screen.")
            print('Please use the "back" command and reenter the correct serial and device type.')
            input("Press enter to continue.")
        else:
            print(f"{attribute.capitalize()} is not editable, please contact an admin to fix.")
            input("Press enter to continue.")
    
    
    def _edit_save(self, editing_asset: object, check_fields: list):
        missing_fields = []
        for field in check_fields:
            if not getattr(editing_asset, field):
                missing_fields.append(field.capitalize())
        if missing_fields:
            self._edit_screen(editing_asset, True)
            print("The following fields are required and have not been filled in. Please complete and save again.")
            print(", ".join(missing_fields))
            print()
        else:
            current_date = datetime.now().date()
            editing_asset.last_seen = current_date
            return maria.save_object(editing_asset)
    
    
    def quit_program(self):
        Utility.clear_screen()
        maria.close_connection()
        print("\nGoodbye!\n")
        exit()




class MenuFunction:
    """Provides menu and input functionality."""
    
    def __init__(
        self: object,
        calling_class,
        back_to: str = "n/a",
        prompt: str = "",
        menu_options: list = ["n/a"],
        command_options: list = ["all"],
        pass_object: object = None,
        search_term: str = None
    ):
        """Instatiates menu input class."""
        
        # Class variable(s) used to indicate where "cancel" and "back" should go.
        self._calling_class = calling_class
        self._back_to = back_to
        self._pass_object = pass_object
        
        # Class variable(s) used to display the input prompt.
        self._prompt = prompt
        
        # Class variable(s) used for the calling menu.
        self._menu_options = menu_options
        
        # Class variable for user input or selection
        self.menu_input = search_term
        
        # Class variable(s) used to display the list of commands (i.e. "back").
        self._command_options = [(command.lower()) for command in command_options]
        self._command_list = []
        self._command_print_dict = {
            "clear": ": Clear the screen.",
            "back": ": Go back to previous screen.",
            "cancel": ": Go back to main menu.",
            "quit": ": Disconnect from database and quit the program.",
        }
        
        # Input methods not needed if search term is defined by the caller.
        if not search_term:
            # Method to list available commands before user input.
            self._list_commands()
            
            # Method to ask user for input.
            self._get_user_input()


    def _list_commands(self):
        """List commands that can be used from input."""
        
        if "all" in self._command_options:
            self._command_list.extend(["clear", "back", "cancel", "quit"])
        elif ("n/a" in self._command_options):
            return
        else:
            if "clear" in self._command_options:
                self._command_list.append("clear")
            if "back" in self._command_options:
                self._command_list.append("back")
            if "cancel" in self._command_options:
                self._command_list.append("cancel")
            if "quit" in self._command_options:
                self._command_list.append("quit")
        
        for command in self._command_list:
            print(f"{command}{self._command_print_dict[command]}", end = "    ")
        print("\n")
    
    
    def _get_user_input(self):
        while True:
            user_input = input(self._prompt).strip()
            
            if user_input.lower() in self._command_list:
                if user_input.lower() == "clear":
                    Utility.clear_screen()
                    break
                elif user_input.lower() == "back":
                    if self._pass_object:
                        self._back_to(self._pass_object)
                    else:
                        self._back_to()
                elif user_input.lower() == "cancel":
                    self._calling_class.main_menu()
                elif user_input.lower() == "quit":
                    self._calling_class.quit_program()
            elif not user_input or (user_input not in self._menu_options and "n/a" not in self._menu_options):
                # Clear the screen, show "invalid input," and redisplay menu, commands, and input.     #!!!!!!!!!!!!!!!!!!!!
                print("Invalid input, please try again.\n")
            else:
                self.menu_input = user_input
                break




class Utility:
    """Provides functions for use by menus."""
    
    def clear_screen():
        if os.name == "posix":
            os.system("clear")
        else:
            os.system("cls")
            
            


if __name__ == "__main__":
    maria = database.DatabaseManager()
    start = MenuScreens()