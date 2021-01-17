import sqlite3 as sql

connection = sql.connect("G:/Dissertation Code/FirstDraft/Database/ChrDatabase.db")
cursor = connection.cursor()


def int_input(prompt):
    """
    Repeatedly asks for an input until an integer is entered.
    :param prompt: the question an input is required for
    :type prompt: str
    :return: the integer input
    """
    output = None
    while output is None:
        try:
            output = int(input(prompt))
        except ValueError:
            print("The input entered was not an integer")
    return output


def complete_setup():
    """
    Commits and closes the database connection, ensuring all edits are saved.
    """
    connection.commit()
    connection.close()


def get_id(name, table):
    """
    Gets the id of a row from their table and name.
    :param name: the name of the row to be found
    :type name: str
    :param table: the table the row is located in
    :type table: str
    :return: the integer value of the data's id
    """
    name = name.replace("'", "''")
    cursor.execute("SELECT " + table.lower() + "Id from " + table + " WHERE " + table.lower() + "Name='" + name + "'")
    return int(cursor.fetchone()[0])
