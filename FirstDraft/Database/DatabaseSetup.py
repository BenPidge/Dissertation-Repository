from Database import CoreDatabase as Db

# CORE STATIC COMMANDS


def setup_tables():
    """
    Sets up all the database tables by running through the text file.
    """
    count = 0
    nextCommand = ""

    with open("Database/Resources/DatabaseTables.txt") as file:
        while True:
            count += 1
            line = file.readline()

            if not line:
                break

            if line[:2] != "--" and len(line) > 1:
                nextCommand += line
            else:
                Db.cursor.execute(nextCommand)
                nextCommand = ""
    file.close()


def add_another_item():
    """
    Asks the user if they want to add another item, until 'Y' or 'N' are entered.
    :return: a boolean stating whether they want to add another item
    """
    addMore = True
    repeat = True
    while repeat:
        addMoreInp = input("Would you like to add another? Y/N: ")
        if addMoreInp == "Y" or addMoreInp == "N":
            repeat = False
            if addMoreInp == "N":
                addMore = False
    return addMore


def print_added_table(table, plural):
    """
    Prints the names of all the currently entered items in the inputted table.
    :param table: the table to extract the rows from
    :type table: str
    :param plural: the plural text of the tables' content
    :type plural: str
    """
    Db.cursor.execute("SELECT COUNT(*) FROM " + table)
    amount = Db.cursor.fetchone()[0]
    Db.cursor.execute("SELECT " + table.lower() + "Name FROM " + table)
    rows = sorted(Db.cursor.fetchall())
    outputStr = ""
    for row in rows:
        outputStr += row[0] + ", "
    print((plural + "(" + str(amount) + "): " + outputStr)[:-2])


def remove_item(table, item_id=None, name=None):
    """
    Removes an item from a table, based on their name or id.
    :param table: the table to remove the item from
    :type table: str
    :param item_id: the id of the item to remove
    :type item_id: str
    :param name: the name of the item to remove
    :type name: str
    """
    if item_id is None:
        sqlCall = "DELETE FROM " + table + " WHERE " + table.lower() + "Name=" + name
    else:
        sqlCall = "DELETE FROM " + table + " WHERE " + Db.table_to_id(table) + "=" + item_id
    Db.cursor.execute(sqlCall)


# CORE NON-STATIC COMMANDS


def begin():
    """
    Begins the use of the database setup.
    """
    setup_tables()
    print_all_added_data()
    add_item()


def add_item():
    """
    Produces a simple text menu to allow the user to select which kind of item they wish to add.
    This is used for simple navigation during the database filling process.
    """
    print("Choose one of the options below to add, or 13 to exit:\n"
          "1. Spells\n"
          "2. Languages\n"
          "3. Proficiencies\n"
          "4. Equipment\n"
          "5. Background\n"
          "6. Trait\n"
          "7. Race\n"
          "8. Subrace\n"
          "9. Class\n"
          "10. Subclass\n"
          "11. Tag\n"
          "12. Archetype\n"
          "13. Exit\n")
    value = Db.int_input("> ")
    if value == 1:
        add_spells()
    elif value == 2:
        add_languages()
    elif value == 3:
        add_proficiencies()
    elif value == 4:
        add_equipment()
    elif value == 5:
        add_background()
    elif value == 6:
        add_trait()
    elif value == 7:
        add_race()
    elif value == 8:
        add_subrace()
    elif value == 9:
        add_class()
    elif value == 10:
        add_subclass()
    elif value == 11:
        add_tag()
    elif value == 12:
        add_archetype()


def print_all_added_data():
    """
    Prints all the currently added data, in long strings that start with the data groups. For example, a line
    beginning with 'Spells:' shows all the names of spells that have been added.
    This is used for consistency and checkup during the database filling process.
    """
    tables = [["Spell", "Spells"], ["Proficiency", "Proficiencies"], ["Language", "Languages"],
              ["Equipment", "Equipment"], ["Background", "Backgrounds"], ["Race", "Races"], ["Subrace", "Subraces"],
              ["Trait", "Traits"], ["Class", "Classes"], ["Subclass", "Subclasses"], ["Tag", "Tags"],
              ["Archetype", "Archetypes"]]
    for table in tables:
        print_added_table(table[0], table[1])
    print("\n")


# ADD OVERARCHING TABLES' ROWS


def add_race():
    """
    Adds one or more races to the database.
    """
    # Gets the current amount of races and RaceOptions
    Db.cursor.execute("SELECT COUNT(*) FROM Race")
    raceId = Db.cursor.fetchone()[0]
    Db.cursor.execute("SELECT COUNT(*) FROM RaceOptions")
    raceOptionsId = Db.cursor.fetchone()[0]

    addMore = True
    while addMore:
        # Collects the bare race data
        raceId += 1
        name = input("Enter the race's name: ")
        speed = Db.int_input("Enter the race's speed: ")
        size = input("Enter the size of the race: ")
        darkvision = input("Does the race have darkvision? (Y/N): ") == "Y"
        resistance = input("Enter the race's resistance(s), or press enter if it has none: ")
        # Inserts the data, and converts the darkvision Y/N into 1 or 0
        Db.cursor.execute("INSERT INTO Race(raceId, raceName, speed, size, darkvision, resistance) "
                          "VALUES(?, ?, ?, ?, ?, ?);", (raceId, name, speed, size, darkvision, resistance))

        # Adds the ability scores for the race
        addElement = True
        while addElement:
            newScore = input("Add the first 3 letters of the new ability score, or ALL for a choice of any: ")
            scoreAmnt = Db.int_input("How much does this score increase by? ")
            Db.cursor.execute("INSERT INTO RaceAbilityScore(raceId, abilityScore, scoreIncrease) VALUES(?, ?, ?);",
                              (raceId, newScore, scoreAmnt))
            addElement = add_another_item()
        print("Ability scores have now all been added\n")

        # Adds all data received from other methods
        raceOptionsId = add_language_connection("Race", raceId, raceOptionsId)
        print("Languages have now all been added\n")
        raceOptionsId = add_proficiency_connection("Race", raceId, raceOptionsId)
        print("Proficiencies have now all been added\n")
        raceOptionsId = add_race_spell(raceId, raceOptionsId)
        print("Spells have now all been added\n")

        # Adds traits
        addElement = True
        while addElement:
            nextTrait = input("Enter the name of the trait to add, or press enter for none: ")
            if nextTrait != "":
                nextTrait = Db.get_id(nextTrait, "Trait")
                Db.cursor.execute("INSERT INTO RaceTrait(raceId, traitId) VALUES(?, ?);", (raceId, nextTrait))
                addElement = add_another_item()
            else:
                addElement = False
        print("All traits have now been added\n")

        addMore = add_another_item()


