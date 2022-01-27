import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


def execute_sqlite_script(conn, sql_script):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(sql_script)
    except Error as e:
        print(e)


def main():
    database = r"annual_reports.db"

    sql_drop_table = """DROP TABLE IF EXISTS reports; """
    sql_create_reports_table = """CREATE TABLE IF NOT EXISTS reports(
                                	id integer PRIMARY KEY AUTOINCREMENT,
                                	CIK text NOT NULL,
                                	ticker text NOT NULL,
                                	company_name text NOT NULL,
                                	exchange text,
                                	report_period text,
                                	filing_date text,
                                	source_url text,
                                	file_directory text	
                                	); """



    # create a database connection
    conn = create_connection(database)

    # create tables
    if conn is not None:
        # create projects table
        execute_sqlite_script(conn,sql_drop_table)
        execute_sqlite_script(conn, sql_create_reports_table)


    else:
        print("Error! cannot create the database connection.")


if __name__ == '__main__':
    main()