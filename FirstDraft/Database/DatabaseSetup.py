import sqlite3 as sql


class DatabaseSetup:
    connection = sql.connect("Database/ChrDatabase.db")
    cursor = connection.cursor()

    @staticmethod
    def setup_tables():
        """
        Sets up all the database tables by running through the text file.
        """
        count = 0
        nextCommand = ""

        with open("Database/DatabaseTables.txt") as file:
            while True:
                count += 1
                line = file.readline()

                if not line:
                    break

                if line[:2] != "--" and len(line) > 1:
                    nextCommand += line
                else:
                    DatabaseSetup.cursor.execute(nextCommand)
                    nextCommand = ""
        file.close()

    @staticmethod
    def complete_setup():
        """
        Commits and closes the database connection, ensuring all edits are saved.
        :return:
        """
        DatabaseSetup.connection.commit()
        DatabaseSetup.connection.close()

    @staticmethod
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

    @staticmethod
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



    def remove_item(self, table, item_id=None, name=None):
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
            sqlCall = "DELETE FROM " + table + " WHERE " + table.lower() + "Id=" + item_id
        self.cursor.execute(sqlCall)

    def add_item(self):
        """
        Produces a simple text menu to allow the user to select which kind of item they wish to add.
        This is used for simple navigation during the database filling process.
        """
        print("Choose one of the options below to add, or 9 to exit:\n"
              "1. Spells\n"
              "2. Languages\n"
              "3. Proficiencies\n"
              "4. Equipment\n"
              "9. Exit\n")
        value = self.int_input("> ")
        if value == 1:
            self.add_spells()
        elif value == 2:
            self.add_languages()
        elif value == 3:
            self.add_proficiencies()
        elif value == 4:
            self.add_equipment()
        else:
            SystemExit(0)

    def print_added_data(self):
        """
        Prints all the currently added data, in long strings that start with the data groups. For example, a line
        beginning with 'Spells:' shows all the names of spells that have been added.
        This is used for consistency and checkup during the database filling process.
        """
        self.cursor.execute("SELECT spellName FROM Spell")
        spells = sorted(self.cursor.fetchall())
        spellStr = ""
        for spell in spells:
            spellStr += spell[0] + ", "
        print("Spells: " + spellStr)

        self.cursor.execute("SELECT proficiencyName FROM Proficiency")
        proficiencies = sorted(self.cursor.fetchall())
        profStr = ""
        for proficiency in proficiencies:
            profStr += proficiency[0] + ", "
        print("Proficiencies: " + profStr)

        self.cursor.execute("SELECT languageName FROM Language")
        languages = sorted(self.cursor.fetchall())
        langStr = ""
        for language in languages:
            langStr += language[0] + ", "
        print("Languages: " + langStr)

        self.cursor.execute("SELECT equipmentName FROM Equipment")
        equipment = sorted(self.cursor.fetchall())
        equipStr = ""
        for equip in equipment:
            equipStr += equip[0] + ", "
        print("Equipment: " + equipStr)

    def get_id(self, name, table):
        """
        Gets the id of a row from their table and name.
        :param name: the name of the row to be found
        :type name: str
        :param table: the table the row is located in
        :type table: str
        :return: the integer value of the data's id
        """
        self.cursor.execute(
            "SELECT " + table.lower() + "Id from " + table + " WHERE " + table.lower() + "Name='" + name + "'")
        return int(self.cursor.fetchone()[0])



    # ADD NON-CONNECTED ROWS

    def add_spells(self):
        """
        Adds one or more spells to the database.
        """
        self.cursor.execute("SELECT COUNT(*) FROM Spell")
        spellId = self.cursor.fetchone()[0]
        addMore = True
        while addMore:
            spellId += 1
            name = input("Enter the spell name: ")
            level = self.int_input("Enter the spells' level: ")
            castingTime = input("Enter the spells' casting time: ")
            duration = input("Enter the spells' duration: ")
            spellRange = self.int_input("Enter the spells' range: ")
            area = input("Enter the spells' area if applicable, or press enter otherwise: ")
            components = input("Enter the component initials, separated by a comma & space: ")
            attackOrSave = input("Enter 'attack' if the spell attacks, or enter the first three capitalised letters and"
                                 " ' save' of the saving throw's ability: ")
            school = input("Enter the spells' magic school: ")
            damageOrEffect = input("Enter the dice or number, and damage or effect type, of the spell: ")
            description = input("Enter the spells' description: ")
            self.add_spell(spellId, name, level, castingTime, duration, spellRange, components, attackOrSave, school,
                           damageOrEffect, description, area)

            addMore = self.add_another_item()

    def add_spell(self, spell_id, name, level, casting_time, duration, spell_range, components, attack_or_save,
                  school, damage_or_effect, description, area):
        """
        Adds a single spell to the database, adjusting the call based on available data.
        :param spell_id: The unique id of the next spell
        :type spell_id: str
        :param name: The spells name
        :type name: str
        :param level: the minimum level that the spell can be cast at
        :type level: str
        :param casting_time: the casting time of the spell
        :type casting_time: str
        :param duration: the duration the spell lasts for
        :type duration: str
        :param spell_range: the range of the spell
        :type spell_range: str
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
        """
        insertCall1 = "INSERT INTO Spell(spellId, spellName, spellLevel, castingTime, duration, range, area, " \
                      "components, attackOrSave, school, damageOrEffect, description) " \
                      "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"
        insertCall2 = "INSERT INTO Spell(spellId, spellName, spellLevel, castingTime, duration, range, components, " \
                      "attackOrSave, school, damageOrEffect, description) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"

        if area != "":
            self.cursor.execute(insertCall1, (spell_id, name, level, casting_time, duration,
                                              spell_range, area, components, attack_or_save, school,
                                              damage_or_effect, description))
        else:
            self.cursor.execute(insertCall2, (spell_id, name, level, casting_time, duration,
                                              spell_range, components, attack_or_save, school,
                                              damage_or_effect, description))

    def add_proficiencies(self):
        """
        Adds one or more proficiencies to the database.
        """
        self.cursor.execute("SELECT COUNT(*) FROM Proficiency")
        proficiencyId = self.cursor.fetchone()[0]
        addMore = True
        while addMore:
            proficiencyId += 1
            proficiencyName = input("Enter the proficiency to add ")
            proficiencyType = input("Enter the proficiency type ")
            self.cursor.execute(
                "INSERT INTO Proficiency(proficiencyId, proficiencyName, proficiencyType) VALUES(?, ?, ?);",
                (proficiencyId, proficiencyName, proficiencyType))

            addMore = self.add_another_item()

    def add_languages(self):
        """
        Adds one or more languages to the database.
        """
        self.cursor.execute("SELECT COUNT(*) FROM Language")
        languageId = self.cursor.fetchone()[0]
        addMore = True
        while addMore:
            languageId += 1
            language = input("Enter the language to add ")
            self.cursor.execute("INSERT INTO Language(languageId, languageName) VALUES(?, ?);", (languageId, language))

            addMore = self.add_another_item()

    def add_equipment(self):
        """
        Adds one or more pieces of equipment to the database.
        """
        self.cursor.execute("SELECT COUNT(*) FROM Equipment")
        equipmentId = self.cursor.fetchone()[0]
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

            sqlCall = "INSERT INTO Equipment(equipmentId, equipmentName, tags"
            sqlEnd = ") VALUES(?, ?, ?"
            sqlParams = (equipmentId, equipmentName, tags)
            for pair in usedValues:
                sqlCall += ", " + sqlValues[pair[1]]
                sqlEnd += ", ?"
                sqlParams += (pair[0],)
            sqlCall += sqlEnd + ");"

            self.cursor.execute(sqlCall, sqlParams)

            addMore = self.add_another_item()

