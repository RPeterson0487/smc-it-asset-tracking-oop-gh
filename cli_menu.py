"""This module provides various menus and menu operations."""

# TODO Remove notes print from SW and TC

# Standard library imports.
import os

# Third party imports.

# Local application/library specific imports.
import database_manager as database


class MenuScreens:
    """Initializes Main Menu and runs program."""

    def __init__(self):
        """Displays the main menu and asks for input."""
        
        # Menu options that call methods when selected.
        self._menu_options = {
            "1": self.asset_search,
            "2": self.asset_edit,
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
            print("0)  Quit program\n")
            
            main_menu_select = MenuFunction(self, "n/a", "Enter menu option: ", tuple(self._menu_options.keys()), ("n/a",))
            menu_action = self._menu_options.get(main_menu_select.menu_input)
            menu_action()
    

    def asset_search(self):
        Utility.clear_screen()
        while True:
            migrated_count = 0
            duplicate_count = 0
            result_list = []
            
            print(f"==[ BASIC SEARCH ]{'=' * (os.get_terminal_size().columns - 18)}")
            asset_search_term = MenuFunction(self, self.main_menu, "Search for asset: ", ("n/a",), ("all",))
            if asset_search_term.menu_input is None:
                continue
            else:
                asset_search_results = maria.search_tables(asset_search_term.menu_input)
            
            for result in asset_search_results:
                if result.table != "IT_Assets" and result.is_migrated == 1:
                    migrated_count += 1
                elif result.table != "IT_Assets" and result.is_duplicate == 1:
                    duplicate_count += 1
                else:
                    result_list.append(result)
                    
            for entry in result_list:
                print()
                entry.output()
                
                
            
            # print(f"==[ BASIC SEARCH ]{'=' * (os.get_terminal_size().columns - 18)}")
            # asset_search_term = MenuFunction(self, self.main_menu, "Search for asset: ", ("n/a",), ("all",))
            # if asset_search_term.menu_input is None:
            #     continue
            # else:
            #     asset_search_results = maria.search_tables(asset_search_term.menu_input)
            
            # for result in asset_search_results:
            #     if result["table"] != "IT_Assets" and result["is_migrated"] == 1:
            #         migrated_count += 1
                # elif result["table"] != "IT_Assets" and result["is_duplicate"] == 1:
                #     duplicate_count += 1
            #     else:
            #         result_list.append(result)
                
            # for entry in result_list:
            #     print()
            #     Utility.output_limited(entry)
            #     print("-" * os.get_terminal_size().columns)
            # if migrated_count or duplicate_count:
            #     print(f"Showing {len(result_list)} of {len(asset_search_results)} result{'' if (asset_search_results) == 1 else 's'}.")
            # else:
            #     print(f"Found {len(result_list)} result{'' if (asset_search_results) == 1 else 's'}.")
            # if migrated_count:
            #     print(f"{migrated_count} entr{'y' if duplicate_count == 1 else 'ies'} marked migrated hidden.")
            # if duplicate_count:
            #     print(f"{duplicate_count} entr{'y' if duplicate_count == 1 else 'ies'} marked duplicate hidden.")
            # print()


    def asset_edit(self):
        print("Function asset_edit")                #//////////////////////////////////////////
    
    
    def quit_program(self):
        Utility.clear_screen()
        maria.close_connection()
        print("\nGoodbye!\n")
        exit()


class MenuFunction:
    """Provides menu and input functionality."""
    
    def __init__(self, calling_class, back_to: str = "n/a", prompt: str = "Enter option: ", menu_options: tuple = ("n/a",), command_options: tuple = ("all",)):
        """Instatiates menu input class."""
        
        # Class variable(s) used to indicate where "cancel" and "back" should go.
        self._calling_class = calling_class
        self._back_to = back_to
        
        # Class variable(s) used to display the input prompt.
        self._prompt = prompt
        
        # Class variable(s) used for the calling menu.
        self._menu_options = menu_options
        self.menu_input = None
        
        # Class variable(s) used to display the list of commands (i.e. "back").
        self._command_options = [(command.lower()) for command in command_options]
        self._command_list = []
        self._command_print_dict = {
            "clear": ": Clear the screen.",
            "back": ": Go back to previous screen.",
            "cancel": ": Go back to main menu.",
            "quit": ": Disconnect from database and quit the program.",
        }
        
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
            if "main" in self._command_options:
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
    
    
    def output_full(asset_dictionary: dict):
        for key in asset_dictionary:
            if key not in ("table", "column", "is_verified",):
                print(f"{key}: {asset_dictionary[key]}")
    
    
    def output_limited(asset_dictionary: dict):
        if asset_dictionary["table"] == "IT_Assets":
            current = True
        else:
            current = False
        
        print(f"Serial Number: {Utility._check_result_value(asset_dictionary.get(('serial' if current else 'Serial'), 'key missing'))}")
        if current:
            print(f"Device Type: {Utility._check_result_value(asset_dictionary.get('device_type', 'key missing'))}")
        print(f"Model: {Utility._check_result_value(asset_dictionary.get(('model' if current else 'Model'), 'key missing'))}")
        print(f"Asset Number: {Utility._check_result_value(asset_dictionary.get(('asset_number' if current else 'Asset'), 'key missing'))}")
        if current and asset_dictionary["device_type"] == "Fork Truck":
            print(f"Fork Truck: {Utility._check_result_value(asset_dictionary.get('fork_truck_number', 'key missing'))}")
        elif not current and asset_dictionary["table"] == "IT_Assets_FT":
            print(f"Fork Truck: {Utility._check_result_value(asset_dictionary.get('Fork_Truck_No', 'key missing'))}")
        if asset_dictionary["table"] != "IT_Assets_SG":
            print(f"IP Address: {Utility._check_result_value(asset_dictionary.get(('ip_address' if current else 'Ip_Address'), 'key missing'))}")
        print(f"Notes: {Utility._check_result_value(asset_dictionary.get(('notes' if current else 'Current_User'), 'key missing'))}")
        print(f"Found in table {asset_dictionary['table']} under {asset_dictionary['column']} as {asset_dictionary.get(asset_dictionary['column'], 'Error')}.")
        if not current:
            print("Migration Status: This device has not yet been migrated to the new tracking table.")
    
    
    def _check_result_value(value):
        if value == "key missing":
            return "!!!!!key missing!!!!!"                              # ////////////////
        elif value == "" or value is None:
            return "!!!!!BLANKETY BLANK!!!!!"                           # ////////////////
        else:
            return str(value)


if __name__ == "__main__":
    maria = database.DatabaseManager()
    start = MenuScreens()