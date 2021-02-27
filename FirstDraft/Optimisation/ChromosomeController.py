from Optimisation.Chromosome import Chromosome


class ChromosomeController:

    currentGen = []
    nondominatedFront = []

    def build_chromosome(self, character, tags, magic_weight, health_weight):
        """
        Builds a chromosome and adds it to the list of current chromosomes.
        :param character: the character the chromosome holds
        :type character: class: `Character.Character`
        :param tags: the tags that the character aim to optimally fit
        :type tags: list
        :param magic_weight: the weighting of magic for the character requirements
        :type magic_weight: float
        :param health_weight: the weighting of health for the character requirements
        :type health_weight: float
        """
        self.currentGen.append(Chromosome(character, tags, magic_weight, health_weight))

