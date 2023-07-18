"""This module provides various menus and menu operations."""

# TODO Remove notes print from SW and TC.
# TODO Replace tuple arguments with list arguments.
# TODO Review all MenuFunction uses to minimize arguments if they are not needed.

# Standard library imports.
from datetime import datetime
import os

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
            
            main_menu_select = MenuFunction(self, "n/a", "Enter menu option: ", list(self._menu_options.keys()), ["n/a"])
            menu_action = self._menu_options.get(main_menu_select.menu_input)
            menu_action()
    

    def asset_search(self, type_search: str = "basic", output_full: bool = False, search_fields: list = [], search_term: str = None):
        option_number = 0
        
        if type_search == "basic":
            Utility.clear_screen()
        while True:
            migrated_count = 0
            duplicate_count = 0
            result_list = []
            
            # Set up menu and intial search prompt.
            if search_term:
                search_prompt = None
            elif type_search == "edit":
                search_prompt = "Search for asset to edit: "
            else:
                print(f"==[ BASIC SEARCH ]{'=' * (os.get_terminal_size().columns - 18)}")
                search_prompt = "Search for asset: "
                
            # Search for asset.
            if search_term:
                asset_search_term = search_term
            else:
                asset_search_term = MenuFunction(self, self.main_menu, search_prompt, ["n/a"], ["all"]).menu_input
            if asset_search_term is None:
                if type_search == "edit":
                    self.asset_edit()
                else:
                    continue
            else:
                if search_fields:
                    asset_search_results = maria.search_tables(asset_search_term, search_fields)
                else:
                    asset_search_results = maria.search_tables(asset_search_term)
            
            # Set up output of search results.
            for result in asset_search_results:
                if result.table != "IT_Assets" and result.is_migrated == 1:
                    migrated_count += 1
                elif result.table != "IT_Assets" and result.is_duplicate == 1:
                    duplicate_count += 1
                else:
                    result_list.append(result)
                    
            # Output search results.
            for entry in result_list:
                print()
                if type_search == "edit" and len(result_list) >= 2:
                    option_number += 1
                    print(f"Option {option_number})\n")
                if type_search != "edit" or (type_search == "edit" and len(result_list) >= 2):
                    if output_full:
                        entry.output(False)
                    else:
                        entry.output()
                    print(self.SEPARATOR)
            
            # Print results summary. If applicable, return results.
            if type_search != "edit":
                if migrated_count or duplicate_count:
                    print(f"Showing {len(result_list)} of {len(asset_search_results)} result{'' if (asset_search_results) == 1 else 's'}.")
                else:
                    print(f"Found {len(result_list)} result{'' if (asset_search_results) == 1 else 's'}.")
                if migrated_count:
                    print(f"{migrated_count} entr{'y' if duplicate_count == 1 else 'ies'} marked migrated hidden.")
                if duplicate_count:
                    print(f"{duplicate_count} entr{'y' if duplicate_count == 1 else 'ies'} marked duplicate hidden.")
                print()
            else:
                return result_list


    def asset_edit(self):
        Utility.clear_screen()
        while True:
            print(f"==[ EDIT ASSET ]{'=' * (os.get_terminal_size().columns - 16)}")
            search_asset = self.asset_search("edit")
            if search_asset is None:
                continue
            elif len(search_asset) == 1:
                select_asset = "1"
            else:
                asset_options = []
                for i in range(1, (len(search_asset) + 1)):
                    asset_options.append(str(i))
                select_asset = MenuFunction(self, self.asset_edit, "Select asset to edit: ", asset_options).menu_input
                if select_asset is None:
                    continue
            self._edit_screen(self._process_duplicates(search_asset[int(select_asset) - 1]))      # Currently only works on single entry item: bb002
            
            
    def _edit_screen(self, asset: object, stop: bool = False):
        while True:
            fields = []
            field_options = []
            ignore_keys = ("last_seen", "is_verified", "table", "column")
            date_fields = ("deployment_date", "purchase_date", "contract_expiration_date", "last_seen")
            float_fields = ("purchase_price","contract_amount")
            list_fields = ("asset_reference", "notes")
            int_fields = ("asset_number",)
            
            Utility.clear_screen()
            print(f"==[ EDIT ASSET ]{'=' * (os.get_terminal_size().columns - 16)}\n")
            output_dictionary = vars(asset)
            items = list(output_dictionary.items())
            for index, (key, value) in enumerate(items):
                if key not in ignore_keys:
                    if key in date_fields:
                        value = self._convert_date(str(value))
                    print(f"{index + 1})  {key}: {value if value is not None else ('_' * 10)}")
                    fields.append(key)
            print(self.SEPARATOR)
            
            if stop:
                break
            
            for i in range(1, (len(fields) + 1)):
                field_options.append(str(i))
            field_options.append("save")
            
            print("save: Save changes to database.")
            print("WARNING: The below commands will discard any changes!")
            select_field = MenuFunction(self, self.asset_edit, "Enter command or select field to edit: ", field_options, ["back", "cancel", "quit"]).menu_input
            
            if select_field is None:
                continue
            elif select_field == "save":
                input("saving... not")                              #//////////////////////
            else:
                if fields[int(select_field) - 1] in date_fields:
                    self._edit_date_field(asset, fields[int(select_field) - 1])


    def _edit_date_field(self, editing_asset: object, attribute):
        sql_date = str(getattr(editing_asset, attribute))
        display_date = self._convert_date(sql_date)
        
        self._edit_screen(editing_asset, True)
        print("back: Cancel changes.\n")
        print(f"{attribute} current date:  {display_date}\n")
        
        while True:
            new_date = MenuFunction(self, self._edit_screen, "Enter new date (MM/DD/YYYY): ", ["n/a"], ["n/a"]).menu_input
            if new_date is None:
                continue
            elif new_date == "back":
                self._edit_screen(editing_asset)
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
        
        
        
    
    
    def _edit_list_field(self, attribute):
        pass
    
    
    def _edit_field(self, attribute):
        pass
    
    
    def _save_asset(self, asset: object):
        pass
        


    
    
    def _process_duplicates(self, asset_object: object):
        if asset_object.table == "IT_Assets":
            serial = asset_object.serial
        else:
            serial = asset_object.Serial
        search_duplicates = self.asset_search("edit", True, ["Serial", "serial"], serial)
        if len(search_duplicates) == 1:
            return asset_object
        else:
            duplicate_options = []
            for i in range(1, (len(search_duplicates) + 1)):
                duplicate_options.append(str(i))
            select_duplicate = MenuFunction(self, self.asset_edit, "Select duplicate to keep: ", duplicate_options).menu_input
        

            
    
    
    def quit_program(self):
        Utility.clear_screen()
        maria.close_connection()
        print("\nGoodbye!\n")
        exit()


class MenuFunction:
    """Provides menu and input functionality."""
    
    def __init__(self: object, calling_class, back_to: str = "n/a", prompt: str = "Enter option: ", menu_options: list = ["n/a"], command_options: list = ["all"], search_term: str = None):
        """Instatiates menu input class."""
        
        # Class variable(s) used to indicate where "cancel" and "back" should go.
        self._calling_class = calling_class
        self._back_to = back_to
        
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