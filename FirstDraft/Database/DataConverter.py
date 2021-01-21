from Database import DataExtractor, CoreDatabase as Db
from CharacterElements import Character, Class, Equipment, Race, Spell



def make_choice(num_of_choices, choices):
    """
    Lets the user choose a certain amount of items from an array of options.
    Any use of this should be replaced with the optimising algorithm when possible.
    :param num_of_choices: how many of the choices must be selected
    :type num_of_choices: int
    :param choices: a list of the choices available
    :type choices: list
    :return: a list of the choices selected
    """
    output = []
    if num_of_choices >= len(choices):
        output = choices
    else:
        choiceCount = []
        choiceDict = dict()

        # converts any list choices into a single string, directing a dictionary to the list of objects
        for x in range(0, len(choices)):
            if type(choices[x]) is list:
                fullStr = ""
                for y in list({i: choices[x].count(i) for i in choices[x]}.items()):
                    fullStr += f"({str(y[1])}x) {str(y[0])}\n"
                choiceDict.update({fullStr: choices[x]})
            else:
                choiceCount.append(choices[x])

        # puts all single-object choices into the dictionary,
        # linking their string to the appropriate amount of the object
        choiceCount = list({i: choiceCount.count(i) for i in choiceCount}.items())
        for z in range(0, len(choiceCount)):
            objects = []
            for l in range(0, choiceCount[z][1]):
                objects.append(choiceCount[z][0])
            choiceDict.update({f"({choiceCount[z][1]}x) {str(choiceCount[z][0])}": objects})

        # lists their options
        while len(output) < num_of_choices:
            print("Choose one from: ")
            counter = 0
            for key in list(choiceDict.keys()):
                counter += 1
                print(str(counter) + ".\n" + key)

            nextAddition = Db.int_input(">") - 1
            if nextAddition < len(choiceDict.keys()):
                output.append(list(choiceDict.values())[nextAddition])
                choiceDict.pop(list(choiceDict.keys())[nextAddition])
    return list(*output)




def create_background(background_name):
    """
    Creates and returns a background object, given the name of the background to use.
    :param background_name: the name of the background selected
    :type background_name: str
    :return: a python object representing the background
    """
    tools, skills, languages = DataExtractor.background_connections(background_name)
    finalProfs, finalLanguages = [], []

    finalProfs += make_choice(tools[0], tools[1])
    finalProfs += make_choice(skills[0], skills[1])
    finalLanguages = make_choice(languages[0], languages[1])

    return Character.Background(background_name, finalProfs, finalLanguages)


def create_class(class_name, class_lvl, subclass=None):      # INCOMPLETE
    """
    Creates and returns a class object, given the name of the class to use.
    :param class_name: the name of the class selected
    :type class_name: str
    :param class_lvl: the level to build the class at
    :type class_lvl: int
    :param subclass: the subclass to add to this object
    :type subclass: object
    :return: a python object representing the class
    """
    classId = Db.get_id(class_name, "Class")
    Db.cursor.execute("SELECT hitDiceSides, primaryAbility, secondaryAbility, isMagical FROM Class WHERE classId="
                      + str(classId))
    hitDice, primaryAbility, secondaryAbility, isMagical = Db.cursor.fetchone()

    traits, proficiencies, languages = collect_class_option_data(class_name, class_lvl)
    equipment = []   # EXTRACT EQUIPMENT

    if isMagical:
        magic = []   # EXTRACT MAGIC
        return Class.Class(class_name, traits, proficiencies, equipment, primaryAbility, secondaryAbility,
                           hitDice, languages, class_lvl, magic, subclass)
    else:
        return Class.Class(class_name, traits, proficiencies, equipment, primaryAbility, secondaryAbility,
                           hitDice, languages, class_lvl, subclass=subclass)


def collect_class_option_data(class_name, class_lvl):
    """
    Extracts the class options data from the class database.
    :param class_name: the name of the class selected
    :type class_name: str
    :param class_lvl: the level to build the class at
    :type class_lvl: int
    :return: a python object representing the class
    """
    traits, proficiencies, languages = [], [], []
    Db.cursor.execute("SELECT classOptionsId FROM ClassOptions WHERE classId=" + str(
        Db.get_id(class_name, "Class")) + " AND subclassId IS NULL")
    ids = Db.cursor.fetchall()
    for nextId in ids:
        metadata, options = DataExtractor.class_options_connections(nextId[0])
        if metadata[0] <= class_lvl:
            if metadata[2] == "traits":
                traits = make_choice(metadata[1], options)
            elif metadata[2] == "proficiencies":
                proficiencies = make_choice(metadata[1], options)
            else:
                languages = make_choice(metadata[1], options)
    return traits, proficiencies, languages


def create_all_equipment():
    """
    Creates an object for each equipment item in the database.
    """
    equipmentData = DataExtractor.equipment_items()
    for equip in equipmentData:
        for x in range(0, len(equip)):
            if equip[x] == "":
                equip[x] = 0
        if type(equip[-1]) is list:
            Equipment.Equipment(*equip[:-1], item_range=equip[-1])
        else:
            Equipment.Equipment(*equip)


def create_equipment(class_name):
    optionsData = DataExtractor.equipment_connections(Db.get_id(class_name, "Class"))
    equipment = []
    for option in optionsData:
        equipment += create_equipment_option(option)[1]
    return equipment


def create_equipment_option(option):
    """
    Creates a single equipment option set.
    :param option: a list of metadata and objects in the option,
    in the layout [[isChoice boolean, [optional subsection]], [equipment objects]]
    :return: whether the option was a choice, and a list of the equipment objects selected
    """
    metadata, items = option
    itemChoices = items
    if len(metadata) > 1:
        for subsection in metadata[1:]:
            choice, subsectionVal = create_equipment_option(subsection)
            items += subsectionVal
            if choice is False:
                for x in range(0, len(subsectionVal)):
                    itemChoices.remove(subsectionVal[x])
                itemChoices.append(subsectionVal)

    if metadata[0] is True:
        equipment = make_choice(1, itemChoices)
    else:
        equipment = items
    return metadata[0], equipment



def begin():
    output = create_equipment("Bard")
    for item in output:
        print(item.name)

