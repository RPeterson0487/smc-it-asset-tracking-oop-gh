# Standard library imports.

# Third party imports.

# Local application/library specific imports.
import database_manager as database
import cli_menus as menu


def main():
    maria = database.DatabaseManager()
    main_menu = menu.MainMenu()
    
    
    
    print("Executed") #/////////////////////////////////


if __name__ == "__main__":
    main()