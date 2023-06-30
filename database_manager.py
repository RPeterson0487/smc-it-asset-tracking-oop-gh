"""This class provides functionality for updating MariaDB database tables."""
# Standard library imports.

# Third party imports.
import mariadb

# Local application/library specific imports.
import database_manager_config as dbconfig

class DatabaseManager:
    """Database manager base class."""
    
    def __init__(self) -> None:
        """Initializes a database manager object."""
        
        # Login variables
        self.database_host = dbconfig.mariadb_login["host"]
        self.database_name = dbconfig.mariadb_login["database"]
        self.username = dbconfig.mariadb_login["username"]
        self.password = dbconfig.mariadb_login["password"]

        # Connection / Cursor variables
        self._connection = None
        self._cursor = None
        
        # Attempt to connect to database
        try:
            self._connection = mariadb.connect(
                host = self.database_host,
                user = self.username,
                password = self.password,
                database = self.database_name
            )
            
            # Create database cursor
            self._cursor = self._connection.cursor(dicionary = True)
        except:
            print("\nError connecting to database.\n")
        return