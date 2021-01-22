
class Class:
    """A python class representing a character's class."""
    def __init__(self, name, traits, proficiencies, equipment, main_ability, second_ability, hit_dice,
                 languages, level, magic=None, subclass=None):
        """

        :param name: The name of the class
        :type name: str
        :param traits: The text-based traits the class grants.
        :type traits: list
        :param proficiencies: The proficiencies gained from the class.
        :type proficiencies: list
        :param equipment: The equipment selected from the class-specific options.
        :type equipment: list
        :param main_ability: The main ability score used by the class.
        :type main_ability: str
        :param second_ability: The second most used ability score by the class.
        :type second_ability: str
        :param hit_dice: The hit dice the class gains at every level, and therefore it's health increase per level.
        :type hit_dice: int
        :param magic: A ClassMagic object representing all spell-related elements of the class.
        :type magic: ClassMagic, optional
        :param languages: The languages gained from the class.
        :type languages: list, optional
        :param level: The amount of levels the character currently has in this class.
        :type level: int, optional
        :param subclass: A Class object representing the subclass of the current class.
        :type subclass: Class, optional
        """
        if languages is None:
            languages = []
        self.name = name
        self.traits = traits
        self.proficiencies = proficiencies
        self.equipment = equipment
        self.mainAbility = main_ability
        self.secondAbility = second_ability
        self.hitDice = hit_dice
        self.magic = magic
        self.languages = languages
        self.level = level

        if subclass is not None:
            self.extract_subclass(subclass)

    def extract_subclass(self, subclass):
        """
        Extract and apply all subclass data to the class.
        :param subclass: The subclass of the current class selected.
        """
        subclassDict = subclass.get_data()
        for key in subclassDict.keys():
            attributeVal = getattr(self, key)
            # if its an array, merge the arrays
            if key in ["languages", "proficiencies", "traits",  "equipment"]:
                setattr(self, key, attributeVal + subclassDict[key])
            # if it's single value, update the attribute value
            else:
                setattr(self, key, subclassDict[key])

        if subclass.magic is not None:
            self.magic = subclass.magic

    def get_data(self):
        """
        Combines all non-null data into a dictionary for easy extraction.
        :return: a dictionary of all non-null class data.
        """
        dataDict = {
            "name": self.name,
            "languages": self.languages,
            "proficiencies": self.proficiencies,
            "traits": self.traits,
            "equipment": self.equipment,
            "secondAbility": self.secondAbility
        }

        # remove null data
        for key in dataDict.keys():
            if dataDict[key] is None:
                del dataDict[key]

        return dataDict



class ClassMagic:
    """A class representing all details of magic that a character class might require."""
    def __init__(self, spell_slot, are_spells_prepared, spell_amount=-1, known_spells=None,
                 prepared_spell_calculation=None, prepared_spell_options=None):
        """
        Stores all the core information on a classes magic.
        :param spell_slot: The spell slot level, linked to the amount of these spell slots available at the class level.
        :type spell_slot: dict
        :param are_spells_prepared: Stating whether spells are prepared or selected at levels/
        :type are_spells_prepared: bool
        :param spell_amount: The amount of spells that the class should have at any one time, or -1 to show more info is
                             required to calculate this.
        :type spell_amount: int, optional
        :param known_spells: Spells that are always known at any one time.
        :type known_spells: list, optional
        :param prepared_spell_calculation: States how the spells are prepared
        :type prepared_spell_calculation: str, optional
        :param prepared_spell_options: Spells that can be prepared and unprepared during long rests.
        :type prepared_spell_options: list, optional
        """
        self.spellAmount = spell_amount
        self.spellSlot = spell_slot
        self.knownSpells = known_spells
        self.areSpellsPrepared = are_spells_prepared
        self.preparedSpellCalculation = prepared_spell_calculation
        self.preparedSpellOptions = prepared_spell_options

        if known_spells is None:
            self.knownSpells = []
        if prepared_spell_options is None:
            self.preparedSpellOptions = []


    def __str__(self):
        string = f"They have "
        for (level, amnt) in self.spellSlot.items():
            if level < 4:
                multiple = ["st", "nd", "rd"]
                multiple = multiple[level-1]
            else:
                multiple = "th"
            string += f"{str(amnt)} {str(level)}{multiple}-Level spellslots, "
        string = string[:-2] + "\n"

        string += "They know the cantrips: "
        for x in range(0, len(self.knownSpells)):
            if self.knownSpells[x].level == 0:
                string += self.knownSpells[x].name + ", "
        string = string[:-2] + ".\n"

        string += "They know the spells: "
        for x in range(0, len(self.knownSpells)):
            if self.knownSpells[x].level > 0:
                string += self.knownSpells[x].name + ", "
        string = string[:-2] + ".\n"

        if self.preparedSpellCalculation is not None:
            if self.spellAmount > -1:
                string += f"They know {self.spellAmount} spells.\n"
            else:
                string += "They known spells equal to " + self.preparedSpellCalculation + ".\n"
            string += "They can prepare the spells: "
            for x in range(0, len(self.preparedSpellOptions)):
                string += self.preparedSpellOptions[x].name + ", "
            string = string[:-2] + "."
        return string

