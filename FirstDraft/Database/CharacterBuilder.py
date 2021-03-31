import itertools
from collections import Counter

import numpy as np

from CharacterElements import Character
from Database import CoreDatabase as Db, DataConverter


def take_choices(choices):
    """
    Takes a 3D array of decided choices and where each can be from, and calculates options.
    :param choices: a 3D array, in the layout [[choice, choiceType, [where from]]
    :type choices: list
    :return a dictionary of the results, or -1 if the passed requirements are impossible
    """
    allOptions = dict()
    optionCount = []
    for [choice, choiceType, placesFrom] in choices:
        if choiceType in ("Class", "Race", "Background", "Subrace", "Subclass"):
            nextResult = {choice: [choiceType + ": " + choice]}
        else:
            nextResult = extract_choice(choice, choiceType, placesFrom)
        allOptions.update(nextResult)
        optionCount += itertools.chain(*nextResult.values())
    optionCount = Counter(optionCount)

    result = option_combos(allOptions, optionCount)
    if len(result) == 0:
        if len(choices) > 0:
            print("You've asked for impossible requirements")
        return -1
    else:
        return result


def extract_choice(choice, choice_loc, places_from):
    """
    Extracts all the potential options that the choice could be taken from.
    :param choice: the choice to make
    :type choice: str
    :param choice_loc: what table the choice comes from to, such as proficiency
    :type choice_loc: str
    :param places_from: where this choice can potentially come from
    :type places_from: list
    :return: a 2D array of the choice and it's options, where each option is the name of a row within one of the
             placesFrom tables
    """
    options = []
    choiceLocLower = choice_loc.lower()
    for place in places_from:
        basePlace = place[0].lower() + place[1:]
        place = place.replace("Options", "")
        choice = choice.replace("'", "''")

        call = f"SELECT {basePlace}Id FROM {place}{choice_loc} WHERE {choiceLocLower}Id IN (" \
               f"SELECT {choiceLocLower}Id FROM {choice_loc} WHERE {choiceLocLower}Name='{choice}'))"

        if "Options" in basePlace:
            call = f"SELECT {place.lower()}Name FROM {place} WHERE {place.lower()}Id IN (" \
                   f"SELECT {place.lower()}Id FROM {basePlace.capitalize()} WHERE {basePlace}Id IN (" + call + ")"
        elif choice_loc == "Equipment":
            call = f"SELECT className FROM Class WHERE classId IN (" \
                   f"SELECT classId FROM EquipmentOption WHERE equipOptionId IN (" \
                   f"SELECT equipmentOptionId FROM EquipmentIndivOption WHERE equipmentId=(" \
                   f"SELECT equipmentId FROM Equipment WHERE equipmentName='{choice}')))"
        elif choice_loc == "Spell":
            call = f"SELECT {basePlace}Name FROM {place} WHERE {basePlace}Id IN ("
            if place == "Race":
                call += "SELECT raceId FROM RaceOptions WHERE raceOptionsId IN (" \
                        "SELECT raceOptionsId FROM RaceSpell WHERE spellId IN ("
            else:
                call += "SELECT classId FROM Magic WHERE magicId IN (" \
                        "SELECT magicId FROM ClassSpell WHERE spellId IN ("
            call += f"SELECT spellId FROM Spell WHERE spellName='{choice}')))"
        else:
            call = f"SELECT {basePlace}Name FROM {place} WHERE {basePlace}Id IN (" + call

        Db.cursor.execute(call)
        for result in itertools.chain(*Db.cursor.fetchall()):
            options.append(place + ": " + result)
    return {choice: options}


def option_combos(options, option_counter):
    """
    Takes in the current options and finds a combination to achieve all of them.
    :param options: a dictionary that links the choice with it's options
    :type options: dict
    :param option_counter: a dictionary saying how many occurrences each option has throughout
    :type option_counter: dict
    :return: a dictionary of the choices made for the character, linking the class/race/etc choice to an array of the
             options it fulfills
    """
    unmetChoices = set()
    for key in option_counter.keys():
        unmetChoices.add(key.split(":")[0])
    choicesMade = dict()
    # for each array of options linked to one choice, in order of the lowest amount of options
    optionItems = sorted(options, key=lambda k: len(options[k]))
    for nextKey in optionItems:
        nextValues = options[nextKey]
        # if it's an impossible build, return an empty array
        if len(nextValues) == 0:
            return []

        bestOpt = nextValues[0]
        # for each option in the array of options
        for nextVal in nextValues:
            # if the option is valid and better than the current best, replace with this
            if (nextVal in choicesMade) or (nextVal.split(":")[0] in unmetChoices):
                if option_counter[nextVal] > option_counter[bestOpt] or (nextVal in choicesMade):
                    bestOpt = nextVal
        choicesMade[bestOpt] = choicesMade.get(bestOpt, []) + [nextKey]
        option_counter[bestOpt] -= 1
        try:
            unmetChoices.remove(bestOpt.split(":")[0])
        except KeyError:
            pass
    return order_outputs(choicesMade)