def add_subrace():
    """
    Adds one or more subraces to the database.
    """
    Db.cursor.execute("SELECT COUNT(*) FROM Subrace")
    subraceId = Db.cursor.fetchone()[0]
    Db.cursor.execute("SELECT COUNT(*) FROM RaceOptions")
    raceOptionsId = Db.cursor.fetchone()[0]
    print("For all requested data, press enter if it isn't changed from the core race.\n")

    addMore = True
    while addMore:
        subraceId += 1
        race = input("Enter the name of the race this extends from: ")
        raceId = Db.get_id(race, "Race")
        name = input("Enter the subrace's name: ")
        speed = Db.int_input("Enter the subrace's speed, or 0 if it doesn't change: ")
        darkvision = input("Does the subrace gain darkvision? (Y/N): ") == "Y"
        resistance = input("Enter the subrace's resistance(s), or press enter if it has none: ")

        # Inserts the data, finding the parameters needed, and converts the darkvision Y/N into 1 or 0
        sqlCall = "INSERT INTO Subrace(subraceId, raceId, subraceName"
        sqlValues = ") VALUES(?, ?, ?"
        params = [["darkvision", int(darkvision)], ["speed", speed], ["resistance", resistance]]
        newParams = []
        for param in params:
            if not (param[1] == "" or param[1] == 0):
                sqlCall += ", " + param[0]
                sqlValues += ", ?"
                newParams.append(param[1])

        sqlCall += sqlValues + ");"
        Db.cursor.execute(sqlCall, (subraceId, raceId, name) + (*newParams,))

        # Adds the ability scores for the race
        addElement = True
        while addElement:
            newScore = input("Add the first 3 letters of the new ability score, or ALL for a choice of any: ")
            scoreAmnt = Db.int_input("How much does this score increase by? ")
            Db.cursor.execute("INSERT INTO RaceAbilityScore(raceId, abilityScore, scoreIncrease, subraceId) "
                              "VALUES(?, ?, ?, ?);", (raceId, newScore, scoreAmnt, subraceId))
            addElement = add_another_item()
        print("Ability scores have now all been added\n")

        raceOptionsId = add_language_connection("Race", raceId, raceOptionsId, subraceId)
        print("Languages have now all been added\n")
        raceOptionsId = add_proficiency_connection("Race", raceId, raceOptionsId, subraceId)
        print("Proficiencies have now all been added\n")
        raceOptionsId = add_race_spell(raceId, raceOptionsId, subraceId)
        print("Spells have now all been added\n")

        addElement = True
        while addElement:
            nextTrait = input("Enter the name of the trait to add, or press enter for none: ")
            if nextTrait != "":
                nextTrait = Db.get_id(nextTrait, "Trait")
                Db.cursor.execute("INSERT INTO RaceTrait(raceId, traitId, subraceId) VALUES(?, ?, ?);",
                                  (raceId, nextTrait, subraceId))
                addElement = add_another_item()
            else:
                addElement = False
        print("All traits have now been added\n")

        addMore = add_another_item()


def add_class():
    """
    Adds the first level of one or more classes into the database.
    """
    # Gets the current amount of classes and ClassOptions
    Db.cursor.execute("SELECT COUNT(*) FROM Class")
    classId = Db.cursor.fetchone()[0]
    Db.cursor.execute("SELECT COUNT(*) FROM ClassOptions")
    classOptionsId = Db.cursor.fetchone()[0] + 100

    addMore = True
    while addMore:
        # Collects the core data for the class
        classId += 1
        name = input("Enter the classes name: ")
        hitDice = Db.int_input("Enter the amount of sides of the character's hit dice: ")
        pAbility = input("Enter the first 3 letters of the primary ability: ")
        sAbility = input("Enter the first 3 letters of the secondary ability: ")
        isMagic = input("Is the class fully or partially magical? (Y/N) ") == "Y"
        savingThrows = input("Enter the first three characters of the first saving throw: ")
        savingThrows += ", " + input("Enter the first three characters of the second saving throw: ")
        Db.cursor.execute("INSERT INTO Class(classId, className, hitDiceSides, primaryAbility, secondaryAbility, "
                          "isMagical, savingThrows) VALUES(?, ?, ?, ?, ?, ?, ?);",
                          (classId, name, hitDice, pAbility, sAbility, isMagic, savingThrows))

        # Adds all data received from other methods
        print("Input the starting equipment information.")
        add_equipment_option("class", classId)
        print("Equipment has now all been added\n")
        classOptionsId = add_language_connection("Class", classId, classOptionsId)
        print("Languages have now all been added\n")
        classOptionsId = add_proficiency_connection("Class", classId, classOptionsId)
        print("Proficiencies have now all been added\n")
        add_class_magic(classId, 1)
        print("Magic details have now been added\n")
        classOptionsId = add_class_traits(classId, classOptionsId)
        print("All traits have now been added\n")

        addMore = add_another_item()


