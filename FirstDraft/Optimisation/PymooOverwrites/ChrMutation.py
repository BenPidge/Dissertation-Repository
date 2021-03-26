from pymoo.model.mutation import Mutation


class ChrMutation(Mutation):
    """Mutates a character chromosome, with the potential to leave it unchanged."""

    def _do(self, problem, x, **kwargs):
        return