def order_outputs(selections):
    """
    Orders selections into an easier to access layout.
    :param selections: the selections to choose, in a dictionary of "type: choice": [subchoices]
    :type selections: dict
    :return: a dictionary of the items, in the layout "type": (choice, [subchoices])
    """
    selectionDict = dict()
    for selection, subchoices in selections.items():
        splitSelect = selection.split(": ")
        selectionDict.update({splitSelect[0]: (splitSelect[1], subchoices)})
    return selectionDict


def change_filter(character, filters, element, modifier):
    """
    Modifies one filter in a dictionary of chromosome filters.
    :param character: the character that is being adjusted
    :type character: class: `CharacterElements.Character`
    :param filters: the dictionary of filters used to make a full character
    :type filters: dict
    :param element: the element to modify within this, listed as it's dictionary key
    :type element: str
    :param modifier: the modifier number produced, used to help randomise adjustment
    :type modifier: int
    :return: newly modified filters
    """
    # Race, Class, Background - any option
    # subrace, subclass - based on race/class
    # Languages, Proficiencies, Skills - class, race or background
    # if possible, it should avoid changing the parent factor that affects it(try not to change class to change skills)
    if element in ("Race", "Class", "Subrace", "Subclass"):
        filters = change_core_filter(filters, element, modifier, character)

    elif element in ("Subrace", "Subclass"):
        # maybe use core filters, with some modifier to keep it within the same race/class
        pass

    elif element == "Background":
        change_background_filter(filters, character, modifier)

    elif element == "Spells":
        filters = change_spell_filter(character, filters, modifier)

    elif element == "Equipment":
        currentEquip = [e.name for e in character.chrClass.equipment]
        filters = change_equipment_filter(currentEquip, filters, modifier)

    else:
        # languages, proficiencies or skills
        if element == "Proficiencies":
            elementSingular = "Proficiency"
        else:
            elementSingular = element[:-1]
        filters = change_basic_filter(character, filters, modifier, element, elementSingular)

    return filters