def add_subclass():
    """
    Adds the first level of one or more subclasses to the database.
    """
    Db.cursor.execute("SELECT COUNT(*) FROM Subclass")
    subclassId = Db.cursor.fetchone()[0]
    Db.cursor.execute("SELECT COUNT(*) FROM ClassOptions")
    classOptionsId = Db.cursor.fetchone()[0] + 100

    addMore = True
    while addMore:
        # Adds core subclass data
        subclassId += 1
        classId = input("Enter what class you want to create a subclass for: ")
        classId = Db.get_id(classId, "Class")
        subclassName = input("Enter the name of the new subclass: ")
        Db.cursor.execute("INSERT INTO Subclass(subclassId, classId, subclassName) VALUES(?, ?, ?);",
                          (subclassId, classId, subclassName))

        # Adds all data received from other methods
        classOptionsId = add_language_connection("Class", classId, classOptionsId, subclassId)
        print("Languages have now all been added\n")
        classOptionsId = add_proficiency_connection("Class", classId, classOptionsId, subclassId)
        print("Proficiencies have now all been added\n")
        lvl = Db.int_input("Enter the level that this subclass is chosen: ")
        add_class_magic(classId, lvl, subclassId)
        print("Magic details have now been added\n")
        classOptionsId = add_class_traits(classId, classOptionsId, subclassId)
        print("All traits have now been added\n")

        addMore = add_another_item()


def add_background():
    """
    Adds one or more backgrounds to the database.
    """
    Db.cursor.execute("SELECT COUNT(*) FROM Background")
    backgroundId = Db.cursor.fetchone()[0]
    addMore = True
    while addMore:
        backgroundId += 1
        name = input("Enter the background's name: ")
        skillAmnt = Db.int_input("Enter how many skills the character gets: ")
        toolAmnt = Db.int_input("Enter how many tools the character gets: ")
        languageAmnt = Db.int_input("Enter how many languages the character gets: ")
        Db.cursor.execute("INSERT INTO Background(backgroundId, backgroundName, skillAmnt, toolAmnt, languageAmnt) "
                          "VALUES(?, ?, ?, ?, ?);", (backgroundId, name, skillAmnt, toolAmnt, languageAmnt))

        add_background_connections(backgroundId, skillAmnt, languageAmnt, toolAmnt)
        add_equipment_option("background", backgroundId)

        print("The background and connections have now been added.")
        addMore = add_another_item()


def add_trait():
    """
    Adds one or more traits to the database.
    """
    Db.cursor.execute("SELECT COUNT(*) FROM Trait")
    traitId = Db.cursor.fetchone()[0]
    addMore = True
    while addMore:
        traitId += 1
        name = input("Enter the trait's name: ")
        description = input("Enter the trait's description: ")
        tags = input("Enter the tag or tags this tag involves: ")
        tagValue = Db.int_input("Enter the value related to this tag, or -1 if there isn't one: ")

        if tagValue == -1:
            Db.cursor.execute("INSERT INTO Trait(traitId, traitName, traitDescription) "
                              "VALUES(?, ?, ?, ?);", (traitId, name, description))
        else:
            Db.cursor.execute("INSERT INTO Trait(traitId, traitName, traitDescription, traitTagValue) "
                              "VALUES(?, ?, ?, ?, ?);", (traitId, name, description, tagValue))

        for tag in tags.split(", "):
            Db.cursor.execute("INSERT INTO TraitTag(genericTagId, traitId) VALUES(?, ?)",
                              (Db.get_id(tag, "GenericTag"), traitId))

        addOption = input("Does this trait have options? (Y/N) ") == "Y"
        Db.cursor.execute("SELECT COUNT(*) FROM TraitOption")
        traitOptionId = Db.cursor.fetchone()[0]
        while addOption:
            traitOptionId += 1
            desc = input("Enter the description of the option: ")
            value = Db.int_input("Enter the number value associated with this option, or -1 if there is none: ")

            if tagValue == -1:
                Db.cursor.execute("INSERT INTO TraitOption(traitOptionId, traitId, optionDesc) VALUES(?, ?, ?);",
                                  (traitOptionId, traitId, desc))
            else:
                Db.cursor.execute("INSERT INTO TraitOption(traitOptionId, traitId, optionDesc, optionVal) "
                                  "VALUES(?, ?, ?, ?);", (traitOptionId, traitId, desc, value))
            addOption = add_another_item()
        print("All trait options are added\n")

        addMore = add_another_item()


def add_tag():
    """
    Adds a tag, and connections, to the database.
    """
    Db.cursor.execute("UPDATE Tag SET tagSubgroup='Combat' WHERE tagName='Weapons' OR tagName='Melee'")
    Db.cursor.execute("SELECT proficiencyType FROM Proficiency")
    types = set(Db.cursor.fetchall())
    print(types)
    Db.cursor.execute("SELECT COUNT(*) FROM Tag")
    tagId = Db.cursor.fetchone()[0]
    addMore = True
    while addMore:
        tagId += 1
        name = input("Enter the name of the tag to add: ")
        subgroup = input("Enter the subgroup the tag is a part of: ")
        Db.cursor.execute("INSERT INTO Tag(tagId, tagName, tagSubgroup) VALUES(?, ?, ?)", (tagId, name, subgroup))

        addProf = True
        while addProf:
            prof = input("Enter the next proficiency it links to, or GROUP group_name for a collection: ")
            if prof.startswith("GROUP"):
                Db.cursor.execute("SELECT proficiencyId FROM Proficiency WHERE proficiencyType LIKE '%" +
                                  prof[6:].replace("'", "''") + "%'")
            else:
                Db.cursor.execute("INSERT INTO TagProficiency(tagId, proficiencyId) VALUES (?, ?)",
                                  (tagId, Db.get_id(prof, "Proficiency")))
            addProf = add_another_item()

        addMore = add_another_item()


