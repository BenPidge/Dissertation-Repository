from Database import CoreDatabase as Db


class DataExtractor:
    """A class used for extracting data from the database."""

    # Represents the table(s) accessible from the input table using an intermediary table
    # This excludes equipment due to the intermediary table holding extra information
    INDIRECT_PATHS = {"Background": ["Proficiency", "Language"], "RaceOptions": ["Language", "Proficiency", "Spell"],
                      "ClassOptions": ["Proficiency", "Trait", "Language"], "Magic": ["Spell"], "Race": ["Trait"]}

    # CORE STATIC METHODS

    @staticmethod
    def getNamesFromConnector(start_table, input_id, end_table):
        """
        Given two tables and an id, it gets all possible row names from the second table that are
        intermediately connected to the first row. This does not operate for EquipmentOption as the
        intermediary table has useful information.
        :param start_table: the name of the table the connection travels from
        :type start_table: str
        :param input_id: the id of the row to travel from in the start table
        :type input_id: int
        :param end_table: the name of the table the connection travels to
        :type end_table: str
        :return: an array of the names assigned within the rows pulled from the end table
        """
        # determines the name of the intermediary table
        if start_table == "Magic":
            connTable = "ClassSpell"
        else:
            connTable = start_table.replace("Options", "") + end_table

        # determines what is returned
        if end_table == "Language":
            endId = "language"
            nameColumn = "languageName"
        else:
            endId = Db.tableToId(end_table)
            nameColumn = endId.replace("Id", "Name")
        startId = Db.tableToId(start_table)

        # joins the tables to extract the names
        command = f"SELECT {nameColumn} FROM {connTable} INNER JOIN {start_table} ON {start_table}.{startId} = " \
                  f"{connTable}.{startId} INNER JOIN {end_table} ON {end_table}.{endId} = {connTable}.{endId} " \
                  f"WHERE {start_table}.{startId}={str(input_id)}"
        Db.cursor.execute(command)

        # converts the output into a cleaner, 1D array
        initOutput = Db.cursor.fetchall()
        output = []
        for item in initOutput:
            output.append(item[0])

        return output



    # CORE NON-STATIC METHODS

    def begin(self):
        """
        Begins the use of the data extraction.
        """
        Db.cursor.execute("SELECT magicId FROM Magic WHERE classId=2")
        bardId = Db.cursor.fetchone()[0]
        methodOutput = DataExtractor.getNamesFromConnector("Magic", bardId, "Spell")
        print(methodOutput)