def change_core_filter(filters, element, modifier, character, subset=None):
    """
    Modifies a core filter, trying to keep all other filters as similar as possible in the process.
    A core filter refers to Race, Class and Background - the three top-end elements.
    Modifies one filter in a dictionary of chromosome filters.
    :param filters: the dictionary of filters used to make a full character
    :type filters: dict
    :param element: the element to modify within this, listed as it's dictionary key
    :type element: str
    :param modifier: the modifier number produced, used to help randomise adjustment
    :type modifier: int
    :param character: the character that is being adjusted
    :type character: class: `CharacterElements.Character`
    :param subset: a subset of options the new change must be from
    :type subset: list, optional
    :return: newly modified filters
    """
    # if no subset is provided, set it to all potential options that aren't the current option
    if subset is None:
        sqlCall = f"SELECT {element.lower()}Name FROM {element} " \
                  f"WHERE {element.lower()}Name != '{filters[element]}'"
        if "Sub" in element:
            parentTable = element.replace('Sub', '')
            Db.cursor.execute(f"SELECT {parentTable}Id FROM {element} "
                              f"WHERE {element.lower()}Name = '{filters[element]}'")
            sqlCall = sqlCall + f" AND {parentTable}Id=" + Db.cursor.fetchone()[0]
        Db.cursor.execute(sqlCall)
        subset = list(itertools.chain(*Db.cursor.fetchall()))
    # get the value at the modifier position if there is one, or choose a random one otherwise
    modifier = check_modifier(modifier, subset)
    choice = subset[modifier]

    # gets the data the current core filter provides
    # subrace is treat the same as race as no race with subraces has a choice outside the subrace
    oldData = dict()
    if element in ["Race", "Subrace"]:
        oldData = character.race.get_data()
    elif element == "Subclass":
        unmodifiedData = character.chrClass.subclassItems
        oldData["language"] = unmodifiedData.get("languages", [])
        oldData["proficiency"] = unmodifiedData.get("proficiencies", [])
        oldData["spell"] = unmodifiedData.get("spells", [])
    elif element == "Class":
        oldData.update({"language": character.chrClass.languages, "proficiency": character.chrClass.proficiencies,
                        "spell": character.chrClass.magic.knownSpells + character.chrClass.magic.preparedSpellOptions})

    if "Sub" in element:
        subId = "IS NULL"
    else:
        subId = "= " + Db.get_id(choice, element)

    newData = dict()
    Db.cursor.execute(f"SELECT {element.lower()}OptionsId, amntToChoose FROM {element}Options "
                      f"WHERE {element.lower()}Id={Db.get_id(choice, element)} AND sub{element.lower()}Id {subId}")
    results = Db.cursor.fetchall()
    for (opId, amnt) in results:
        for elem in ["language", "proficiency", "spell"]:
            # find any data linked to the RaceOptions/ClassOptions
            Db.cursor.execute(f"SELECT {elem}Name FROM {elem.capitalize()} WHERE {elem}Id IN ("
                              f"SELECT {elem}Id FROM {element}{elem.capitalize()} "
                              f"WHERE {element.lower()}OptionsId={opId})")
            items = list(set(itertools.chain(*Db.cursor.fetchall())))
            # if this is the data the results are for, add all items if there's no choice, or all items that the old
            # one had if there is - all extra choices will be made during construction
            if len(items) > 0:
                if elem == "proficiency":
                    elem = "proficiencies"
                else:
                    elem = elem + "s"

                if len(items) > amnt:
                    chosenItems = [item for item in items if item in oldData[elem]]
                    if len(chosenItems) > amnt:
                        chosenItems = chosenItems[:amnt]
                    newData.setdefault(elem, []).extend(chosenItems)
                else:
                    newData.setdefault(elem, []).extend(items)
                break

    # updates every data piece in the filters to match
    for elem in ["language", "proficiency", "spell"]:
        filters[elem.capitalize()] = [x for x in filters[elem.capitalize()] if x not in oldData[elem]] \
                                     + newData[elem]
    filters[element] = choice

    return filters


def change_spell_filter(character, filters, modifier):
    """
    Modifies one spell in the filters, and anything else required to achieve this.
    :param character: the character that is being adjusted
    :type character: class: `CharacterElements.Character`
    :param filters: the dictionary of filters used to make a full character
    :type filters: dict
    :param modifier: the modifier number produced, used to help randomise adjustment
    :type modifier: int
    :return: newly modified filters
    """
    # if the character currently has spells from more than just race
    currentSpells = filters["Spells"]
    if character.magic is not None:
        spells = tuple("'" + s.name.replace("'", "''") + "'" for s in character.magic.knownSpells)
        spells = spells.__str__().replace('"', '')

        # changes only cantrips
        if character.magic.areSpellsPrepared:
            Db.cursor.execute(f"SELECT spellName FROM Spell WHERE spellLevel=0 AND "
                              f"spellName NOT IN {spells} AND spellId IN ("
                              f"SELECT spellId FROM ClassSpell WHERE magicId IN ("
                              f"SELECT magicId FROM Magic WHERE classId = "
                              f"{Db.get_id(character.chrClass.name, 'Class')}))")
        # changes anything
        else:
            Db.cursor.execute(f"SELECT spellName FROM Spell WHERE spellName NOT IN {spells} AND spellId IN ("
                              f"SELECT spellId FROM ClassSpell WHERE magicId IN ("
                              f"SELECT magicId FROM Magic WHERE classId = "
                              f"{Db.get_id(character.chrClass.name, 'Class')}))")

        spells = list(set(itertools.chain(*Db.cursor.fetchall())))
        modifier = check_modifier(modifier, spells)
        currentSpells[np.random.randint(0, len(character.magic.knownSpells))] = spells[modifier]
        filters["Spells"] = currentSpells

    # if they only have spells from race
    elif len(character.race.spells) > 0:
        if modifier//5 == 0:
            # change to any race other than the current - this will change the spells by either swapping or removing
            filters = change_core_filter(filters, "Race", modifier, character)
        else:
            # change to any class other than the current that has some amount of spells
            Db.cursor.execute("SELECT className FROM Class WHERE classId IN ("
                              "SELECT classId FROM Magic WHERE (cantripsKnown > 0 OR amntKnown > 0))")
            classes = list(set(itertools.chain(*Db.cursor.fetchall())))
            classes.remove(character.chrClass.className)
            filters = change_core_filter(filters, "Class", modifier, character, classes)

    # if they have no spells
    else:
        if modifier//5 == 0:
            # change race to one with spells
            Db.cursor.execute("SELECT raceName FROM Race WHERE raceId IN ("
                              "SELECT raceId FROM RaceOptions WHERE raceOptionsId IN ("
                              "SELECT raceOptionsId FROM RaceSpell))")
            races = list(set(itertools.chain(*Db.cursor.fetchall())))
            races.remove(character.race.raceName)
            filters = change_core_filter(filters, "Race", modifier, character, races)
        else:
            # change class to one with spells
            Db.cursor.execute("SELECT className FROM Class WHERE classId IN ("
                              "SELECT classId FROM Magic WHERE (cantripsKnown > 0 OR amntKnown > 0))")
            classes = list(set(itertools.chain(*Db.cursor.fetchall())))
            classes.remove(character.chrClass.className)
            filters = change_core_filter(filters, "Class", modifier, character, classes)

    return filters


