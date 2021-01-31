import itertools

from CharacterElements import Character
from Database import CoreDatabase as Db


class Chromosome:
    """A singular potential solution for the optimisation problem."""

    fitness = 0
    nondominatedFront = 0

    def __init__(self, character, tags, magic_weight, health_weight):
        """
        Initialises the chromosome with a provided character object and tags.
        :param character: the character the chromosome will represent
        :type character: Character.Character
        :param tags: the tags that it's sorting will judge it off, in a [tag, weight] layout
        :type tags: list
        """
        self.character = character
        self.health = [health_weight, (character.chrClass.hitDice - 6)/2]
        self.magic = [magic_weight, self.spellslots_value()]

        # tags is a 2D array with nested array layouts of [tag, tags' weighting, tags' unweighted individual fitness]
        self.tags = []
        for (tag, weight) in tags:
            self.tags.append([tag, weight, 0])

        self.extract_tags()

    def update_indiv_tag_fitness(self, tag, addition):
        """
        Updates the fitness value of a given tag.
        :param tag: the tag to update the fitness of
        :type tag: str
        :param addition: the amount to increase the tag fitness by
        :type addition: int
        """
        # flatten tagsFitness to get the tags' array index from the name
        index = int(list(itertools.chain(*self.tags)).index(tag) / 3)
        self.tags[index][2] += addition

    def extract_tags(self):
        """
        Extracts the needed information from each tag.
        """
        self.ability_scores_tag()
        for (tag, weight, fitness) in self.tags:
            self.update_indiv_tag_fitness(tag, self.get_tag_fitness(tag))

    def get_tag_fitness(self, tag):
        """
        Gets the unweighted fitness value of a tag relative to it's character.
        :param tag: the tag applying to the character
        :type tag: str
        :return: the integer weight
        """
        fitness = 0
        tagId = Db.get_id(tag, "Tag")
        fitness += self.proficiencies_total(tagId)

        return fitness

    def proficiencies_total(self, tag_id):
        """
        Counts how many proficiencies the character has that are appropriate to the given tag.
        :param tag_id: the id of the given tag to use for comparisons
        :type tag_id: int
        :return: the integer value of how many proficiencies are relevant
        """
        values = 0
        Db.cursor.execute("SELECT proficiencyId FROM TagProficiency WHERE tagId=" + str(tag_id))
        for pId in Db.cursor.fetchall():
            Db.cursor.execute("SELECT proficiencyName FROM Proficiency WHERE proficiencyId=" + str(pId[0]))
            prof = Db.cursor.fetchone()[0]
            if prof in self.character.proficiencies:
                values += self.character.get_skill_value(prof)

        return values

    def spellslots_value(self):
        """
        Calculates the total magic value provided from the spellslots.
        :return: an integer value representing the spellslots' worth
        """
        value = 0
        for lvl, amnt in self.character.magic.spellSlot.items():
            value += lvl * amnt
        return value

    def ability_scores_tag(self):
        """
        Converts the current ability scores into one weighted integer, if they're related to tag.
        """
        # while it'll never be part of the intersect, health is kept in for tags-to-ability-score index consistency
        potentialTags = ["strong", "dexterous", "health", "wise", "knowledgeable", "charismatic"]
        # for every archetype-owned tag within potentialTags, ignoring casing
        for tag in list(set([x[0].lower() for x in potentialTags]) & set([x[0].lower() for x in self.tags])):
            value = self.character.abilityScores.items()[potentialTags.index(tag)]
            self.update_indiv_tag_fitness(tag, value)
