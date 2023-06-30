"""This module provides various menus and menu operations."""

# TODO Figure out how to validate user input against menu, probably pass acceptable options range.

# Standard library imports.
import os

# Third party imports.

# Local application/library specific imports.


class MainMenu:
    """Initializes main menu object."""

    def __init__(self):
        """Displays the main menu and asks for input."""
        
        # self._menu_options = {
        #     "1": self.asset_search,
        #     "2": self.asset_edit,
        #     "0": self.quit_program,
        # }
        
        
        self._loop_main_menu() #//////////////////////////////////////////
    
    
    def _display_main_menu(self):
        print(f"""
==[ MAIN MENU ]{'=' * (os.get_terminal_size().columns - 15)}

1)  Search for asset
2)  Edit existing asset
0)  Quit program
        """)
    
    
    def _loop_main_menu(self):
        """Display the main menu and wait for user input."""
        
        while True:
            self._display_main_menu()
            _main_menu_select = MenuInput("Testing this out: ", "nowhere", ("back", "clear"))
            print(_main_menu_select.menu_input) #//////////////////////////
            break #/////////////////////////








class MenuInput:
    """User input class."""
    
    def __init__(self, prompt: str = "Enter option: ", back_to: str = "nowhere", command_options: tuple = ("all",)):
        """Instatiates menu input class."""
        
        # Command list class variables for use by MenuInput class.
        self._prompt = prompt
        self._back_to = back_to.lower()
        self._command_options = [(command.lower()) for command in command_options]
        self._command_list = []
        self._command_print_dict = {
            "clear": ": Clear the screen.",
            "back": ": Go back to previous screen.",
            "cancel": ": Go back to main menu.",
            "quit": ": Disconnect from database and quit the program.",
        }
        
        # User input variables to be used by calling menu.
        self.menu_input = None
        
        # List available commands before user input.
        self._list_commands()
        # Get user input to be used in the calling menu.
        self._get_user_input()


    def _list_commands(self):
        """List commands that can be used from input."""
        
        if "all" in self._command_options:
            self._command_list.extend(["clear", "back", "cancel", "quit"])
        elif ("none" in self._command_options):
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
                    print("input clear") #///////////////////////////
                elif user_input.lower() == "back":
                    print("input back") #///////////////////////////
                elif user_input.lower() == "cancel":
                    print("input cancel") #///////////////////////////
                elif user_input.lower() == "quit":
                    print("input quit") #///////////////////////////
            elif not user_input:
                print("Not a valid entry, please try again.")
            else:
                self.menu_input = user_input
                break
            
        
        





if __name__ == "__main__":
    print("\nTesting Menus only:\n") #/////////////////
    MainMenu()
    print()