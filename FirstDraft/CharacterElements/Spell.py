class Spell:
    """A class used to represent a singular spell."""

    def __init__(self, name, level, casting_time, duration, spell_range, components, school, tags, description,
                 damage=None, attack=None, save=None, area=None, chr_level=1):
        """
        Initialises the spell with all required information.
        :param name: The spells name.
        :type name: str
        :param level: The spells level, with 0 for cantrips.
        :type level: int
        :param casting_time: The spells casting time, including any ritual information.
        :type casting_time: str
        :param duration: The spells duration and if it requires concentration.
        :type duration: str
        :param spell_range: The range of the spell, in feet.
        :type spell_range: int
        :param components: The component tags the spell requires, and any non-foci materials.
        :type components: str
        :param school: The school of magic the spell is within.
        :type school: str
        :param tags: The tags applied to the spell, which help identify it's purpose.
        :type tags: list
        :param description: The description of the spell in its entirety.
        :type description: str
        :param damage: The damage it deals, typically represented as (num of dice)d(sides of dice), and the damage type.
        :type damage: str, optional
        :param attack: The attack type of the spell, such as melee or ranged.
        :type attack: str, optional
        :param save: The saving throw required against the spell.
        :type save: str, optional
        :param area: The area the spell covers in feet, and the shape of this area.
        :type area: str, optional
        :param chr_level: The level of the character, used for cantrip damages.
        :type chr_level: int, optional
        """

        self.name = name
        self.level = level
        self.castingTime = casting_time
        self.duration = duration
        self.range = spell_range
        self.description = description
        self.area = area
        self.components = components
        self.school = school
        self.tags = tags
        self.damage = damage
        self.attack = attack
        self.save = save
        self.__chrLevel = chr_level

        self.cantrip_damage()

    def update_chr_level(self, new_level):
        """
        Updates the characters level, and adjusts accordingly.
        :param new_level: the new level of the character
        :type new_level: int
        """
        self.__chrLevel = new_level
        self.cantrip_damage()

    def cantrip_damage(self):
        """Calculates the damage the spell does, providing it's a cantrip, based on the character level."""
        if self.level == 0:
            if self.__chrLevel < 5:
                damage = 1
            elif 5 <= self.__chrLevel < 11:
                damage = 2
            elif 11 <= self.__chrLevel < 17:
                damage = 3
            else:
                damage = 4
            self.damage = str(damage) + self.damage[1:]

    def to_string(self):
        """
        Returns the data of the spells as a string
        :return: a string stating the spell data
        """
        details = "{} - Level {} {} spell.\n" \
                  "{} \n\n" \
                  "It has a duration of {} and a casting time of {}, with a range of {}.\n" \
                  "It requires the components {} and has the tags: {}\n".format(self.name, self.level, self.school,
                                                                                self.description, self.duration,
                                                                                self.castingTime, self.range,
                                                                                self.components, self.tags)
        if self.area is not None:
            details += "It has an area of {}.".format(self.area)
        if self.damage is not None:
            if self.attack is not None:
                details += "It is a {} attack. ".format(self.attack)
            if self.save is not None:
                details += "It required a {} spell save. ".format(self.save)
            details += "It deals {} damage.\n".format(self.damage)
        return details
