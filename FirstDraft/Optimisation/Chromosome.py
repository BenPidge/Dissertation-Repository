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
        self.tags = tags
        self.magicWeight = magic_weight
        self.healthWeight = health_weight

        # tagsFitness is a 2D array with nested array layouts of [tag, tags' weighting, tags' individual fitness]
        self.tagsFitness = []
        for (tag, weight) in self.tags:
            self.tagsFitness.append([tag, weight, 0])

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
        index = int(list(itertools.chain(*self.tagsFitness)).index(tag) / 3)
        self.tagsFitness[index][2] += addition * self.tagsFitness[index][1]

    def extract_tags(self):
        """
        Extracts the needed information from each tag.
        """
        self.ability_scores_tag()
        for (tag, weight) in self.tags:
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
        fitness += self.get_proficiencies(tagId)

        return fitness

    def get_proficiencies(self, tag_id):
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

    def ability_scores_tag(self):
        """
        Converts the current ability scores into one weighted integer, if they're related to tag.
        """
        potentialTags = ["strong", "dexterous", "health", "wise", "knowledgeable", "charismatic"]
        # for every archetype-owned tag within potentialTags, ignoring casing
        for tag in list(set([x.lower() for x in potentialTags]) & set([x.lower() for x in self.tags])):
            value = self.character.abilityScores.items()[potentialTags.index(tag)]
            self.update_indiv_tag_fitness(tag, value)
