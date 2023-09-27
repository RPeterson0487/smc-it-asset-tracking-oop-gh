"""This class provides functionality for updating MariaDB database tables."""

# Standard library imports.

# Third party imports.
import mariadb

# Local application/library specific imports.
import database_manager_config as dbconfig


class DatabaseManager:
    """Database manager base class."""

    def __init__(self):
        """Initializes a database manager object."""
        
        # Login variables
        self._database_host = dbconfig.mariadb_login["host"]
        self.database_name = dbconfig.mariadb_login["database"]
        self._username = dbconfig.mariadb_login["username"]
        self._password = dbconfig.mariadb_login["password"]

        # Connection / Cursor variables.
        self.connection = None
        self._cursor = None
        
        # Error variable.
        self.fail_error = None
        
        # Connection / Cursor method.
        try:
            self.connection = mariadb.connect(
                host=self._database_host,
                user=self._username,
                password=self._password,
                database=self.database_name
            )

            self._cursor = self.connection.cursor(dictionary = True)
        except Exception as error:
            self.fail_error = error
            print(f"\nError connecting to database:\n{error}\n")
            return
        
        # Device / Field control variables.
        self.field_control = self._setup_field_control()
        self.insert_key_list = self._show_columns(dbconfig.insert_table)
    
    
    def close_connection(self):
        """Commits changes and closes the connection."""
        try:
            self.connection.commit()
            self.connection.close()
            print("Connection Closed.")
        except Exception as error:
            print(f"\nError closing database:\n{error}\n")
            self.fail_error = error
    
    
    def search_tables(self, search_term:str, search_fields: list = [], search_partial: bool = True):
        """Search through the database tables listed in config."""
        
        search_results = []
        
        if not search_term.strip():
            return "Empty Search"
        else:
            for table in dbconfig.search_tables:
                column_list = self._show_columns(table)
                for column in column_list:
                    if not search_fields or column in search_fields:
                        if search_partial:
                            self._cursor.execute(f"""
                                SELECT *
                                FROM {table}
                                WHERE {column}
                                LIKE '%{search_term}%'
                            """)
                        else:
                            self._cursor.execute(f"""
                                SELECT *
                                FROM {table}
                                WHERE {column}
                                = '{search_term}'
                            """)
                    return_row = self._cursor.fetchone()
                    
                    while return_row is not None:
                        item = dbconfig.template()
                        for key, value in return_row.items():
                            setattr(item, key, value)
                        if item not in search_results:
                            item.table = table
                            item.column = column
                            search_results.append(item)
                            
                        return_row = self._cursor.fetchone()
                            
            return search_results
        
        
    def new_object(self, key_values: dict):
        initial = dbconfig.template()
        for key, value in key_values.items():
            setattr(initial, key, value)
        initial.table = dbconfig.insert_table
        return initial
    
    
    def save_object(self, class_object: object):
        attributes = vars(class_object)
        columns = []
        values = []
        update_columns = []
        object_updated = None
        
        if hasattr(class_object, "table"):
            save_table = class_object.table
        else:
            save_table = dbconfig.insert_table
        
        for key, value in attributes.items():
            if key not in ("table", "column"):
                if key in ("Serial", "Current_User"):
                    key = f"`{key}`"
                columns.append(key)
                values.append(value)
        columns_string = ", ".join(columns)
        placeholders = ", ".join(["%s"] * len(columns))
        
        for key in columns:
            update_columns.append(f"{key} = VALUES({key})")
        update_clause = ", ".join(update_columns)
        
        query = f"""
            INSERT INTO {save_table} ({columns_string})
            VALUES ({placeholders})
            ON DUPLICATE KEY
            UPDATE {update_clause}
        """
        
        self._cursor.execute(query, values)
        self.connection.commit()
        
        if self._cursor.lastrowid:
            object_updated = self._cursor.lastrowid
        elif not self._cursor.lastrowid and self._cursor.rowcount:
            object_updated = "updated"
        
        return object_updated
    
    
    def _setup_field_control(self):
        field_dictionary = {}
        column_list = self._show_columns(dbconfig.control_tables[0])
        
        self._cursor.execute(f"""
            SELECT {column_list[0]}, {column_list[1]}
            FROM {dbconfig.control_tables[0]}
        """)
        
        control_row = self._cursor.fetchone()
        while control_row is not None:
            key = control_row[column_list[0]]
            value_list = control_row[column_list[1]].split(", ")
            field_dictionary[key] = value_list
            control_row = self._cursor.fetchone()
        return field_dictionary
    
    
    def _show_columns(self, table_name):
        columns = []
                
        self._cursor.execute(f"""
            SHOW COLUMNS
            FROM {table_name}
        """)
        
        column_row = self._cursor.fetchone()
        while column_row is not None:
            columns.append(column_row["Field"])
            column_row = self._cursor.fetchone()

        return columns
    
    
    
    
if __name__ == "__main__":
    dbTest = DatabaseManager()