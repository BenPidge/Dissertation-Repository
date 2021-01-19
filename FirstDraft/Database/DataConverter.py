from Database import DataExtractor, CoreDatabase as Db
from CharacterElements import Character, Class, Equipment, Race, Spell



def makeChoice(num_of_choices, choices):
    """
    Lets the user choose a certain amount of items from an array of options.
    :param num_of_choices: how many of the choices must be selected
    :type num_of_choices: int
    :param choices: a list of the choices available
    :type choices: list
    :return: a list of the choices selected
    """
    output = []
    if num_of_choices == len(choices):
        output = choices
    else:
        while len(output) < num_of_choices:
            print("Choose one from: ")
            for x in range(0, len(choices)):
                print(f"{x+1}. {choices[x]}")
            nextAddition = Db.int_input(">") - 1
            if nextAddition < len(choices):
                output.append(choices[nextAddition])
                choices.pop(nextAddition)
    return output




def createBackground(background_name):
    """
    Creates and returns a background object, given the name of the background to use.
    :param background_name: the name of the background selected
    :type background_name: str
    :return: a python object representing the background
    """
    tools, skills, languages = DataExtractor.backgroundConnections(background_name)
    finalProfs, finalLanguages = [], []

    # INSERT CHOICE CALCULATIONS HERE
    finalProfs += makeChoice(tools[0], tools[1])
    finalProfs += makeChoice(skills[0], skills[1])
    finalLanguages = makeChoice(languages[0], languages[1])
    # INSERT CHOICE CALCULATIONS HERE

    return Character.Background(background_name, finalProfs, finalLanguages)


def createClass(class_name):
    """
    Creates and returns a class object, given the name of the class to use.
    :param class_name: the name of the class selected
    :type class_name: str
    :return: a python object representing the class
    """
    classId = Db.get_id(class_name, "Class")
    DataExtractor.classOptionsConnections(classId)
    return
    #(self, name, traits, proficiencies, equipment, main_ability, second_ability, hit_dice,
    #             magic=None, languages=None, level=1, subclass=None)



def begin(self):
    print(self.createBackground("Sage"))