def add_archetype():
    """
    Adds an archetype, and connections, to the database.
    """
    Db.cursor.execute("SELECT COUNT(*) FROM Archetype")
    archId = Db.cursor.fetchone()[0]
    addMore = True
    while addMore:
        archId += 1
        name = input("Insert the name of the archetype: ")
        desc = input("Enter the description: ")
        magicWeight = Db.float_input("Enter the magic weighting: ")
        healthWeight = Db.float_input("Enter the health weighting: ")
        Db.cursor.execute("INSERT INTO Archetype(archetypeId, archetypeName, description, magicWeighting, "
                          "healthWeighting) VALUES(?, ?, ?, ?, ?)", (archId, name, desc, magicWeight, healthWeight))

        addTag = True
        while addTag:
            name = input("Enter the name of the next tag: ")
            weight = Db.float_input("Enter the weighting value of the tag: ")
            Db.cursor.execute("INSERT INTO ArchetypeTag(archetypeId, tagId, weighting) VALUES(?, ?, ?)",
                              (archId, Db.get_id(name, "Tag"), weight))
            addTag = add_another_item()

        addMore = add_another_item()


# ADD CONNECTED ROWS


def add_options_connection(connector_type, options_id, connector_id, subconnector_id=-1, amnt_to_choose=-1):
    """
    Adds a RaceOptions or ClassOptions to be used for part of the race or class building.
    :param connector_type: states whether the row connects to a class or race. It's inputs are 'Class' or 'Race'
    :type connector_type: str
    :param options_id: the id to be used for the new RaceOptions/ClassOptions
    :type options_id: int
    :param connector_id: the unique identifier for the row to add options to
    :type connector_id: int
    :param subconnector_id: the id of the subrace or subclass it connects to, if appropriate
    :type subconnector_id: int, optional
    :param amnt_to_choose: the amount of these options they choose, if a choice must be made
    :type amnt_to_choose: int, optional
    """
    sqlStart = "INSERT INTO " + connector_type + "Options(" + connector_type.lower() + "OptionsId, " \
               + Db.table_to_id(connector_type)
    sqlEnd = "VALUES(?, ?"
    params = [options_id, connector_id]

    if subconnector_id > -1:
        sqlStart += ", sub" + Db.table_to_id(connector_type)
        sqlEnd += ", ?"
        params.append(subconnector_id)
    if amnt_to_choose > -1:
        sqlStart += ", amntToChoose"
        sqlEnd += ",  ?"
        params.append(amnt_to_choose)

    Db.cursor.execute(sqlStart + ") " + sqlEnd + ");", (*params,))


def add_equipment_option(connector_type, connector_id):
    """

    :param connector_type: states whether the row connects to a class, background or another EquipmentOption.
                            It's inputs are 'class', 'background' or 'equipment option'
    :type connector_type: str
    :param connector_id: the id of the class or background it connects to
    :type connector_id: int
    """
    amnt = Db.int_input("How many bullet points of items or item choices are there: ")
    for x in range(1, amnt+1):
        print("Now starting bullet point " + str(x) + "\n")
        add_equipment_point(connector_type, connector_id, "Point " + str(x))


def add_equipment_point(connector_type, connector_id, path=""):
    """
    Creates a row for EquipmentOption, and any rows needed to satisfy it.
    :param connector_type: states whether the row connects to a class, background or another EquipmentOption.
                            It's inputs are 'class', 'background' or 'equipment option'
    :type connector_type: str
    :param connector_id: the id of the class or background it connects to
    :type connector_id: int
    :param path: illustrates the recursion path taken to reach the current point
    :type path: str, optional
    :return the integer value of how many equipmentOptions there are now
    """
    Db.cursor.execute("SELECT COUNT(*) FROM EquipmentOption")
    equipmentOptionId = Db.cursor.fetchone()[0]
    addMore = True
    while addMore:
        equipmentOptionId += 1
        hasChoice = input("Does this option involve a choice? (Y/N) ") == "Y"

        # makes the appropriate SQL call, based on the type of connector
        if connector_type == "equipment option":
            Db.cursor.execute("INSERT INTO EquipmentOption(equipOptionId, suboption, hasChoice) VALUES (?, ?, ?)",
                              (equipmentOptionId, connector_id, hasChoice))
        else:
            Db.cursor.execute("INSERT INTO EquipmentOption(equipOptionId, " + connector_type + "Id, hasChoice) "
                              "VALUES (?, ?, ?)", (equipmentOptionId, connector_id, hasChoice))

        # adds the options attached to this
        isTagBased = input("Are the items connected to this item specific or any from a tag? (specific/tag) ")

        # adds all items from a tag
        if isTagBased == "tag":
            tag = input("Enter the next items to add, by their common tag: ").replace("'", "''")
            amount = Db.int_input("Enter how much of this item they get: ")
            Db.cursor.execute("SELECT equipmentId FROM Equipment WHERE tags LIKE '%" + tag + "%'")
            results = Db.cursor.fetchall()
            for x in range(0, len(results)):
                Db.cursor.execute("INSERT INTO EquipmentIndivOption(equipmentId, equipmentOptionId, amnt) "
                                  "VALUES (?, ?, ?)", (results[x][0], equipmentOptionId, amount))
            # results currently will be something like [(1,), (4,)]
            path += " -> " + tag + " tag"

        # adds one or more specific items
        else:
            moreEquipment = True
            while moreEquipment:
                isRecursive = input("Does the next option to add involve a choice or multiple items? (Y/N) ")
                if isRecursive == "Y":
                    path += " -> Recursion"
                    equipmentOptionId = add_equipment_point(connector_type, equipmentOptionId, path)
                else:
                    name = input("Enter the next item to add, by it's equipment name: ")
                    amount = Db.int_input("Enter how much of this item they get: ")
                    Db.cursor.execute("INSERT INTO EquipmentIndivOption(equipmentId, equipmentOptionId, amnt) "
                                      "VALUES (?, ?, ?)", (Db.get_id(name, "Equipment"), equipmentOptionId, amount))
                moreEquipment = add_another_item()

            try:
                path += " -> " + name
            except UnboundLocalError:
                break

        print("Your most recently started EquipmentOption involving " + path + " is now complete.")
        addMore = add_another_item()
    return equipmentOptionId


