"""This module provides various menus and menu operations."""

# Standard library imports.
from datetime import datetime
from loguru import logger
from typing import Literal, Union
import os
import re
import sys

# Third party imports.

# Local application/library specific imports.
import database_manager as database


class CommandClass:
    """Initializes Main Menu and runs program."""

    def __init__(self):
        """Displays the main menu and asks for input."""
        
        self._terminal_width = None
        
        # Menu options that call methods when selected.
        self._menu_options = {
            "1": self.asset_search,
            "2": self.asset_full_search,
            "3": self.asset_edit,
            "4": self.asset_new,
            "5": self.asset_print,
            "0": self.exit_program,
        }
        
        # Program starting method.
        self.main_menu()


    def main_menu(self):
        """Display the main menu and wait for user input."""
        
        self.clear_screen()
        while True:
            # Resets terminal width used for separators and wrapping.
            self._terminal_width = os.get_terminal_size().columns
            
            if maria.database_name == "smc_db_TEST":
                print("!!!TEST MODE!!!\n\n")
        
            print(f"==[ MAIN MENU ]{'=' * (self._terminal_width - 15)}\n")
            print('1)  Basic output "label" search')
            print('2)  Extended output "full" search')
            print("3)  Edit existing asset")
            print("4)  Create new asset")
            print("5)  Print asset report")
            print("0)  Exit program")
            print("-" * self._terminal_width)
            
            menu_options = list(self._menu_options.keys())
            main_menu_select = self.menu_input("Enter menu option: ", menu_options, True)
            logger.info(f"Main Menu Select: {main_menu_select}")
            menu_action = self._menu_options.get(main_menu_select)
            menu_action()
            self.clear_screen()
    

    def asset_search(
        self,
        type_search: Literal["basic", "edit"] = "basic",
        output: Literal["limited", "full", "none"] = "limited",
        search_fields: list = [],
        search_term: str = None,
        use_like: bool = True,
        full_return = False,
        second_search = False
    ):
        option_number = 0
        prefix_list = ["A- Asset Number.", "R- Asset Reference.", "S- Serial.", "H- Hidden (all)", "D- Destroyed/Retired"]
        hidden_results = None
        
        with logger.contextualize(type_search = type_search, output = output, search_fields = search_fields, search_term = search_term, use_like = use_like):
            logger.info("Asset Search Start")
        
        if type_search == "basic" and not second_search:
            self.clear_screen()
        while True:
            current_line = ""
            duplicate_count = 0
            migrated_count = 0
            retired_count = 0
            hidden_list = []
            retired_list = []
            result_list = []
            
            # Set up menu and intial search prompt.
            if search_term or search_term == "":
                search_prompt = None
            elif type_search == "edit":
                search_prompt = "Search for asset to edit: "
                command_inputs = ["B", "X"]
            else:
                print(f"==[ ASSET SEARCH ]{'=' * (self._terminal_width - 18)}")
                search_prompt = "Search for asset: "
                command_inputs = ["B", "C", "X"]
                
            # Search for asset.
            if search_term or search_term == "":
                asset_search_term = search_term
            else:
                print("Search Prefix (No space):")
                for prefix in prefix_list:
                    prefix_string = f"{prefix}  "
                    if len(current_line) + len(prefix_string) <= os.get_terminal_size().columns:
                        current_line += prefix_string
                    else:
                        print(current_line)
                        current_line = prefix_string
                print(current_line)
                
                asset_search_term = self.menu_input(search_prompt, command_inputs)
                if not asset_search_term:
                    continue
                elif type_search == "edit" and asset_search_term.upper() == "B":
                    return "go_back"
                elif type_search != "edit" and asset_search_term.upper() == "B":
                    break
                elif len(asset_search_term) < 3:
                    print("Search term too short, please refine your search to at least three characters.\n")
                    continue
                
            with logger.contextualize(search_prompt = search_prompt):
                logger.info(f"Asset Search Term: {asset_search_term}")
                
            if asset_search_term[0:2].upper() == "A-" or (asset_search_term[0] == "0" and len(asset_search_term) == 6):
                search_fields.extend(["Asset", "asset_number"])
                use_like = False
                asset_search_term = asset_search_term[2:].lstrip("0")
            elif asset_search_term[0:2].upper() == "R-":
                search_fields.extend(["asset_reference"])
                asset_search_term = asset_search_term[2:]
            elif asset_search_term[0:2].upper() == "S-":
                search_fields.extend(["serial", "Serial"])
                use_like = False
                asset_search_term = asset_search_term[2:]
            elif asset_search_term[0:2].upper() == "H-":
                hidden_results = "all"
                asset_search_term = asset_search_term[2:]
            elif asset_search_term[0:2].upper() == "D-":
                hidden_results = "limited"
                asset_search_term = asset_search_term[2:]
                
            
            if search_fields and use_like:
                asset_search_results = maria.search_tables(asset_search_term, search_fields)
            elif search_fields and not use_like:
                asset_search_results = maria.search_tables(asset_search_term, search_fields, False)
            elif not search_fields and not use_like:
                asset_search_results = maria.search_tables(asset_search_term, None, False)
            else:
                asset_search_results = maria.search_tables(asset_search_term)
            with logger.contextualize(search_fields = search_fields, use_like = use_like, asset_search_term = asset_search_term):
                logger.info(f"Asset search returned: {len(asset_search_results)}.")
            
            if second_search:
                return asset_search_results
            elif "asset_number" in search_fields and not asset_search_results:
                print("\nNo results found, searching under general.")
                asset_search_results = self.asset_search(type_search, output, [], asset_search_term, True, full_return, True)
            
            # Set up output of search results.
            if asset_search_results != "Empty Search":
                for result in asset_search_results:
                    if result.table == "IT_Assets" and (result.status == "Retired" or result.status == "Destroyed"):
                        retired_count += 1
                        retired_list.append(result)
                    elif result.table != "IT_Assets" and result.is_migrated == 1:
                        migrated_count += 1
                        hidden_list.append(result)
                    elif result.table != "IT_Assets" and result.is_duplicate == 1:
                        duplicate_count += 1
                        hidden_list.append(result)
                    else:
                        result_list.append(result)
                    
            if hidden_results == "all":
                output_list = retired_list + hidden_list
            elif hidden_results == "limited":
                output_list = retired_list
            else:
                output_list = result_list
            
            # Output search results.
            if output != "none":
                for entry in output_list:
                    device_fields = self._set_device_fields(entry)
                    print()
                    if type_search == "edit" and len(output_list) >= 2:
                        option_number += 1
                        print(f"Option {option_number})\n")
                    if type_search != "edit" or (type_search == "edit" and len(output_list) >= 2):
                        if output == "full":
                            entry.output(False, device_fields)
                        elif output == "limited":
                            entry.output()
                        print("-" * self._terminal_width)
            
            # Print results summary and / or return results if applicable.
            if output != "none":
                if migrated_count or duplicate_count or retired_count:
                    print(f"Showing {len(output_list)} of {len(asset_search_results)} result{'' if (asset_search_results) == 1 else 's'}.")
                else:
                    print(f"Found {len(output_list)} result{'' if (asset_search_results) == 1 else 's'}.")
                if migrated_count:
                    print(f"{migrated_count} entr{'y' if migrated_count == 1 else 'ies'} marked migrated {'shown' if hidden_results == 'all' else 'hidden'}.")
                if duplicate_count:
                    print(f"{duplicate_count} entr{'y' if duplicate_count == 1 else 'ies'} marked duplicate {'shown' if hidden_results == 'all' else 'hidden'}.")
                if retired_count:
                    print(f"{retired_count} entr{'y' if retired_count == 1 else 'ies'} marked retired or destroyed {'hidden' if not hidden_results else 'shown'}.")
                print()
            with logger.contextualize(hidden_results = hidden_results):
                logger.info(f"Asset Search Results: Returned: {len(output_list)}, Migrated: {migrated_count}, Duplicate: {duplicate_count}, Retired: {retired_count}")
            
            hidden_results = False
            use_like = True
            search_fields = []
            
            if full_return:
                return asset_search_results
            elif type_search == "edit":
                return output_list
    
    
    def asset_full_search(self):
        self.asset_search(output="full")
    
    
    def asset_print(self):
        self.clear_screen()
        logger.info("Asset Print Start")
        while True:
            print(f"==[ PRINT ASSET REPORT ]{'=' * (self._terminal_width - 24)}")
            search_asset = self.asset_search(type_search="edit", search_fields=[], output="full")
            if not search_asset:
                logger.info("Asset Print Search: No results found.")
                continue
            elif search_asset == "go_back":
                break
            elif len(search_asset) == 1:
                select_asset = "1"
            else:
                select_asset = self.menu_input("Select asset report to print: ", [str(i) for i in range(1, len(search_asset) + 1)] + ["B", "M", "X"], True)
            if select_asset.upper() == "B":
                self.clear_screen()
                continue
            else:
                header = ["Asset Report"]
                if hasattr(search_asset[int(select_asset) - 1], "is_migrated") and search_asset[int(select_asset) - 1].is_migrated == 0:
                    header.append("Migration Status: This device has not yet been migrated to the new tracking table.")
                elif hasattr(search_asset[int(select_asset) - 1], "is_migrated") and search_asset[int(select_asset) - 1].is_migrated == 1:
                    header.append("Migration Status: This device has been migrated and cannot be edited.")
                try:
                    self.output_to_printer(search_asset[int(select_asset) - 1], header)
                except:
                    print("\n\n!!! An error has occurred, please try again later. !!!\n")
                    input("Press enter to continue.")
                    self.clear_screen()
                    continue
                print("\nAsset report sent to the printer\n")


    def asset_edit(self):
        self.clear_screen()
        logger.info("Asset Edit Start")
        while True:
            print(f"==[ EDIT ASSET ]{'=' * (self._terminal_width - 16)}")
            search_asset = self.asset_search(type_search="edit", search_fields=[])
            if not search_asset:
                logger.info("Asset Edit Search: No results found.")
                continue
            elif search_asset == "go_back":
                break
            elif len(search_asset) == 1:
                if hasattr(search_asset[0], "is_migrated") and search_asset[0].is_migrated == 1:
                    print("This asset has been migrated.  Please find the new asset and edit it.\n")
                    input("Press enter to continue.\n")
                    self.clear_screen()
                    continue
                elif hasattr(search_asset[0], "is_duplicate") and search_asset[0].is_duplicate == 1:
                    print("This asset has been marked as a duplicate of another.  Please find that device and edit it.\n")
                    input("Press enter to continue.\n")
                    self.clear_screen()
                    continue
                else:
                    select_asset = "1"
            else:
                while True:
                    select_asset = self.menu_input("Select asset to edit: ", [str(i) for i in range(1, len(search_asset) + 1)] + ["B", "M", "X"], True)
                    if select_asset.upper() != "B" and hasattr(search_asset[int(select_asset) - 1], "is_migrated") and search_asset[int(select_asset) - 1].is_migrated == 1:
                        print("\nThis asset has been migrated.  Please find the new asset and edit it.\n")
                        continue
                    elif select_asset.upper() != "B" and hasattr(search_asset[int(select_asset) - 1], "is_duplicate") and search_asset[int(select_asset) - 1].is_duplicate == 1:
                        print("\nThis asset has been marked as a duplicate of another.  Please find that device and edit it.\n")
                        continue
                    if select_asset.upper() != "B":
                        with logger.contextualize(select_asset = select_asset):
                            logger.info(f"Asset Edit Selection: {vars(search_asset[int(select_asset) - 1])}")
                    else:
                        with logger.contextualize(select_asset = select_asset):
                            logger.info(f"Asset Edit Selection: Back")
                    break
                if select_asset.upper() == "B":
                    self.clear_screen()
                    continue
                        
            duplicate_migration_check = self._process_duplicates_migrations(search_asset[int(select_asset) - 1])
            if not duplicate_migration_check:
                break
            else:
                asset_id = self._edit_screen(duplicate_migration_check)
            logger.info(f"Asset Edit Complete, Asset ID {asset_id}")
            if asset_id:
                self.clear_screen()
                print(f"==[ EDIT ASSET ]{'=' * (self._terminal_width - 16)}\n")
                print(f"Asset ID {asset_id} has been updated in the database.\n")
                input("Press enter to continue.")
                self.clear_screen()
                continue
            else:
                self.clear_screen()
                continue
    
    
    def asset_new(self):
        initial_setup = {}
        
        self.clear_screen()
        logger.info("Asset New Start")
        while True:
            print(f"==[ NEW ASSET ]{'=' * (self._terminal_width - 15)}")
            initial_serial = self.menu_input("Enter full serial: ", ["B", "X"])
            logger.info(f"Asset New Initial Serial: {initial_serial}")
            if initial_serial.upper() == "B":
                break
            else:
                asset_exists = self.asset_search("edit", "none", ["Serial", "serial"], initial_serial, False, True)
            
            if asset_exists:
                logger.error(f"Asset Exists: {asset_exists}")
                self.clear_screen()
                print(f"==[ NEW ASSET ]{'=' * (self._terminal_width - 15)}\n")
                print("This asset already exists, please go to the edit screen.")
                input("Press enter to continue.")
                self.clear_screen()
                continue
            else:
                initial_type = self._edit_fixed_list("device_type")
                logger.info(f"Asset New Initial Type: {initial_type}")
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
                logger.info(f"Asset New Asset: {vars(new_asset)}")
                new_id = self._edit_screen(new_asset, False)
                
                if not new_id:
                    logger.info("New Asset Cancelled")
                    self.clear_screen()
                    continue
                else:
                    logger.info(f"Asset New ID: {new_id}")
                    self.clear_screen()
                    print(f"==[ NEW ASSET ]{'=' * (self._terminal_width - 15)}\n")
                    print("New asset has been saved to the database.")
                    print("Please take note of the new Asset ID below.\n")
                    print(f"Asset ID: {new_id}\n")
                    print("A new asset report has (probably) been sent to the IT printer.")
                    print("Please make sure to give this to Ben.\n")
                    input("Press enter to continue.")
                    self.clear_screen()
                    self.output_to_printer(new_asset, ["New Asset Added", f"Asset Number:  {new_id}"], ["asset_number"])
                    continue
    
    
    def output_to_printer(self, print_object: object, extra: list = [], exclude: list = []):
        object_dictionary = vars(print_object)
        print_file = f"print_file_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        exclude_list = exclude + ["table", "column", "is_verified"]
        
        if hasattr(print_object, "asset_number") and print_object.asset_number:
            print_file += f"_{print_object.asset_number}"
        
        with open(f"{print_file}.txt", "w") as file:
            for item in extra:
                file.write(f"{item}\r\n")
            file.write("\r\n")
            for key, value in object_dictionary.items():
                if key not in exclude_list:
                    file.write(f"{key.capitalize()}:  {value}\r\n")
        
        if os.name == "posix":
            os.system(f"cat {print_file}.txt |netcat -w 1 90.8.3.14 9100")
        else:
            os.startfile(f"{print_file}.txt", "print")
            
    
    def _process_duplicates_migrations(self, asset_object: object):
        migrated = False
        option_number = 0
        duplicate_list = []
        migrated_ouput = []
        
        with logger.contextualize(asset_object = vars(asset_object)):
            logger.info("Dup/Mig Start")
        
        # Check if the asset selected for edit is from the old or new table.
        if asset_object.table == "IT_Assets":
            current = True
            serial = asset_object.serial
        else:
            current = False
            serial = asset_object.Serial
        
        # Check the asset for duplicate entries by serial number.
        search_duplicates = self.asset_search("edit", "none", ["Serial", "serial"], serial, False)
        with logger.contextualize(current = current, serial = serial):
            logger.info(f"Dup/Mig search returned: {len(search_duplicates)}")
        
        # If there are no duplicates, return the asset if from the new table.
        # If from the old table, send it on to be migrated.
        if len(search_duplicates) == 1:
            with logger.contextualize(search_duplicates_count = len(search_duplicates)):
                logger.info(f"Dup/Mig Search Result: {vars(search_duplicates[0])}")
            if current:
                return search_duplicates[0]
            else:
                self._migrate_asset(search_duplicates[0])
        
        # If no asset is returned at all (i.e., the serial number is missing)
        #   return or migrate the original asset.
        elif len(search_duplicates) == 0:
            with logger.contextualize(search_duplicates_count = len(search_duplicates)):
                logger.info(f"Dup/Mig Empty: {vars(asset_object)}")
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
            self.clear_screen()
            while True:
                select_duplicate = None
                print(f"==[ Mark Duplicates ]{'=' * (self._terminal_width - 21)}")
                if len(output_list) == 1:
                    select_duplicate = "1"
                else:
                    for entry in output_list:
                        device_fields = self._set_device_fields(entry)
                        print()
                        option_number += 1
                        print(f"Option {option_number})\n")
                        entry.output(False, device_fields)
                        print("-" * self._terminal_width)
                
                # Get user input on which asset to keep.
                if not select_duplicate:
                    select_duplicate = self.menu_input("Select duplicate to keep: ",[str(i) for i in range(1, len(output_list) + 1)] + ["B","M","X"], True)
                if select_duplicate.upper() == "B":
                    self.clear_screen()
                    break
                # Set any other duplicates to be marked as duplicate.
                else:
                    with logger.contextualize(select_duplicate = select_duplicate, migrated = migrated, migrated_count = len(migrated_ouput)):
                        logger.info(f"Mig/Dup Select Duplicate: {vars(search_duplicates[int(select_duplicate) - 1])}")
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
                        logger.error(f"Mig/Dup New Table Duplicate: {asset.asset_number}, {asset.serial}")
                        if not duplicate_message:
                            duplicate_message = True
                            self.clear_screen()
                            print(f"==[ Mark Duplicates ]{'=' * (self._terminal_width - 21)}")
                            print(f"{'!' * self._terminal_width}")
                            print("Please send a message to the IT department with the following information.")
                            print("Copy / Paste if possible.\n\n")
                            print("Duplicate(s) detected in the new IT Assets table:\n")
                        print(f"Asset Number: {asset.asset_number}")
                        print(f"Serial Number: {asset.serial}")
                        print("-" * self._terminal_width)
                if duplicate_message:
                    print(f"\n{'!' * self._terminal_width}")
                    input("Press enter to continue.")
                
                # If selected asset is from old table, send it to be migrated.
                #  Otherwise, return it.
                with logger.contextualize(duplicate_message = duplicate_message):
                    logger.info(f"Mig/Dup Duplicate Count: {len(duplicate_list)}")
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
        
        logger.info(f"Migrate Asset Start: {vars(old_asset)}")
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
        
        if unconvertable_datatype:
            self.clear_screen()
            print("The following information will be lost, please take note:\n")
            for field, entry in unconvertable_datatype.items():
                print(f"{field.capitalize()}: {entry}")
            input("\nPress enter to continue.")
        
        asset_id = self._edit_screen(maria.new_object(new_setup), False)
        with logger.contextualize(unconvertable_datatype = unconvertable_datatype):
            logger.info(f"Migrate Asset New Asset: {asset_id}: {new_setup}")
        if asset_id:
            old_asset.is_migrated = 1
            logger.info(f"Old Asset {old_asset.Asset} Migrated: {old_asset.is_migrated}")
            maria.save_object(old_asset)
            
            self.clear_screen()
            print(f"==[ MIGRATING ASSET ]{'=' * (self._terminal_width - 21)}\n")
            print(f"Asset {old_asset.Asset} has been migrated from {old_asset.table}.")
            print("Please take note of the new Asset ID below.\n")
            print(f"Asset ID: {asset_id}\n")
            input("Press enter to continue.")
            self.clear_screen()
        else:
            self.clear_screen()
            print(f"Migration of asset {old_asset.Asset} has been cancelled.\n")
            input("Press enter to continue.")
            
        self.asset_edit()
    
    
    def _set_device_fields(self, asset: Union[object, str]):
        fields_dictionary = {}
        control_fields = ("device_type", "status", "entity", "building", "manufacturer", "operating_system")
        display_fields = []
        
        if asset not in control_fields:
            fields_dictionary["Common"] = maria.field_control["Common"]
        if isinstance(asset, str):
            asset_type = asset
        elif isinstance(asset, object) and hasattr(asset, "table") and asset.table == "IT_Assets":
            asset_type = asset.device_type
        else:
            return None
        fields_dictionary[asset_type] = maria.field_control[asset_type]
        
        if asset in control_fields:
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
            locked_fields = ["asset_number", "serial", "last_seen"]
            fixed_list_fields = ("device_type", "status", "entity", "building", "manufacturer", "operating_system")
            required_fields = ["device_type", "manufacturer", "model", "entity", "building", "department", "status"]
            date_fields = ("deployment_date", "purchase_date", "contract_expiration_date", "last_seen")
            float_fields = ("purchase_price","contract_amount")
            int_fields = ()
            list_fields = ("asset_reference", "notes")
            option_number = 0
            
            self.clear_screen()
            # with logger.contextualize(short = short):
            #     logger.info(f"Edit Screen Start")
            if not hasattr(asset, "serial") or not getattr(asset, "serial", ""):
                logger.info("Edit Screen: No Serial")
                locked_fields.remove("serial")
                required_fields.append("serial")
            
            if asset.column == "new":
                print(f"==[ NEW ASSET ]{'=' * (self._terminal_width - 15)}\n")
                ignore_keys.append("asset_number")
                required_fields.remove("device_type")
                locked_fields.append("device_type")
            elif asset.column == "migrate":
                print(f"==[ MIGRATING ASSET ]{'=' * (self._terminal_width - 21)}\n")
                ignore_keys.append("asset_number")
            else:
                print(f"==[ EDIT ASSET ]{'=' * (self._terminal_width - 16)}\n")
                
            output_dictionary = vars(asset)
            device_fields = self._set_device_fields(asset)
            
            if "ip_address" in device_fields:
                required_fields.append("ip_address")
            
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
                        print(f"{option_number})  {key.capitalize()}: {'_' * 5} {postfix}")
                    fields.append(key)
            print("-" * self._terminal_width)
            
            if short:
                break
            
            print("S: Save changes to database.")
            select_field = self.menu_input("Enter command or select field to edit: ", [str(i) for i in range(1, len(fields) + 1)] + ["B", "S"], True)
            logger.info(f"Edit Screen Select Field: {select_field}")
            if select_field.upper() == "B":
                if self._confirm_exit():
                    break
                else:
                    continue
            elif select_field.upper() == "S":
                saved_asset = self._edit_save(asset, required_fields)
                if saved_asset:
                    return saved_asset
                else:
                    input("Nothing has been changed in the database. Press enter to continue.")
            else:
                logger.info(f"Edit Screen Select Field: {fields[int(select_field) - 1]}")
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
                elif fields[int(select_field) - 1] in fixed_list_fields:
                    self._edit_fixed_list(fields[int(select_field) - 1], asset)
                else:
                    self._edit_field(asset, fields[int(select_field) - 1])
    
    
    def _confirm_exit(self):
        self.clear_screen()
        print("All unsaved changes will be lost.")
        print("Are you sure you want to exit?\n")
        
        print("1)  Yes")
        print("2)  No")
        
        options = ["1", "YES", "Y", "2", "NO", "N"]
        select_option = self.menu_input("\nEnter selection: ", options, True)
        
        if select_option.upper() in ["1", "YES", "Y"]:
            return True
        else:
            return False


    def _edit_date_field(self, editing_asset: object, attribute):
        sql_date = str(getattr(editing_asset, attribute))
        
        if sql_date is None or sql_date == "None" or sql_date == "":
            display_date = "empty"
        else:
            display_date = self._convert_date(sql_date)
        
        self._edit_screen(editing_asset, True)
        print("B: Go back to previous screen.\n")
        print(f"{attribute.capitalize().replace('_', ' ')} current date: {display_date}\n")
        
        while True:
            print("Warning: Current date will be overwritten")
            new_date = self.menu_input("Enter new date (MM/DD/YYYY): ")
            with logger.contextualize(attribute=attribute, sql_date = sql_date):
                logger.info(f"Edit Date New Date: {new_date}")
            if new_date.upper() == "B":
                logger.info("Edit Date Back Command")
                break
            else:
                valid_date = self._convert_date(new_date)
                if not valid_date:
                    logger.error("Edit Date Invalid Date")
                    print("\nInvalid date format, please try again.")
                    continue
                else:
                    setattr(editing_asset, attribute, valid_date)
                    with logger.contextualize(editing_asset = vars(editing_asset)):
                        logger.info("Edit Date Set")
                    break
    
    
    def _convert_date(self, date: str):
        try:
            date_object = datetime.strptime(date, "%Y-%m-%d")
            formatted_date = date_object.strftime("%m/%d/%Y")
            return formatted_date
        except ValueError:
            pass
        try:
            date_object = datetime.strptime(date, "%m/%d/%Y")
            formatted_date = date_object.strftime("%Y-%m-%d")
            return formatted_date
        except ValueError:
            pass
        try:
            date_object = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            formatted_date = date_object.strftime("%m/%d/%Y %H:%M:%S")
            return formatted_date
        except ValueError:
            pass
        try:
            date_object = datetime.strptime(date, "%m/%d/%Y %H:%M:%S")
            formatted_date = date_object.strftime("%Y-%m-%d %H:%M:%S")
            return formatted_date
        except ValueError:
            return None
    
    
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
                select_entry = self.menu_input("Enter command or select entry to add or edit: ", [str(i) for i in range(1, len(entries_list) + 2)] + ["B"], True)
                with logger.contextualize(attribute = attribute):
                    logger.info(f"Edit List Select Entry: {select_entry}")
                if select_entry.upper() == "B":
                    logger.info("Edit List Select Entry Back")
                    go_back = True
                    break
                self._output_list_entries(editing_asset, attribute, entries_list)
                
                if int(select_entry) == (len(entries_list) + 1):
                    logger.info("Edit List New Entry")
                    print("B: Go back to previous screen.\n")
                    print("New entry\n")
                else:
                    logger.info(f"Edit List Current Entry: {entries_list[int(select_entry) - 1]}")
                    print("B: Go back to previous screen.    D: Delete this entry\n")
                    print(f"Current entry: {entries_list[int(select_entry) - 1].replace('_', ' ')}\n")
                    print("Warning: Current entry will be overwritten")
                    
                list_prompt = f"Enter command or new {attribute[:-1].replace('_', ' ') if attribute.endswith('s') else attribute.replace('_', ' ')}: "
                edit_entry = self.menu_input(list_prompt)
                with logger.contextualize(current_entry = entries_list[int(select_entry) - 1] if len(entries_list) > int(select_entry) - 1 else "Empty"):
                    logger.info(f"Edit Notes Edit Entry: {edit_entry}")
                if edit_entry.upper() == "B":
                    logger.info("Edit List Edit Entry Back")
                    break
                elif edit_entry.upper() == "D":
                    logger.info("Edit List Edit Entry Delete")
                    if len(entries_list) == 0:
                        logger.info("Edit List Nothing To Delete")
                        break
                    else:
                        try:
                            entries_list.pop(int(select_entry) - 1)
                            logger.info(f"Edit List Delete {(int(select_entry))}")
                        except IndexError:
                            logger.info(f"Delete Empty Index {(int(select_entry))}")
                            break
                else:
                    if int(select_entry) == (len(entries_list) + 1):
                        if len(" --- ".join(entries_list)) + len(edit_entry) >= 225:
                            logger.error("Edit List: Notes string is too long.")
                            print("There are too many notes, please edit or delete existing notes.")
                            input("Press enter to continue.")
                            break
                        entries_list.append(edit_entry)
                    else:
                        entries_list[int(select_entry) - 1] = edit_entry
                setattr(editing_asset, attribute, (" --- ".join(entries_list)))
                with logger.contextualize(editing_asset = vars(editing_asset)):
                        logger.info("Edit Entry Set")
                break


    def _output_list_entries(self, asset: object, display_attribute, entries: list):
        option_number = 0
        
        self._edit_screen(asset, True)
        print(f"{display_attribute.capitalize().replace('_', ' ')} current entries:\n")
        
        for entry in entries:
            option_number += 1
            print(f"{option_number})  {entry}")
        option_number += 1
        print(f"{option_number})  <Add new entry>")
        print("-" * self._terminal_width)
    
    
    def _edit_fixed_list(self, asset_field: str, editing_asset: object = None):
        restricted = ("device_type", "status")
        options = self._set_device_fields(asset_field)
        
        while True:
            if editing_asset:
                self._edit_screen(editing_asset, True)
            else:
                self.clear_screen()
                if asset_field == "device_type":
                    print(f"==[ DEVICE TYPE ]{'=' * (self._terminal_width - 17)}\n")
                else:
                    print(f"==[ DEVICE STATUS ]{'=' * (self._terminal_width - 19)}\n")
            
            if asset_field in restricted:
                option_prompt = f"Select {asset_field.replace('_', ' ')}: "
                option_list_set = None
                restrict_selection = True
            else:
                option_prompt = f"Enter or select {asset_field.replace('_', ' ')}: "
                option_list_set = "n/a"
                restrict_selection = False
            
            if editing_asset:
                if getattr(editing_asset, asset_field) is not None:
                    print(f"{asset_field.capitalize().replace('_', ' ')} current setting: {getattr(editing_asset, asset_field)}\n")
                else:
                    print(f"{asset_field.capitalize().replace('_', ' ')} has not been set.\n")
            option_number = 0
            for items in options:
                option_number += 1
                print(f"{option_number})  {items}")
            option_list = [str(i) for i in range(1, len(options) + 1)]
            option_list.append("B")
            if not option_list_set:
                option_list_set = option_list
            print("-" * self._terminal_width)
            select_option = self.menu_input(option_prompt, option_list, restrict_selection)
            with logger.contextualize(asset_field = asset_field):
                logger.info(f"Edit Fixed List Select Option: {select_option}")
                
            if select_option.upper() == "B":
                logger.info("Edit Fixed List Back")
                self.clear_screen()
                break
            elif editing_asset and select_option not in option_list and asset_field not in restricted:
                setattr(editing_asset, asset_field, select_option)
                with logger.contextualize(editing_asset = vars(editing_asset)):
                    logger.info("Edit Fixed List Set")
                break
            else:
                logger.info(f"Edit Fixed List Select Option: {options[int(select_option) - 1]}")
                if editing_asset:
                    setattr(editing_asset, asset_field, options[int(select_option) - 1])
                    with logger.contextualize(editing_asset = vars(editing_asset)):
                        logger.info("Edit Fixed List Set")
                    break
                else:
                    logger.info("Edit Fixed List Return")
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
        print("B: Go back to previous screen.\n")
        print(f"Current {attribute.capitalize().replace('_', ' ')}: {sql_number}\n")
        
        while True:
            print("Warning: Current entry will be overwritten")
            new_number = self.menu_input(f"Enter new {attribute.replace('_', ' ')}: ")
            with logger.contextualize(attribute = attribute,sql_number = sql_number, data_type = data_type):
                logger.info(f"Edit Number: {new_number}")
            if new_number.upper() == "B":
                logger.info("Edit Number Back Command")
                break
            try:
                new_number = float(new_number)
            except ValueError as error:
                logger.error(f"Edit Number Error: {error}")
                print("Invalid input, please try again.\n")
                continue
            if data_type is float:
                new_number = float(format(new_number, ".2f"))
            else:
                new_number = int(new_number)
            setattr(editing_asset, attribute, new_number)
            with logger.contextualize(editing_asset = vars(editing_asset)):
                logger.info(f"Edit Number Set ({type(new_number)})")
            break
        
    
    def _edit_field(self, editing_asset: object, attribute):
        sql_data = getattr(editing_asset, attribute)
        if sql_data is None or sql_data == "None" or sql_data == "":
            sql_data = "empty"
        self._edit_screen(editing_asset, True)
        print("B: Go back to previous screen.\n")
        print(f"{attribute.capitalize().replace('_', ' ')} current entry: {sql_data}\n")
        
        while True:
            print("Warning: Current entry will be overwritten")
            new_data = self.menu_input(f"Enter new {attribute.replace('_', ' ')}: ")
            with logger.contextualize(attribute = attribute, sql_data = sql_data):
                logger.info(f"Edit Field New Data: {new_data}")
            if new_data.upper() == "B":
                logger.info("Edit Field Back Command.")
                break
            elif len(new_data) >= 255:
                print("Entry is too long, please shorten to under 255 characters.")
                logger.error("Edit Field: Entry is too long.")
                continue
            else:
                setattr(editing_asset, attribute, new_data)
                with logger.contextualize(editing_asset = vars(editing_asset)):
                    logger.info("Edit Field Set")
                break
    
    
    def _edit_locked_field(self, editing_asset: object, attribute):
        logger.info(f"Edit Locked: {attribute}")
        self._edit_screen(editing_asset, True)
        if attribute == "last_seen":
            print('This will update when using the "S" command.')
            input("Press enter to continue.")
        elif editing_asset.column == "new":
            print(f"{attribute.capitalize().replace('_', ' ')} cannot be edited from this screen.")
            print('Please use the "B" command and reenter the correct serial and device type.')
            input("Press enter to continue.")
        else:
            print(f"{attribute.capitalize().replace('_', ' ')} is not editable, please contact an admin to fix.")
            input("Press enter to continue.")
    
    
    def _edit_save(self, editing_asset: object, check_fields: list):
        missing_fields = []
        
        logger.info(f"Save Asset: {vars(editing_asset)}")
        for field in check_fields:
            if not getattr(editing_asset, field):
                missing_fields.append(field.capitalize())
        if missing_fields:
            logger.info(f"Save Asset Missing Fields: {missing_fields}")
            self._edit_screen(editing_asset, True)
            print("The following fields are required and have not been filled in. Please complete and save again.")
            print(", ".join(missing_fields))
            print()
        else:
            current_date = datetime.now()
            editing_asset.last_seen = current_date
            return maria.save_object(editing_asset)
    
    
    def exit_program(self):
        self.clear_screen()
        maria.close_connection()
        print("\nGoodbye!\n")
        logger.info("-----Ending session.-----")
        exit()
    
    
    def menu_input(self, prompt: str, options_list: list = None, restricted = False):
        command_dictionary = {
            "C": "Clear the screen.",
            "B": "Go back to previous screen.",
            "M": "Go back to main menu.",
            "X": "Exit the program.",
        }
        command_options = []
        
        if options_list:
            for option in options_list:
                if option in command_dictionary.keys():
                    command_options.append(option)
        
        if command_options:
            print("Command Options:")
            current_line = ""
            for command in command_options:
                command_string = f"{command}: {command_dictionary[command]}  "
                if len(current_line) + len(command_string) <= self._terminal_width:
                    current_line += command_string
                else:
                    print(current_line)
                    current_line = command_string
            print(f"{current_line}\n")
        
        while True:
            user_input = input(prompt).strip()
            
            if os.name == "posix":
                import termios
                termios.tcflush(sys.stdin, termios.TCIOFLUSH)
            else:
                import msvcrt
                while msvcrt.kbhit():
                    msvcrt.getch()
            
            if not user_input or (restricted and user_input.upper() not in options_list):
                print("Invalid input, please try again.")
                continue
            elif options_list and user_input.upper() in options_list:
                if user_input.upper() == "C":
                    self.clear_screen()
                    break
                elif user_input.upper() == "M":
                    self.main_menu()
                elif user_input.upper() == "X":
                    self.exit_program()
                else:
                    return user_input
            else:
                return user_input
            
    
    def clear_screen(self):
        if os.name == "posix":
            os.system("clear")
        else:
            os.system("cls")
            
            


if __name__ == "__main__":
    logger.remove(0)
    logger.add("debug.log", format="{time:MMMM D, YYYY > HH:mm:ss} | {level} | {message} | {extra}")
    logger = logger.bind(session_id = os.getpid())
    with logger.contextualize(width = os.get_terminal_size().columns):
        logger.info("-----Starting session.-----")
    
    # This section being uncommented moves crashes to log file.
    with logger.catch():
        maria = database.DatabaseManager()
        if maria.connection:
            start = CommandClass()
        else:
            logger.critical(maria.fail_error)
            input("Critical Error!: Press enter to terminate.")
            
    # This section being uncommented moves crashes to terminal
    # maria = database.DatabaseManager()
    # start = CommandClass()