# Standard library imports.

# Third party imports.

# Local application/library specific imports.
import database_manager as database

def main():
    maria = database.DatabaseManager()
    print("Test")
    print(maria.database_host)


if __name__ == "__main__":
    main()