def add_background_connections(background_id, skill_amnt, language_amnt, tool_amnt):
    """
    Adds appropriate rows into all tables that connect to a background, bar EquipmentOptions.
    :param background_id: the id of the current background being added
    :type background_id: int
    :param skill_amnt: the amount of skills the user chooses from the background
    :type skill_amnt: int
    :param language_amnt: the amount of languages the user chooses from the background
    :type language_amnt: int
    :param tool_amnt: the amount of tools the user chooses from the background
    :type tool_amnt: int
    """
    addSkill = (skill_amnt > 0)
    while addSkill:
        skillName = input("Enter the name of the next skill the background offers, 'ALL' for all or 'TAG' "
                          "followed by the tag for a subgroup: ")
        if skillName == "ALL":
            Db.cursor.execute("SELECT proficiencyId FROM Proficiency WHERE proficiencyType='Skill'")
            results = Db.cursor.fetchall()
            for x in range(0, len(results)):
                Db.cursor.execute("INSERT INTO BackgroundProficiency(backgroundId, proficiencyId) VALUES (?, ?)",
                                  (background_id, results[x][0]))
        elif skillName[0:3] == "TAG":
            Db.cursor.execute("SELECT proficiencyId FROM Proficiency WHERE proficiencyType LIKE '%" +
                              skillName[4:].replace("'", "''") + "%'")
            for result in Db.cursor.fetchall():
                Db.cursor.execute("INSERT INTO BackgroundProficiency(backgroundId, proficiencyId) VALUES(?, ?);",
                                  (background_id, result[0]))
        else:
            Db.cursor.execute("INSERT INTO BackgroundProficiency(backgroundId, proficiencyId) VALUES(?, ?);",
                              (background_id, Db.get_id(skillName, "Proficiency")))
        addSkill = add_another_item()

    addLang = (language_amnt > 0)
    while addLang:
        langName = input("Enter the name of the next language the background offers or 'ALL' for all: ")
        if langName == "ALL":
            Db.cursor.execute("SELECT languageId FROM Language")
            results = Db.cursor.fetchall()
            for x in range(0, len(results)):
                Db.cursor.execute("INSERT INTO BackgroundLanguage(backgroundId, languageId) VALUES (?, ?)",
                                  (background_id, results[x][0]))
        else:
            Db.cursor.execute("INSERT INTO BackgroundLanguage(backgroundId, languageId) VALUES(?, ?);",
                              (background_id, Db.get_id(langName, "Language")))
        addLang = add_another_item()

    addTool = (tool_amnt > 0)
    while addTool:
        toolName = input("Enter the name of the next tool the background offers, 'ALL' for all or 'TAG' "
                         "followed by the tag for a subgroup: ")
        if toolName == "ALL":
            Db.cursor.execute("SELECT proficiencyId FROM Proficiency WHERE proficiencyType='Tool'")
            results = Db.cursor.fetchall()
            for x in range(0, len(results)):
                Db.cursor.execute("INSERT INTO BackgroundProficiency(backgroundId, proficiencyId) VALUES (?, ?)",
                                  (background_id, results[x][0]))
        elif toolName[0:3] == "TAG":
            Db.cursor.execute("SELECT proficiencyId FROM Proficiency WHERE proficiencyType LIKE '%" +
                              toolName[4:].replace("'", "''") + "%'")
            for result in Db.cursor.fetchall():
                Db.cursor.execute("INSERT INTO BackgroundProficiency(backgroundId, proficiencyId) VALUES(?, ?);",
                                  (background_id, result[0]))
        else:
            Db.cursor.execute("INSERT INTO BackgroundProficiency(backgroundId, proficiencyId) VALUES(?, ?);",
                              (background_id, Db.get_id(toolName, "Proficiency")))
        addTool = add_another_item()


def add_language_connection(connector_type, connector_id, options_id, subconnector_id=-1):
    """
    Adds one or more languages to a race or class.
    :param connector_type: states whether the row connects to a class or race. It's inputs are 'Class' or 'Race'
    :type connector_type: str
    :param connector_id: the unique identifier for the row to add languages to
    :type connector_id: int
    :param options_id: the current amount of global options of the connector
    :type options_id: int
    :param subconnector_id: the id of the subrace or subclass it connects to, if appropriate
    :type subconnector_id: int, optional
    :return: the new current amount of global options of the connector
    """
    addElement = True
    # increments the raceOptions id and saves it as the id for non-optional languages
    options_id += 1
    add_options_connection(connector_type, options_id, connector_id, subconnector_id=subconnector_id)
    defaultOptionsId = options_id

    while addElement:
        nextLanguage = input("Enter the language to add to the race/class, or 'ALL' for a choice: ")

        if nextLanguage == "ALL":
            options_id += 1
            add_options_connection(connector_type, options_id, connector_id, subconnector_id, 1)
            Db.cursor.execute("SELECT languageId FROM Language")
            for languageId in Db.cursor.fetchall():
                Db.cursor.execute("INSERT INTO " + connector_type + "Language(" + connector_type.lower()
                                  + "OptionsId, language) VALUES(?, ?);", (options_id, languageId[0]))
        elif nextLanguage == "":
            return options_id
        else:
            nextLanguage = Db.get_id(nextLanguage, "Language")
            Db.cursor.execute("INSERT INTO " + connector_type + "Language(" + connector_type.lower()
                              + "OptionsId, language) VALUES(?, ?);", (defaultOptionsId, nextLanguage))
        addElement = add_another_item()
    return options_id


