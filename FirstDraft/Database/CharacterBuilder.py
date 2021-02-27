import itertools
from Database import CoreDatabase as Db
from collections import Counter


def takeChoices(choices):
    """
    Takes a 3D array of decided choices and where each can be from, and calculates options.
    :param choices: a 3D array, in the layout [[choice, choiceType, [where from]]
    :type choices: list
    """
    allOptions = dict()
    optionCount = []
    for [choice, choiceType, placesFrom] in choices:
        nextResult = extractChoice(choice, choiceType, placesFrom)
        allOptions.update(nextResult)
        optionCount += itertools.chain(*nextResult.values())
    optionCount = Counter(optionCount)

    result = optionCombos(allOptions, optionCount)
    if len(result) == 0:
        print("You've asked for impossible requirements")
    else:
        print(result)


def extractChoice(choice, choice_loc, places_from):
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

        call = f"SELECT {basePlace}Id FROM {place}{choice_loc} WHERE {choiceLocLower}Id IN (" \
               f"SELECT {choiceLocLower}Id FROM {choice_loc} WHERE {choiceLocLower}Name='{choice}'))"

        if "Options" in basePlace:
            call = f"SELECT {place.lower()}Name FROM {place} WHERE {place.lower()}Id IN (" \
                   f"SELECT {place.lower()}Id FROM {basePlace.capitalize()} WHERE {basePlace}Id IN (" + call + ")"
        elif choice_loc == "Equipment":
            call = f"SELECT {place.lower()}Name FROM {place} WHERE {place.lower()}Id IN (" \
                   f"SELECT {place.lower()}Id FROM EquipmentOption WHERE equipOptionId IN (" \
                   f"SELECT equipmentOptionId FROM EquipmentIndivOption WHERE equipmentId=(" \
                   f"SELECT equipmentId FROM Equipment WHERE equipmentName='{choice}')))"
        else:
            call = f"SELECT {place.lower()}Name FROM {place} WHERE {place.lower()}Id IN (" + call

        Db.cursor.execute(call)
        for result in itertools.chain(*Db.cursor.fetchall()):
            options.append(place + ": " + result)
    return {choice: options}


def optionCombos(options, option_counter):
    """
    Takes in the current options and finds a combination to achieve all of them.
    :param options: a dictionary that links the choice with it's options
    :type options: dict
    :param option_counter: a dictionary saying how many occurrences each option has throughout.
    :type option_counter: dict
    :return: a dictionary of the choices made for the character, linking the class/race/etc choice to an array of the
             options it fulfills
    """
    unmetChoices = set()
    for key in option_counter.keys():
        unmetChoices.add(key.split(":")[0])
    choicesMade = dict()
    # for each array of options linked to one choice
    for nextKey, nextValues in options.items():
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
    return choicesMade


def begin():
    takeChoices([["Acrobatics", "Proficiency", ["Background", "ClassOptions"]],
                 ["Athletics", "Proficiency", ["Background", "ClassOptions", "RaceOptions"]],
                 ["Dwarvish", "Language", ["Background", "ClassOptions", "RaceOptions"]],
                 ["Warhammer", "Equipment", ["Background", "Class"]]])

