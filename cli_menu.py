"""This module provides various menus and menu operations."""

# TODO Freeze all but regular assets table and walk through code with bb002 to figure out why results are empty

# Standard library imports.
import os

# Third party imports.

# Local application/library specific imports.
import database_manager as database


class MainMenu:
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
        self._main_menu()


    def _main_menu(self):
        """Display the main menu and wait for user input."""
        
        Utility.clear_screen()
        while True:
            
            print(f"""
==[ MAIN MENU ]{'=' * (os.get_terminal_size().columns - 15)}

1)  Search for asset
2)  Edit existing asset
0)  Quit program
        """)
            
            main_menu_select = MenuFunction("n/a", "Select menu option: ", tuple(self._menu_options.keys()), "n/a") #//////////////////////////////////////////
            menu_action = self._menu_options.get(main_menu_select.menu_input)
            menu_action()
    

    def asset_search(self):
        Utility.clear_screen()
        asset_search_term = MenuFunction("n/a", "Enter search term: ", ("n/a",), ("all",))
        asset_search_results = maria.search_tables(asset_search_term.menu_input)
        
        for result in asset_search_results:         #//////////////////////////////////////////
            Utility.output_limited(result)
            print()


    def asset_edit(self):
        print("Function asset_edit")                #//////////////////////////////////////////
    
    
    def quit_program(self):
        print("Function quit_program")              #//////////////////////////////////////////


class MenuFunction:
    """Provides menu and input functionality."""
    
    def __init__(self, back_to: str = "n/a", prompt: str = "Enter option: ", menu_options: tuple = ("n/a",), command_options: tuple = ("all",)):
        """Instatiates menu input class."""
        
        # Class variable(s) used to indicate where "back" should go.
        self._back_to = back_to.lower()
        
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
            if "cancel" in self._command_options:
                self._command_list.append("cancel")
            if "quit" in self._command_options:
                self._command_list.append("quit")
        
        for command in self._command_list:
            print(f"{command}{self._command_print_dict[command]}", end = "    ")
        print()
    
    
    def _get_user_input(self):
        while True:
            user_input = input(self._prompt)
            
            if user_input.lower() in self._command_list:
                if user_input.lower() == "clear":
                    print("input clear")                    #///////////////////////////
                elif user_input.lower() == "back":
                    print("input back")                     #///////////////////////////
                elif user_input.lower() == "cancel":
                    print("input cancel")                   #///////////////////////////
                elif user_input.lower() == "quit":
                    print("input quit")                     #///////////////////////////
            elif not user_input or (user_input not in self._menu_options and "n/a" not in self._menu_options):
                print("Not a valid entry, please try again.")
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
        print(f"IP Address: {Utility._check_result_value(asset_dictionary.get(('ip_address' if current else 'Ip_Address'), 'key missing'))}")
        print(f"Notes: {Utility._check_result_value(asset_dictionary.get(('notes' if current else 'Current_User'), 'key missing'))}")
        print(f"Found in table {asset_dictionary['table']} under {asset_dictionary['column']} as {asset_dictionary.get(asset_dictionary['column'], 'Error')}.")
        if not current:
            print("Migration Status: This device has not yet been migrated to the new tracking table.")
    
    
    def _check_result_value(value):
        if value == "key missing":
            return "!!!!!key missing!!!!!"
        elif value == "" or value is None:
            return "!!!!!BLANKETY BLANK!!!!!"
        else:
            return str(value)


if __name__ == "__main__":
    maria = database.DatabaseManager()
    start = MainMenu()