def add_proficiency_connection(connector_type, connector_id, options_id, subconnector_id=-1):
    """
    Adds one or more proficiencies to a race or class.
    :param connector_type: states whether the row connects to a class or race. It's inputs are 'Class' or 'Race'
    :type connector_type: str
    :param connector_id: the unique identifier for the row to add proficiencies to
    :type connector_id: int
    :param options_id: the current amount of global options of the connector
    :type options_id: int
    :param subconnector_id: the id of the subrace or subclass it connects to, if appropriate
    :type subconnector_id: int, optional
    :return: the new current amount of global options of the connector
    """
    addElement = True
    # increments the raceOptions id and saves it as the id for non-optional proficiencies
    options_id += 1
    add_options_connection(connector_type, options_id, connector_id, subconnector_id=subconnector_id)
    defaultOptionsId = options_id

    while addElement:
        nextProf = input("Enter the proficiency to add to the race/class, "
                         "'CHOICE' for a choice, or enter for none: ")
        expertise = input("Does this option get expertise? (Y/N) ") == "Y"
        # if it's a choice, enter the options
        if nextProf == "CHOICE":
            options_id += 1
            amnt = Db.int_input("How many of these do they choose? ")
            if expertise:
                expertiseNum = Db.int_input("How many of these get expertise? ")
            else:
                expertiseNum = 0
            add_options_connection(connector_type, options_id, connector_id, subconnector_id, amnt)

            # enter a tag of choices or several individual choices
            tagOrIndiv = input("Are these choices from a TAG or INDIVIDUAL? ")
            if tagOrIndiv == "TAG":
                tag = input("Please input the tag they choose from: ")
                Db.cursor.execute("SELECT proficiencyId FROM Proficiency WHERE proficiencyType LIKE '%" +
                                  tag.replace("'", "''") + "%'")
                for proficiencyId in Db.cursor.fetchall():
                    Db.cursor.execute("INSERT INTO " + connector_type + "Proficiency(" + connector_type.lower() +
                                      "OptionsId, proficiencyId, expertise, expertiseNum) VALUES(?, ?, ?, ?);",
                                      (options_id, proficiencyId[0], expertise, expertiseNum))
            else:
                optionAmnt = Db.int_input("How many individual options are there? ")
                for x in range(0, optionAmnt):
                    nextProf = input("Enter the next proficiency option: ")
                    nextProf = Db.get_id(nextProf, "Proficiency")
                    Db.cursor.execute("INSERT INTO " + connector_type + "Proficiency(" + connector_type.lower() +
                                      "OptionsId, proficiencyId, expertise) VALUES(?, ?, ?);",
                                      (options_id, nextProf, expertise))
            print("The optional proficiencies have been complete.")
        elif nextProf == "":
            return options_id
        # otherwise, connect it to the non-optional raceOptions row
        else:
            nextProf = Db.get_id(nextProf, "Proficiency")
            Db.cursor.execute("INSERT INTO " + connector_type + "Proficiency(" + connector_type.lower() +
                              "OptionsId, proficiencyId, expertise) VALUES(?, ?, ?);",
                              (defaultOptionsId, nextProf, expertise))
        addElement = add_another_item()
    return options_id


def add_race_spell(race_id, race_options_id, subrace_id=-1):
    """
    Adds one or more spells to a race.
    :param race_id: the unique identifier for the race to add spells to
    :type race_id: int
    :param race_options_id: the current amount of global race options
    :type race_options_id: int
    :param subrace_id: the id of the subrace it connects to, if appropriate
    :type subrace_id: int, optional
    :return: the new current amount of global race options
    """
    addElement = True
    # increments the raceOptions id and saves it as the id for non-optional proficiencies
    race_options_id += 1
    add_options_connection("Race", race_options_id, race_id, subconnector_id=subrace_id)

    while addElement:
        nextSpell = input("Enter the spell to add to the race: ")
        if nextSpell == "":
            return race_options_id
        spellLvl = Db.int_input("Enter the level the spell is cast at: ")
        chrLvl = Db.int_input("Enter the level the character can cast the spell at: ")
        modUsed = input("Enter the first 3 letters of the modifier used: ")
        nextSpell = Db.get_id(nextSpell, "Spell")
        Db.cursor.execute("INSERT INTO RaceSpell(raceOptionsId, spellId, spellLevel, characterLevel, modifierUsed"
                          ") VALUES(?, ?, ?, ?, ?);", (race_options_id, nextSpell, spellLvl, chrLvl, modUsed))

        addElement = add_another_item()
    return race_options_id


