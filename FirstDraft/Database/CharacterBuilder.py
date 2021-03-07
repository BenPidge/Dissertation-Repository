import itertools
from collections import Counter

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


def begin():
    result = take_choices([["Acrobatics", "Proficiency", ["Background", "ClassOptions"]],
                          ["Survival", "Proficiency", ["Background", "ClassOptions", "RaceOptions"]],
                          ["Dwarvish", "Language", ["Background", "ClassOptions", "RaceOptions"]],
                          ["Guidance", "Spell", ["Race", "Class"]]])
    chr = DataConverter.create_character(1, result)
    print(chr)

