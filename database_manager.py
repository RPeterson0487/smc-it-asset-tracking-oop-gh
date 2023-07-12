"""This class provides functionality for updating MariaDB database tables."""

# Standard library imports.

# Third party imports.
import mariadb

# Local application/library specific imports.
import asset as asset
import database_manager_config as dbconfig


class DatabaseManager:
    """Database manager base class."""

    def __init__(self):
        """Initializes a database manager object."""
        
        # Login variables
        self._database_host = dbconfig.mariadb_login["host"]
        self._database_name = dbconfig.mariadb_login["database"]
        self._username = dbconfig.mariadb_login["username"]
        self._password = dbconfig.mariadb_login["password"]

        # Connection / Cursor variables.
        self._connection = None
        self._cursor = None
        
        # Connection / Cursor method.
        try:
            self._connection = mariadb.connect(
                host=self._database_host,
                user=self._username,
                password=self._password,
                database=self._database_name
            )

            self._cursor = self._connection.cursor(dictionary = True)
        except Exception as error:
            print(f"\nError connecting to database:\n{error}\n")
    
    
    def close_connection(self):
        """Commits changes and closes the connection."""
        try:
            self._connection.commit()
            self._connection.close()
            print("Connection Closed.")
        except Exception as error:
            print(f"\nError closing database:\n{error}\n")
    
    
    def search_tables(self, search_term):
        """Search through the database tables listed in config."""
        
        search_results = []
        
        if not search_term.strip():
            return "Empty Search"
        else:
            for table in dbconfig.search_tables:
                column_list = []
                
                self._cursor.execute(f"""
                    SHOW COLUMNS
                    FROM {table}
                """)
                column_row = self._cursor.fetchone()
                while column_row is not None:
                    column_list.append(column_row["Field"])
                    column_row = self._cursor.fetchone()
                    
                for column in column_list:
                    self._cursor.execute(f"""
                        SELECT *
                        FROM {table}
                        WHERE {column}
                        LIKE '%{search_term}%'
                    """)
                    return_row = self._cursor.fetchone()
                    while return_row is not None:
                        if table == "IT_Assets":
                            item = asset.AssetNew()
                        else:
                            item = asset.AssetOld()
                        for key, value in return_row.items():
                                setattr(item, key, value)
                        if item not in return_row:
                            item.table = table
                            item.column = column
                            search_results.append(item)
            return search_results
                            
                            
                        
                        
            #             return_row["table"] = table
            #             return_row["column"] = column
            #             if not self._check_for_duplicates(return_row, search_results):
            #                 search_results.append(return_row)
            #             return_row = self._cursor.fetchone()
            # return search_results
    
    
    # def _check_for_duplicates(self, entry, results):
    #     """Compares entry to the list of results to check for duplicate match."""
        
    #     ignore_keys = ("column",)
        
    #     if not results:
    #         return False
    #     else:
    #         for dictionary in results:
    #             duplicate = True
    #             for key in dictionary:
    #                 if key not in ignore_keys and entry.get(key) != dictionary.get(key):
    #                     duplicate = False
    #                     break
    #                 if duplicate:
    #                     return True
    #             return False