def change_equipment_filter(current_equip, filters, modifier):
    """
    Modifies one piece of equipment to another piece available for the given class.
    :param current_equip: a list of the names of the current equipment the character owns
    :type current_equip: list
    :param filters: the dictionary of filters used to make a full character
    :type filters: dict
    :param modifier: the modifier number produced, used to help randomise adjustment
    :type modifier: int
    :return: newly modified filters
    """
    Db.cursor.execute("SELECT equipOptionId, suboption FROM EquipmentOption WHERE hasChoice = 1 AND classId="
                      + Db.get_id(filters["Class"], "Class"))
    for (nextId, suboption) in Db.cursor.fetchall():
        if suboption is not None:
            nextId = suboption
        Db.cursor.execute(f"SELECT equipmentName FROM Equipment WHERE equipmentId IN ("
                          f"SELECT equipmentId FROM EquipmentIndivOption WHERE equipmentOptionId = {nextId})")
        results = list(set(itertools.chain(*Db.cursor.fetchall())))
        swap = None
        for result in results:
            if result in current_equip:
                swap = result
                break
        if swap is not None:
            index = filters["Equipment"].index(swap)
            results.remove(swap)
            modifier = check_modifier(modifier, results)
            filters["Equipment"][index] = results[modifier]
            break
    return filters


def change_basic_filter(character, filters, modifier, element, table_name):
    """
    Modifies one basic filter in the filters, and anything else required to achieve this. A basic filter may be a
    language, a proficiency or a skill.
    :param character: the character that is being adjusted
    :type character: class: `CharacterElements.Character`
    :param filters: the dictionary of filters used to make a full character
    :type filters: dict
    :param modifier: the modifier number produced, used to help randomise adjustment
    :type modifier: int
    :param element: the type of basic filter it is, stating Languages, Proficiencies or Skills
    :type element: str
    :param table_name: the database table name for the element
    :type table_name: str
    :return: newly modified filters
    """
    background = character.background.name
    skillsList = list(itertools.chain(*Character.character_skills))

    # gets a collection of the current items of the element's type that the background provides
    if element == "Languages":
        backgroundItems = character.background.languages
    elif element == "Skills":
        backgroundItems = []  # no background gives a choice of skills
    else:
        backgroundItems = [prof for prof in character.background.proficiencies
                           if prof not in skillsList]

    # if the background provides the correct type of basic filter
    if len(backgroundItems) > 0:
        Db.cursor.execute(f"SELECT {table_name.lower()}Name FROM {table_name} WHERE {table_name.lower()}Id IN ("
                          f"SELECT {table_name.lower()}Id FROM Background{table_name} WHERE backgroundId="
                          f"{Db.get_id(background, 'Background')})")
        results = list(set(itertools.chain(*Db.cursor.fetchall())))
        # adjusts results appropriately
        if element == "Languages":
            results = [lang for lang in results if lang not in character.languages]
        else:
            results = [prof for prof in results if ((prof not in skillsList) and (prof not in character.proficiencies))]

        # if it can make the successful filter change, it does. Otherwise, it continues to the code below
        if len(results) > 0:
            replacedItem = backgroundItems[np.random.randint(0, len(backgroundItems))]
            modifier = check_modifier(modifier, results)
            filters[element].replace(replacedItem, results[modifier])
            return filters

    # if the current background cannot perform the change

    if element == "Proficiencies":
        elementAmnt = "toolAmnt"
    else:
        elementAmnt = element[:-1].lower() + "Amnt"
    Db.cursor.execute(f"SELECT backgroundName FROM Background WHERE {elementAmnt} > 0")
    options = list(set(itertools.chain(*Db.cursor.fetchall())))
    options.remove(background)
    modifier = check_modifier(modifier, options)
    newBackground = options[modifier]

    return change_background_filter(filters, newBackground, character)


