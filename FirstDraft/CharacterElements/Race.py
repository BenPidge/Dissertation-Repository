
class Race:
    """A class representing a character's race."""

    def __init__(self, name, languages, proficiencies, ability_scores, traits, speed=30, size="Medium",
                 darkvision=False, spells=None, spell_modifier=None, resistance=None, subrace=None):
        """
        Initialise the race with all the necessary information to properly model it.
        :param name: The name of the race.
        :type name: str
        :param languages: The language or languages that the character knows from racial features.
        :type languages: list
        :param proficiencies: The proficiencies that the character knows from racial features.
        :type proficiencies: list
        :param ability_scores: The ability score improvements gained from the race, in an ability-to-value dictionary.
        :type ability_scores: dict
        :param traits: The racial traits gained that don't directly impact other racial data.
        :type traits: list
        :param speed: The walking speed, in feet, of the race.
        :type speed: int, optional
        :param size: The creature size of members of the race.
        :type size: str, optional
        :param darkvision: Whether this race grants darkvision or not.
        :type darkvision: bool, optional
        :param spells: Any spells that can be cast from a racial trait.
        :type spells: list, optional
        :param spell_modifier: The ability score modifier used to cast the racial spells
        :type spell_modifier: str, optional
        :param resistance: The damage type that this race grants resistance to.
        :type resistance: str, optional
        :param subrace: The subrace of this race that was selected.
        :type subrace: Race, optional
        """

        self.name = name
        self.languages = languages
        self.proficiencies = proficiencies
        self.abilityScores = ability_scores
        self.traits = traits
        self.speed = speed
        self.size = size
        self.darkvision = darkvision
        self.spellMod = spell_modifier
        self.resistance = resistance
        if spells is None:
            self.spells = []
        else:
            self.spells = spells

        if subrace is not None:
            self.extract_subrace(subrace)

    def extract_subrace(self, subrace):
        """
        Extract and apply all subrace data to the race.
        :param subrace: The subrace of this race that was selected.
        """
        subraceDict = subrace.get_data()
        for key in subraceDict.keys():
            attributeVal = getattr(self, key)
            # if its an array, merge the arrays
            if key in ["languages", "proficiencies", "traits",  "spells"]:
                setattr(self, key, attributeVal + subraceDict[key])
            # if it's a dictionary, merge the dictionaries
            elif key == "ability scores":
                self.abilityScores = {**self.abilityScores, **subraceDict[key]}
            # if it's single value, update the attribute value
            else:
                setattr(self, key, subraceDict[key])

    def get_data(self):
        """
        Combines all non-null data into a dictionary for easy extraction.
        :return: a dictionary of all non-null racial data.
        """
        dataDict = {
            "name": self.name,
            "languages": self.languages,
            "proficiencies": self.proficiencies,
            "ability scores": self.abilityScores,
            "traits": self.traits,
            "speed": self.speed,
            "size": self.size,
            "darkvision": self.darkvision,
            "resistance": self.resistance,
            "spells": self.spells,
            "spellMod": self.spellMod
        }

        # remove null data
        for key in dataDict.keys():
            if dataDict[key] is None or dataDict[key] is False:
                del dataDict[key]

        return dataDict