def add_class_magic(class_id, lvl, subclass_id=-1):
    """
    Adds the magic data for a classes level, building up from the previous level if appropriate.
    :param class_id: the unique identifier for the class it's assigned to
    :type class_id: int
    :param lvl: the level at which this magic is accessible to the class
    :type lvl: int
    :param subclass_id: the unique identifier of the subclass required for the class to gain access to this, or -1
    :type subclass_id: int, optional
    """
    Db.cursor.execute("SELECT COUNT(*) FROM Magic")
    magicId = Db.cursor.fetchone()[0] + 1
    spellsPrepared = input("Are the spells prepared during a long rest? (Y/N) ") == "Y"
    cantripsKnown = Db.int_input("Enter how many cantrips are known at this stage: ")
    if spellsPrepared:
        knownCalc = input("Enter how the amount of spells are calculated: ")
        if subclass_id > -1:
            Db.cursor.execute("INSERT INTO Magic(magicId, classId, subclassId, spellsPrepared, knownCalc, "
                              "lvl, cantripsKnown) VALUES(?, ?, ?, ?, ?, ?, ?);",
                              (magicId, class_id, subclass_id, spellsPrepared, knownCalc, lvl, cantripsKnown))
        else:
            Db.cursor.execute("INSERT INTO Magic(magicId, classId, spellsPrepared, knownCalc, lvl, "
                              "cantripsKnown) VALUES(?, ?, ?, ?, ?, ?);",
                              (magicId, class_id, spellsPrepared, knownCalc, lvl, cantripsKnown))
    else:
        amntKnown = Db.int_input("Enter how many spells are known at this stage: ")
        if subclass_id > -1:
            Db.cursor.execute("INSERT INTO Magic(magicId, classId, subclassId, spellsPrepared, knownCalc, "
                              "amntKnown, lvl, cantripsKnown) VALUES(?, ?, ?, ?, ?, ?, ?, ?);",
                              (magicId, class_id, subclass_id, spellsPrepared, "ALL",
                               amntKnown, lvl, cantripsKnown))
        else:
            Db.cursor.execute("INSERT INTO Magic(magicId, classId, spellsPrepared, knownCalc, amntKnown, lvl"
                              ", cantripsKnown) VALUES(?, ?, ?, ?, ?, ?, ?);",
                              (magicId, class_id, spellsPrepared, "ALL", amntKnown, lvl, cantripsKnown))

    # If it's not the first level, add all previous spells and slots to the class magic
    if lvl > 1:
        Db.cursor.execute("SELECT magicId FROM Magic WHERE lvl=" + str(lvl - 1) +
                          " AND classId=" + str(class_id))
        prevMagicId = str(Db.cursor.fetchone()[0])
        Db.cursor.execute("SELECT spellslotLvl, amount FROM ClassSpellslot WHERE magicId=" + prevMagicId)
        for slot in Db.cursor.fetchall():
            Db.cursor.execute("INSERT INTO ClassSpellslot(magicId, spellslotLvl, amount) VALUES (?, ?, ?);",
                              (magicId, slot[0], slot[1]))
        Db.cursor.execute("SELECT spellId FROM ClassSpell WHERE magicId=" + prevMagicId)
        for spell in Db.cursor.fetchall():
            Db.cursor.execute("INSERT INTO ClassSpell(magicId, spellId) VALUES (?, ?);",
                              (magicId, spell[0], spell[1]))

    # Add spellslots
    addMore = input("Does the class gain any new spellslots from the previous level? (Y/N) ") == "Y"
    while addMore:
        spellslotLvl = Db.int_input("What's the level of the new spellslot gained: ")
        isNew = input("Is the new spellslot the first of it's level? (Y/N) ") == "Y"
        if isNew:
            amount = Db.int_input("How many of these slots does the class get: ")
            Db.cursor.execute("INSERT INTO ClassSpellslot(magicId, spellslotLvl, amount) VALUES(?, ?, ?)",
                              (magicId, spellslotLvl, amount))
        else:
            amount = Db.int_input("How many of these slots does the class now have: ")
            Db.cursor.execute("UPDATE TABLE ClassSpellslot SET amount=" + str(amount) + " WHERE magicId=" +
                              str(magicId) + " AND spellslotLvl=" + str(spellslotLvl))
        addMore = add_another_item()
    print("All spellslots have been added\n")

    # Add spells
    addMore = input("Does the class gain any new spells from the previous level? (Y/N) ") == "Y"
    while addMore:
        spellId = input("Enter the name of the next new spell gained: ")
        spellId = Db.get_id(spellId, "Spell")
        Db.cursor.execute("INSERT INTO ClassSpell(magicId, spellId) VALUES (?, ?);", (magicId, spellId))
        addMore = add_another_item()
    print("All spells have been added\n")


def add_class_traits(class_id, class_options_id, subclass_id=-1):
    """
    Adds one or more traits to a class.
    :param class_id: the unique identifier of the class to add to
    :type class_id: int
    :param class_options_id: the current total amount of ClassOptions rows
    :type class_options_id: int
    :param subclass_id: the unique identifier of the subclass to add to, if appropriate
    :type subclass_id: int, optional
    :return: the new total amount of ClassOptions rows
    """
    class_options_id += 1
    choiceOptionsId = class_options_id
    add_options_connection("Class", class_options_id, class_id, subclass_id)
    addElement = True
    while addElement:
        nextTrait = input("Enter the name of the trait to add, CHOICE for a choice, or enter for none: ")
        if nextTrait == "CHOICE":
            choiceOptionsId += 1
            amnt = Db.int_input("How many options are there: ")
            picks = Db.int_input("How many do they pick: ")
            add_options_connection("Class", choiceOptionsId, class_id, subclass_id, picks)
            for x in range(0, amnt):
                nextTraitChoice = input("Enter the name of the next trait option: ")
                nextTraitChoice = Db.get_id(nextTraitChoice, "Trait")
                Db.cursor.execute("INSERT INTO ClassTrait(classOptionsId, traitId) VALUES(?, ?);",
                                  (choiceOptionsId, nextTraitChoice))

        elif nextTrait != "":
            nextTrait = Db.get_id(nextTrait, "Trait")
            Db.cursor.execute("INSERT INTO ClassTrait(classOptionsId, traitId) VALUES(?, ?);",
                              (class_options_id, nextTrait))
            addElement = add_another_item()
        else:
            addElement = False
    return choiceOptionsId


# ADD NON-CONNECTED ROWS