def change_background_filter(filters, character, modifier):
    """
    Modifies the background filter and all filters affecting it, trying to keep them as close to the original
    as possible.
    :param filters: the dictionary of filters used to make a full character
    :type filters: dict
    :param character: the character that is being adjusted
    :type character: class: `CharacterElements.Character`
    :param modifier: the modifier number produced, used to help randomise adjustment
    :type modifier: int
    :return: newly modified filters
    """
    Db.cursor.execute(f"SELECT backgroundName FROM Background WHERE backgroundName != {filters['Background']}")
    options = list(itertools.chain(*Db.cursor.fetchall()))
    modifier = check_modifier(modifier, options)
    new_background = options[modifier]

    # gets everything the background offers
    Db.cursor.execute(f"SELECT proficiencyName FROM Proficiency WHERE proficiencyType = 'Skill' AND proficiencyId IN ("
                      f"SELECT proficiencyId FROM BackgroundProficiency WHERE "
                      f"backgroundId = {Db.get_id(new_background, 'Background')})")
    skills = list(itertools.chain(*Db.cursor.fetchall()))
    Db.cursor.execute(f"SELECT proficiencyName FROM Proficiency WHERE proficiencyType = 'Tool' AND proficiencyId IN ("
                      f"SELECT proficiencyId FROM BackgroundProficiency WHERE "
                      f"backgroundId = {Db.get_id(new_background, 'Background')})")
    tools = list(itertools.chain(*Db.cursor.fetchall()))
    Db.cursor.execute(f"SELECT languageName FROM Language WHERE languageId IN ("
                      f"SELECT languageId FROM BackgroundLanguage WHERE "
                      f"backgroundId = {Db.get_id(new_background, 'Background')})")
    langs = list(itertools.chain(*Db.cursor.fetchall()))
    Db.cursor.execute(f"SELECT skillAmnt, languageAmnt, toolAmnt FROM Background "
                      f"WHERE backgroundId={Db.get_id(new_background, 'Background')}")
    skillAmnt, langAmnt, toolAmnt = Db.cursor.fetchone()

    # gets all items both the old and new background had, then adds random ones until the background is full
    results = []
    currentItems = set(character.background.proficiencies + character.background.languages)
    for (elems, amnt) in [(skills, skillAmnt), (tools, toolAmnt), (langs, langAmnt)]:
        currentResults = [x for x in elems if x in currentItems]
        if len(currentResults) > amnt:
            currentResults = currentResults[:amnt]
        results.append(currentResults)

    # updates the filters to match
    filters["Background"] = new_background
    for (nextElem, items) in [("Skills", results[0]), ("Proficiencies", results[1]), ("Languages", results[2])]:
        filters[nextElem] = [x for x in filters[nextElem] if x not in currentItems] + items

    return filters


def check_modifier(modifier, results):
    """
    Checks whether the modifier is within range of the results array, and changes it if not.
    :param modifier: the current modifier
    :type modifier: int
    :param results: the results that a check produced
    :type results: list
    :return: the new modifier value
    """
    if len(results) <= modifier:
        modifier = np.random.randint(0, len(results))
    return modifier


def begin():
    result = take_choices([["Acrobatics", "Proficiency", ["Background", "ClassOptions"]],
                          ["Survival", "Proficiency", ["Background", "ClassOptions", "RaceOptions"]],
                          ["Dwarvish", "Language", ["Background", "ClassOptions", "RaceOptions"]],
                          ["Guidance", "Spell", ["Race", "Class"]]])
    character = DataConverter.create_character(1, result)
    print(character)

