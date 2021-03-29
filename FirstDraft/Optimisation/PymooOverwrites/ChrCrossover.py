import numpy as np
from pymoo.model.crossover import Crossover


class ChrCrossover(Crossover):
    """Combines the parent chromosomes to create new offspring."""

    def __init__(self):
        # 2 parents will produce 2 offspring
        super().__init__(2, 2)

    def _do(self, problem, x, **kwargs):
        """
        Takes parent chromosomes in order to produce offspring.
        :param problem: the problem the algorithm is trying to optimise
        :type problem: class: `Optimisation.ChrProblem`
        :param x: a list of the chromosomes to crossover
        :type x: class: `Pymoo.Model.Population`
        :param kwargs: arguments connected to their arg number
        :type kwargs: dict
        :return: the list of offspring
        """
        parents_num, matings_num, vars_num = x.shape
        output = np.full_like(x, None, dtype=np.object_)

        for cross in range(matings_num):
            # get parents and setup offspring list
            parents = []
            offspring = []
            for i in range(parents_num):
                parents.append(x[i, cross, 0])

            offspring.append(self.breed(parents))

            # empty offspring list into the output
            for i in range(len(offspring)):
                output[i, cross, 0] = offspring[i]
        return output

    def breed(self, parents):
        # randomly allocate the class, race and background from one parent
        # make adjustable for over 2 parents, jic
        # consider a case where parents have one of those in common - look into breeding between the suboptions of it
        return

