import CharacterElements.Race
import CharacterElements.Class
import CharacterElements.Spell
from CharacterElements import Equipment


class Character:
    """A class representing a built character."""

    # a 2D array, storing all skills within their relative ability scores
    skills = [["Athletics"],                                                            # strength
              ["Acrobatics", "Sleight of Hand", "Stealth"],                             # dexterity
              [],                                                                       # constitution(for iteration)
              ["Arcana", "History", "Investigation", "Nature", "Religion"],             # intelligence
              ["Animal Handling", "Insight", "Medicine", "Perception", "Survival"],     # wisdom
              ["Deception", "Intimidation", "Performance", "Persuasion"]]               # charisma
    # an array storing all the abilities' shortened names
    abilities = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]


    def __init__(self, race, chr_class, background, ability_scores):
        """
        Stores up the key elements of the character.
        :param race: The characters race, stored as a Race object.
        :type race: class: `CharacterElements.Race`
        :param chr_class: The characters class, stored as a Class object.
        :type chr_class: class: `CharacterElements.Class`
        :param background: The characters background, stored as a Background object.
        :type background: Background
        :param ability_scores: The ability scores of the character.
        :type ability_scores: dict
        """
        self.race = race
        self.chrClass = chr_class
        self.background = background

        self.abilityScores = self.setupAbilityScores(ability_scores)
        self.languages = race.languages + chr_class.languages + background.languages
        self.proficiencies = self.setupProficiencies()

    def setupAbilityScores(self, ability_scores):
        """
        Adds the racial ability score increases to the inputted ability scores.
        :param ability_scores: each ability score, linked as a key to it's current value.
        :return: a set of complete ability scores for a character
        """
        raceAbilities = self.race.abilityScores.keys()
        for ability in ability_scores.keys():
            if ability in raceAbilities:
                ability_scores[ability] = ability_scores[ability] + self.race.abilityScores[ability]
        return ability_scores

    def setupProficiencies(self):
        """
        For every proficiency gained from any source, sort it into one of four categories:
        armor, weapons, tools, saving throws. Connect these categories and proficiencies with a dictionary of arrays.
        :return: a dictionary, connecting a key for each category with an array of all applicable proficiencies.
        """
        armor, weapons, tools, saving_throws = [], [], [], []
        for proficiency in (self.race.proficiencies + self.chrClass.proficiencies + self.background.proficiencies):
            if proficiency in Character.abilities:
                saving_throws.append(proficiency)
            elif "armor" in proficiency or proficiency.lower() == "shield":
                armor.append(proficiency)
            elif proficiency in Equipment.get_tag_group("Martial Weapon") + Equipment.get_tag_group("Simple Weapon"):
                weapons.append(proficiency)
            else:
                tools.append(proficiency)

        return {"Armor": armor, "Weapons": weapons, "Tools": tools, "Saving throws": saving_throws}



class Background:
    """A class representing a character's background."""
    def __init__(self, name, proficiencies, languages):
        """
        Sets up the core data the background contains.
        :param name: The name of the background
        :type name: str
        :param proficiencies: The proficiencies this background provides.
        :type proficiencies: list
        :param languages: The languages this background provides.
        :type languages: list
        """
        self.name = name
        self.proficiencies = proficiencies
        self.languages = languages

    def __str__(self):
        output = f"The background is {self.name}:\n" \
                 f"It gives the proficiencies: {', '.join(self.proficiencies)}\n"
        if len(self.languages) > 0:
            output += f"It gives the languages: {', '.join(self.languages)}"
        return output

