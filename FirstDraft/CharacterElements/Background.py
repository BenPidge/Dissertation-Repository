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

    def __eq__(self, other):
        """
        Compares the background object with another background.
        :param other: the other background object to compare against
        :type other: Background
        :return: a boolean stating whether they're equal
        """
        return self.name == other.name and sorted(self.proficiencies) == sorted(other.proficiencies) \
                and sorted(self.languages) == sorted(other.languages)

    def __str__(self):
        """
        Converts the object to a string of it's content.
        :return: the objects relevant content, in a printable layout
        """
        output = f"The background is {self.name}:\n" \
                 f"It gives the proficiencies: {', '.join(self.proficiencies)}\n"
        if len(self.languages) > 0:
            output += f"It gives the languages: {', '.join(self.languages)}"
        return output

