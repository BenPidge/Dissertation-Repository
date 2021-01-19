from Database import CoreDatabase as Db
from Database import DatabaseSetup


# Represents the table(s) accessible from the input table using an intermediary table
# This excludes equipment due to the intermediary table holding extra information
INDIRECT_PATHS = {"Background": ["Proficiency", "Language"], "RaceOptions": ["Language", "Proficiency", "Spell"],
                  "ClassOptions": ["Proficiency", "Trait", "Language"], "Magic": ["Spell"], "Race": ["Trait"]}


def getNamesFromConnector(start_table, end_table, input_id=-1, input_name=""):
    """
    Given two tables and an id or name, it gets all possible row names from the second table that are
    intermediately connected to the first row. This does not operate for EquipmentOption as the
    intermediary table has useful information.
    :param start_table: the name of the table the connection travels from
    :type start_table: str
    :param end_table: the name of the table the connection travels to
    :type end_table: str
    :param input_id: the id of the row to travel from in the start table. This or input_name must not be default
    :type input_id: int
    :param input_name: the name of the row to travel from in the start table. This or input_id must not be default
    :type input_name: str
    :return: an array of the names assigned within the rows pulled from the end table
    """
    # retrieves the id, if not provided
    if input_id == -1:
        input_id = Db.get_id(input_name, start_table)

    # determines the name of the intermediary table
    if start_table == "Magic":
        connTable = "ClassSpell"
    else:
        connTable = start_table.replace("Options", "") + end_table

    # determines the required variables for the sql call
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


def backgroundConnections(background_name):
    """
    Returns the names of the options a background offers, as well as all the background information alongside.
    :param background_name: the name of the background to check
    :type background_name: str
    :return: 3 2D array - tools, skills and languages - holding the amount to pick and an array of the options
    """
    Db.cursor.execute(f"SELECT skillAmnt, toolAmnt, languageAmnt FROM Background "
                      f"WHERE backgroundName='{background_name}'")
    skillAmnt, toolAmnt, languageAmnt = Db.cursor.fetchone()
    proficiencies = getNamesFromConnector("Background", "Proficiency", input_name=background_name)
    languages = getNamesFromConnector("Background", "Language", input_name=background_name)

    Db.cursor.execute("SELECT proficiencyName, proficiencyType FROM Proficiency WHERE proficiencyName IN ('"
                      + "', '".join(proficiencies) + "')")
    skills, tools = [], []
    for pair in Db.cursor.fetchall():
        if pair[1] == "Skill":
            skills.append(pair[0])
        else:
            tools.append(pair[0])

    return [toolAmnt, tools], [skillAmnt, skills], [languageAmnt, languages]


def classOptionsConnections(class_options_id, subclass_id=-1):
    """
    Returns the names of the options that the ClassOptions offers, and ClassOptions data.
    :param class_options_id: the id of the ClassOptions to pull data from
    :type class_options_id: int
    :param subclass_id: the id of the subclass to include checks for, if appropriate
    :type subclass_id: int
    :return: the level required and amount to choose in an array, and an array of the choices
    """
    # retrieve all data related to the ClassOptions
    if subclass_id > -1:
        subclassCall = "=" + str(subclass_id)
    else:
        subclassCall = " IS NULL"

    Db.cursor.execute("SELECT lvlRequired, amntToChoose FROM ClassOptions WHERE classOptionsId="
                      + str(class_options_id) + " AND subclassId" + subclassCall)
    metadata = [class_options_id] + list(Db.cursor.fetchone())
    languages = getNamesFromConnector("ClassOptions", "Language", class_options_id)
    proficiencies = getNamesFromConnector("ClassOptions", "Proficiency", class_options_id)
    traits = getNamesFromConnector("ClassOptions", "Trait", class_options_id)

    # converts all the data into two arrays
    output = []
    for data in [languages, proficiencies, traits]:
        if data is not None:
            output += data
    if metadata[0] is None:
        metadata[0] = 1

    # if the ClassOptions holds no information connections, it was saved during an insert that failed,
    # so thus deletes the row
    if len(output) == 0:
        Db.cursor.execute("DELETE FROM ClassOptions WHERE classOptionsId=" + str(class_options_id))
    return metadata, output



def begin():
    """
    Begins the use of the data extraction.
    """
    for x in ["Barbarian", "Bard", "Cleric", "Druid", "Fighter", "Monk", "Paladin", "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard"]:
        Db.cursor.execute("SELECT classOptionsId FROM ClassOptions WHERE classId=" + str(Db.get_id(x, "Class")) + " AND subclassId IS NULL")
        ids = Db.cursor.fetchall()
        print("Values for " + x)
        for nextId in ids:
            output = classOptionsConnections(nextId[0])
            print(output)
        print("\n")