def add_spell(spell_id, name, level, casting_time, duration, spell_range, components, attack_or_save,
              school, damage_or_effect, description, area, tags):
    """
    Adds a single spell to the database, adjusting the call based on available data.
    :param spell_id: The unique id of the next spell
    :type spell_id: str
    :param name: The spells name
    :type name: str
    :param level: the minimum level that the spell can be cast at
    :type level: imt
    :param casting_time: the casting time of the spell
    :type casting_time: str
    :param duration: the duration the spell lasts for
    :type duration: str
    :param spell_range: the range of the spell
    :type spell_range: imt
    :param components: the components used to cast the spell
    :type components: str
    :param attack_or_save: the attack roll or save type of the spell
    :type attack_or_save: str
    :param school: the school the spell is a member of
    :type school: str
    :param damage_or_effect: the damage amount and type, as well as spell tags
    :type damage_or_effect: str
    :param description: the description of how the spell works
    :type description: str
    :param area: the area and size kind of the spell
    :type area: str
    :param tags: the tags that applies to the spell
    :type tags: str
    """
    insertCall1 = "INSERT INTO Spell(spellId, spellName, spellLevel, castingTime, duration, range, area, " \
                  "components, attackOrSave, school, damageOrEffect, description) " \
                  "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"
    insertCall2 = "INSERT INTO Spell(spellId, spellName, spellLevel, castingTime, duration, range, components, " \
                  "attackOrSave, school, damageOrEffect, description) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"

    if area != "":
        Db.cursor.execute(insertCall1, (spell_id, name, level, casting_time, duration, spell_range, area,
                                        components, attack_or_save, school, damage_or_effect, description))
    else:
        Db.cursor.execute(insertCall2, (spell_id, name, level, casting_time, duration, spell_range, components,
                                        attack_or_save, school, damage_or_effect, description))
    for tag in tags.split(", "):
        Db.cursor.execute("INSERT INTO SpellTag(genericTagId, spellId) VALUES(?, ?)",
                          (Db.get_id(tag, "GenericTag"), spell_id))


def add_spells():
    """
    Adds one or more spells to the database.
    """
    Db.cursor.execute("SELECT COUNT(*) FROM Spell")
    spellId = Db.cursor.fetchone()[0]
    addMore = True
    while addMore:
        spellId += 1
        name = input("Enter the spell name: ")
        level = Db.int_input("Enter the spells' level: ")
        castingTime = input("Enter the spells' casting time: ")
        duration = input("Enter the spells' duration: ")
        spellRange = Db.int_input("Enter the spells' range: ")
        area = input("Enter the spells' area if applicable, or press enter otherwise: ")
        components = input("Enter the component initials, separated by a comma & space: ")
        attackOrSave = input("Enter 'attack' if the spell attacks, or enter the first three capitalised letters and"
                             " ' save' of the saving throw's ability: ")
        school = input("Enter the spells' magic school: ")
        damageOrEffect = input("Enter the dice or number, and damage or effect type, of the spell: ")
        description = input("Enter the spells' description: ")
        tags = input("Enter the spells' tags: ")
        add_spell(spellId, name, level, castingTime, duration, spellRange, components, attackOrSave, school,
                  damageOrEffect, description, area, tags)

        addMore = add_another_item()


def add_proficiencies():
    """
    Adds one or more proficiencies to the database.
    """
    Db.cursor.execute("SELECT COUNT(*) FROM Proficiency")
    proficiencyId = Db.cursor.fetchone()[0]
    addMore = True
    while addMore:
        proficiencyId += 1
        proficiencyName = input("Enter the proficiency to add ")
        proficiencyType = input("Enter the proficiency type ")
        Db.cursor.execute("INSERT INTO Proficiency(proficiencyId, proficiencyName, proficiencyType) "
                          "VALUES(?, ?, ?);", (proficiencyId, proficiencyName, proficiencyType))

        addMore = add_another_item()


def add_languages():
    """
    Adds one or more languages to the database.
    """
    Db.cursor.execute("SELECT COUNT(*) FROM Language")
    languageId = Db.cursor.fetchone()[0]
    addMore = True
    while addMore:
        languageId += 1
        language = input("Enter the language to add ")
        Db.cursor.execute("INSERT INTO Language(languageId, languageName) VALUES(?, ?);", (languageId, language))

        addMore = add_another_item()


def add_equipment():
    """
    Adds one or more pieces of equipment to the database.
    """
    Db.cursor.execute("SELECT COUNT(*) FROM Equipment")
    equipmentId = Db.cursor.fetchone()[0]
    addMore = True
    while addMore:
        equipmentId += 1
        equipmentName = input("Enter the equipment name to add ")
        tags = input("Enter the equipment tags, separated with a comma ")
        description = input("Enter the equipment description ")
        diceNum = input("Enter the amount of dice it uses ")
        diceSides = input("Enter the amount of sides on the dice it uses ")
        armorClass = input("Enter the armor class it provides ")
        weight = input("Enter it's weight, in lb ")
        value = input("Enter its value, in the form '1GP, 3SP, 7CP', for example ")

        usedValues = []
        sqlValues = ["description", "diceNum", "diceSides", "armorClass", "weight", "value"]
        count = 0
        for value in [description, diceNum, diceSides, armorClass, weight, value]:
            if value is not None:
                usedValues.append([value, count])
            count += 1

        sqlCall = "INSERT INTO Equipment(equipmentId, equipmentName"
        sqlEnd = ") VALUES(?, ?, ?"
        sqlParams = (equipmentId, equipmentName)
        for pair in usedValues:
            sqlCall += ", " + sqlValues[pair[1]]
            sqlEnd += ", ?"
            sqlParams += (pair[0],)
        sqlCall += sqlEnd + ");"

        Db.cursor.execute(sqlCall, sqlParams)
        for tag in tags.split(", "):
            Db.cursor.execute("INSERT INTO EquipmentTag(genericTagId, equipmentId) VALUES(?, ?)",
                              (Db.get_id(tag, "GenericTag"), equipmentId))

        addMore = add_another_item()
