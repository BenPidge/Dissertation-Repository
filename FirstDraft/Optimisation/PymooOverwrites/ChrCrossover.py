from pymoo.model.crossover import Crossover


class ChrCrossover(Crossover):
    """Combines the parent chromosomes to create new offspring."""

    def __init__(self):
        # 2 parents will produce 2 offspring
        super().__init__(2, 2)

    def _do(self, problem, x, **kwargs):
        return

