import sqlite3

class db:
    ## Initializes a database connection with the specified credentials.
    def __init__(self, dbname):
        self.dbname = dbname
        self.connect()

    ## Establishes a connection to the SQLite database.
    def connect(self):
        self.con = sqlite3.connect(f"{self.dbname}.db")
        self.cur = self.con.cursor()

    ## Closes the database connection.
    def close(self):
        self.con.close()

    ## Provides a context manager for database connection and transaction handling.
    def database_connection(self):
        try:
            yield self
            self.con.commit()
        except Exception as e:
            self.con.rollback()
            raise e
        finally:
            self.close()

    ## Creates a new table in the database with the specified columns.
    def create_table(self, table_name, columns):
        column_definitions = []

        for col_name, col_type in columns.items():
            col_definition = f"{col_name} {col_type}"
            column_definitions.append(col_definition)
        
        columns_str = ", ".join(column_definitions)
        query = f"CREATE TABLE {table_name} ({columns_str})"
        self.execute_query(query)

    ## Drops the specified table from the database.
    def drop_table(self, table_name):
        query = f"DROP TABLE IF EXISTS {table_name}"
        self.execute_query(query)

    ## Inserts a new row with the given values into the specified table.
    def insert(self, form, values):
        columns = list(values.keys())
        field_string = ", ".join(columns)
        placeholder = ", ".join(["?" for _ in columns])

        query = f"INSERT INTO {form} ({field_string}) VALUES ({placeholder})"
        self.cur.execute(query, list(values.values()))
        self.con.commit()

    ## Updates rows in the specified table with new values based on conditions.
    def update(self, form, set_values, conditions):
        set_columns = ", ".join([f"{col} = ?" for col in set_values.keys()])
        condition = " AND ".join([f"{col} = ?" for col in conditions.keys()])

        query = f"UPDATE {form} SET {set_columns} WHERE {condition}"
        
        values = list(set_values.values()) + list(conditions.values())
        
        self.cur.execute(query, values)
        self.con.commit()

    ## Deletes rows from the specified table based on conditions.
    def delete(self, form, conditions):
        condition = " AND ".join([f"{col} = ?" for col in conditions.keys()])
        values = list(conditions.values())
        query = f"DELETE FROM {form} WHERE {condition}"
        try:
            self.cur.execute(query, values)
            self.con.commit()
            return "Rows deleted successfully."
        except Exception as e:
            print(f"Exception occurred: {e}")
            return "An exception occurred while deleting rows."

       ## Executes a custom SQL query and returns the fetched results.
    def execute_query(self, query, values=None):
        if values is None:
            self.cur.execute(query)
        else:
            self.cur.execute(query, values)
        return self.cur.fetchall()
        
    ## Selects rows from the specified table with optional columns and conditions.
    def select(self, form, columns=None, conditions=None):
        if columns is None:
            columns = "*"
        else:
            columns = ", ".join(columns)

        query = f"SELECT {columns} FROM {form}"

        values = []  # Initialize values as an empty list
        if conditions:
            condition_clauses = []
            for col, val in conditions.items():
                if "LIKE" in col.upper():
                    condition_clauses.append(f"{col}")
                else:
                    condition_clauses.append(f"{col} = ?")
                    values.append(val)  # Only append values for non-LIKE conditions
            condition = " AND ".join(condition_clauses)
            query += f" WHERE {condition}"

        self.cur.execute(query, values)  # Pass values here, it will be an empty list if there are no conditions

        self.get_result = self.cur.fetchall()
        return self.get_result

    ## Selects all rows from the specified table.
    def select_all(self, form):
        self.cur.execute(f"SELECT * FROM {form}")
        self.get_all_result = self.cur.fetchall()
        return self.get_all_result
